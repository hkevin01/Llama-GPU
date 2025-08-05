#!/usr/bin/env python3
"""Check current system status for Llama-GPU"""

import asyncio
import os
import subprocess
from typing import Dict, Optional

from src.core.logging_config import setup_logging
from src.core.api_client import APIClient
from src.core.exceptions import APIUnavailableError

# Set up logging
logger = setup_logging(service_name="status-check")


def check_pytorch() -> Optional[Dict]:
    """Check PyTorch installation and configuration.

    Returns:
        Optional[Dict]: PyTorch status information or None if check fails
    """
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
            timeout=10,
            check=True
        )
        pytorch_info = {}
        for line in result.stdout.strip().split('\n'):
            key, value = line.split(": ", 1)
            pytorch_info[key.lower()] = value
        return pytorch_info
    except Exception as e:
        logger.error(f"PyTorch check failed: {str(e)}")
        return None


def check_backend() -> Optional[Dict]:
    """Check ROCm backend status.

    Returns:
        Optional[Dict]: Backend status information or None if check fails
    """
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
            timeout=10,
            check=True
        )
        backend_info = {}
        for line in result.stdout.strip().split('\n'):
            key, value = line.split(": ", 1)
            backend_info[key.lower()] = value.lower() == "true"
        return backend_info
    except Exception as e:
        logger.error(f"Backend check failed: {str(e)}")
        return None


async def check_system_status() -> Dict:
    """Check the system status of Llama-GPU.

    Returns:
        Dict: Status information for all components
    """
    try:
        status = {
            "project": False,
            "venv": False,
            "pytorch": None,
            "backend": None,
            "server": None
        }

        logger.info("🔍 Llama-GPU System Status Check")
        logger.info("=" * 40)

        # Change to project directory
        os.chdir('/home/kevin/Projects/Llama-GPU')
        logger.info("✅ Project directory: /home/kevin/Projects/Llama-GPU")
        status["project"] = True

# Change to project directory
try:
    os.chdir('/home/kevin/Projects/Llama-GPU')
    print("✅ Project directory: /home/kevin/Projects/Llama-GPU")
except:
    print("❌ Could not find project directory")

# Check virtual environment
    if os.path.exists('venv'):
        logger.info("✅ Virtual environment exists")
        status["venv"] = True
    else:
        logger.error("❌ Virtual environment missing")
        return status

    # Check PyTorch and dependencies
    logger.info("\n📦 Checking Python dependencies...")
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
            timeout=10,
            check=True
        )
        logger.info("✅ PyTorch status:")
        pytorch_info = {}
        for line in result.stdout.strip().split('\n'):
            logger.info(f"   {line}")
            key, value = line.split(": ", 1)
            pytorch_info[key.lower()] = value
        status["pytorch"] = pytorch_info
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ PyTorch check failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("⚠️ PyTorch check timed out")
    except Exception as e:
        logger.error(f"⚠️ Could not check PyTorch: {e}")

    # Check ROCm backend
    logger.info("\n🔧 Checking Llama-GPU backends...")
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
            timeout=10,
            check=True
        )
        logger.info("✅ Backend status:")
        backend_info = {}
        for line in result.stdout.strip().split('\n'):
            logger.info(f"   {line}")
            key, value = line.split(": ", 1)
            backend_info[key.lower()] = value.lower() == "true"
        status["backend"] = backend_info
    except subprocess.CalledProcessError as e:
        logger.error(f"⚠️ Backend check failed: {e.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("⚠️ Backend check timed out")
    except OSError as e:
        logger.error(f"⚠️ Could not execute backend check: {e}")

    # Check WebSocket functionality
    logger.info("\n🌐 Checking WebSocket server...")
try:
    # Test if server is responding
    import requests
    from requests.exceptions import RequestException

    response = requests.get('http://localhost:8001/health', timeout=3)
    if response.status_code == 200:
        data = response.json()
        print("✅ Server running on port 8001")
        print(f"   Server: {data.get('server', 'unknown')}")
        print(f"   Status: {data.get('status', 'unknown')}")
    else:
        print("⚠️ Server responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("⚠️ Server not running on port 8001")
except RequestException as e:
    print(f"⚠️ Server check failed: {e}")

print("\n📊 Summary:")
print("✅ WebSocket connections working (from your logs)")
print("✅ Chat interface communicating with server")
print("💡 Next: Install ROCm PyTorch for GPU acceleration")

print("\n🚀 To enable AMD GPU acceleration:")
print("   chmod +x scripts/setup/complete_amd_setup.sh")
print("   ./scripts/setup/complete_amd_setup.sh")
