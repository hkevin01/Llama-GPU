#!/usr/bin/env python3
"""Comprehensive system status check and diagnostics for Llama-GPU"""

import asyncio
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, Optional, Tuple

from src.core.logging_config import setup_logging
from src.core.api_client import APIClient
from src.core.debug_manager import DebugManager
from src.core.exceptions import APIUnavailableError

# Constants
PYTORCH_TIMEOUT = 10
API_TIMEOUT = 3
CHECK_ID = f"check-{int(time.time())}"
REPORT_PATH = "logs/diagnostic_report.json"

# Set up logging and debugging
logger = setup_logging(service_name="status-check")
debug_mgr = DebugManager()


def check_pytorch() -> Tuple[Optional[Dict], str]:
    """Check PyTorch installation and configuration.

    Returns:
        Tuple[Optional[Dict], str]: PyTorch info and status message
    """
    debug_mgr.start_request(
        f"{CHECK_ID}-pytorch",
        "pytorch-check",
        {"timeout": PYTORCH_TIMEOUT}
    )

    try:
        cmd = (
            'source venv/bin/activate && python3 -c "'
            'import torch; '
            'print(\'PyTorch: \' + torch.__version__); '
            'print(\'HIP: \' + getattr(torch.version, \'hip\', \'No ROCm\')); '
            'print(\'GPU Available: \' + str(torch.cuda.is_available()))"'
        )
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=PYTORCH_TIMEOUT,
            check=True
        )
        pytorch_info = {}
        for line in result.stdout.strip().split('\n'):
            key, value = line.split(": ", 1)
            pytorch_info[key.lower()] = value

        debug_mgr.end_request(f"{CHECK_ID}-pytorch", "success")
        status_msg = "PyTorch check passed"
        return pytorch_info, status_msg
    except subprocess.CalledProcessError as e:
        msg = f"PyTorch not properly installed: {e.stderr}"
        logger.error(msg)
        debug_mgr.track_error("pytorch-error", msg)
        debug_mgr.end_request(f"{CHECK_ID}-pytorch", "error")
        return None, msg
    except subprocess.TimeoutExpired:
        msg = f"PyTorch check timed out after {PYTORCH_TIMEOUT}s"
        logger.error(msg)
        debug_mgr.track_error("pytorch-timeout", msg)
        debug_mgr.end_request(f"{CHECK_ID}-pytorch", "timeout")
        return None, msg
    except Exception as e:
        msg = f"Unexpected error checking PyTorch: {str(e)}"
        logger.error(msg)
        debug_mgr.track_error("pytorch-error", msg)
        debug_mgr.end_request(f"{CHECK_ID}-pytorch", "error")
        return None, msg


def check_backend() -> Tuple[Optional[Dict], str]:
    """Check ROCm backend status.

    Returns:
        Tuple[Optional[Dict], str]: Backend info and status message
    """
    debug_mgr.start_request(
        f"{CHECK_ID}-backend",
        "backend-check",
        {"timeout": PYTORCH_TIMEOUT}
    )

    try:
        cmd = [
            "python3",
            "-c",
            (
                "from src.utils.amd.rocm_backend import ("
                "HAS_AMD_GPU, HAS_ROCM, rocm_backend); "
                "print('AMD GPU: ' + str(HAS_AMD_GPU)); "
                "print('ROCm Available: ' + str(HAS_ROCM)); "
                "print('Backend Ready: ' + str(rocm_backend.available))"
            )
        ]
        result = subprocess.run(
            ["source", "venv/bin/activate", "&&"] + cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=PYTORCH_TIMEOUT,
            check=True
        )
        backend_info = {}
        for line in result.stdout.strip().split('\n'):
            key, value = line.split(": ", 1)
            backend_info[key.lower()] = value.lower() == "true"

        debug_mgr.end_request(f"{CHECK_ID}-backend", "success")
        status_msg = "Backend check passed"
        return backend_info, status_msg
    except subprocess.CalledProcessError as e:
        msg = f"Backend check failed: {e.stderr}"
        logger.error(msg)
        debug_mgr.track_error("backend-error", msg)
        debug_mgr.end_request(f"{CHECK_ID}-backend", "error")
        return None, msg
    except subprocess.TimeoutExpired:
        msg = f"Backend check timed out after {PYTORCH_TIMEOUT}s"
        logger.error(msg)
        debug_mgr.track_error("backend-timeout", msg)
        debug_mgr.end_request(f"{CHECK_ID}-backend", "timeout")
        return None, msg
    except Exception as e:
        msg = f"Unexpected error in backend check: {str(e)}"
        logger.error(msg)
        debug_mgr.track_error("backend-error", msg)
        debug_mgr.end_request(f"{CHECK_ID}-backend", "error")
        return None, msg


async def check_api_health() -> Tuple[Optional[Dict], str]:
    """Check API service health.

    Returns:
        Tuple[Optional[Dict], str]: API health info and status message
    """
    debug_mgr.start_request(
        f"{CHECK_ID}-api",
        "api-health-check",
        {"timeout": API_TIMEOUT}
    )

    try:
        client = APIClient(timeout=API_TIMEOUT)
        health = await client.health_check()
        await client.close()

        debug_mgr.end_request(f"{CHECK_ID}-api", "success")
        return health, "API health check passed"
    except APIUnavailableError as e:
        msg = f"API service unavailable: {str(e)}"
        logger.error(msg)
        debug_mgr.track_error("api-error", msg)
        debug_mgr.end_request(f"{CHECK_ID}-api", "error")
        return None, msg
    except Exception as e:
        msg = f"API check failed: {str(e)}"
        logger.error(msg)
        debug_mgr.track_error("api-error", msg)
        debug_mgr.end_request(f"{CHECK_ID}-api", "error")
        return None, msg


def get_system_info() -> Dict:
    """Get basic system information.

    Returns:
        Dict: System information
    """
    return {
        "platform": platform.platform(),
        "python_version": sys.version.split()[0],
        "timestamp": datetime.now().isoformat(),
        "user": os.getenv("USER", "unknown"),
        "cpu_count": os.cpu_count(),
        "cwd": os.getcwd()
    }


def save_report(results: Dict) -> None:
    """Save diagnostic results to file.

    Args:
        results: Diagnostic results to save
    """
    with open(REPORT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n📊 Summary:")
    for check, result in results["checks"].items():
        status = "✅" if result["status"] == "pass" else "❌"
        print(f"{status} {check}: {result['message']}")

    if results["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")


async def run_diagnostics() -> Dict:
    """Run comprehensive system diagnostics.

    Returns:
        Dict: Complete diagnostic results
    """
    logger.info("🔍 Starting Llama-GPU System Diagnostics")
    logger.info("=" * 50)

    debug_mgr.start_request(CHECK_ID, "full-diagnostics")
    results = {
        "system_info": get_system_info(),
        "checks": {},
        "metrics": {},
        "recommendations": []
    }

    try:
        # Check project directory and venv
        try:
            os.chdir('/home/kevin/Projects/Llama-GPU')
            logger.info("✅ Project directory: /home/kevin/Projects/Llama-GPU")
            results["checks"]["project_dir"] = {
                "status": "pass",
                "message": "Project directory found"
            }
        except OSError as e:
            msg = f"Could not find project directory: {e}"
            logger.error(msg)
            results["checks"]["project_dir"] = {
                "status": "fail",
                "message": msg
            }
            debug_mgr.track_error("project-dir-error", msg)

        # Check virtual environment
        if os.path.exists('venv'):
            logger.info("✅ Virtual environment exists")
            results["checks"]["venv"] = {
                "status": "pass",
                "message": "Virtual environment found"
            }
        else:
            msg = "Virtual environment missing"
            logger.error(msg)
            results["checks"]["venv"] = {
                "status": "fail",
                "message": msg
            }
            debug_mgr.track_error("venv-error", msg)
            results["recommendations"].append(
                "Create virtual environment: python3 -m venv venv"
            )

        # Check PyTorch
        logger.info("\n📦 Checking Python dependencies...")
        pytorch_info, pytorch_msg = check_pytorch()
        results["checks"]["pytorch"] = {
            "status": "pass" if pytorch_info else "fail",
            "message": pytorch_msg,
            "info": pytorch_info
        }
        if not pytorch_info:
            results["recommendations"].append(
                "Install PyTorch: pip install torch"
            )

        # Check backend
        logger.info("\n🔧 Checking Llama-GPU backends...")
        backend_info, backend_msg = check_backend()
        results["checks"]["backend"] = {
            "status": "pass" if backend_info else "fail",
            "message": backend_msg,
            "info": backend_info
        }
        if not backend_info:
            results["recommendations"].append(
                "Install ROCm backend: ./scripts/setup/complete_amd_setup.sh"
            )

        # Check API health
        logger.info("\n🌐 Checking API service...")
        api_info, api_msg = await check_api_health()
        results["checks"]["api"] = {
            "status": "pass" if api_info else "fail",
            "message": api_msg,
            "info": api_info
        }

        # Get performance metrics
        results["metrics"] = debug_mgr.get_metrics()

        # Save diagnostic report
        os.makedirs("logs", exist_ok=True)
        await asyncio.to_thread(save_report, results)
        logger.info(f"Diagnostic report saved to {REPORT_PATH}")

        # Success
        debug_mgr.end_request(CHECK_ID, "success")
        return results

    except Exception as e:
        msg = f"Diagnostic check failed: {str(e)}"
        logger.error(msg)
        debug_mgr.track_error("diagnostic-error", msg)
        debug_mgr.end_request(CHECK_ID, "error")
        return {
            "error": msg,
            "partial_results": results
        }


if __name__ == "__main__":
    try:
        asyncio.run(run_diagnostics())
    except KeyboardInterrupt:
        print("\nDiagnostic check cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
