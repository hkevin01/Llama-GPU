#!/usr/bin/env python3
"""
Comprehensive GPU Diagnostics Tool for Llama-GPU
Integrates knowledge from rocm-patch project for RDNA1/RDNA2 GPUs
"""

import sys
import os
import subprocess
from typing import Dict, List, Optional, Any

sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")

try:
    from src.utils.gpu_detection import is_problematic_amd_gpu, apply_gfx1030_safeguard
    from src.utils.system_info import SystemInfo
    HAS_GPU_UTILS = True
except ImportError:
    HAS_GPU_UTILS = False
    print("⚠️  GPU utilities not available")


class GPUDiagnostics:
    """Comprehensive GPU diagnostics and recommendations."""
    
    def __init__(self):
        self.sys_info = None
        if HAS_GPU_UTILS:
            try:
                self.sys_info = SystemInfo.detect()
            except Exception as e:
                print(f"⚠️  Could not detect system info: {e}")
    
    def check_rocm_installation(self) -> Dict[str, Any]:
        """Check ROCm installation status."""
        result = {
            "installed": False,
            "version": None,
            "path": None,
            "hip_available": False,
            "issues": []
        }
        
        if not self.sys_info:
            result["issues"].append("System info detection failed")
            return result
        
        result["installed"] = self.sys_info.has_rocm
        result["version"] = self.sys_info.rocm_version
        result["path"] = str(self.sys_info.rocm_path) if self.sys_info.rocm_path else None
        result["hip_available"] = self.sys_info.has_hip
        
        # Check for known problematic versions
        if result["version"]:
            if result["version"].startswith("5.7"):
                result["issues"].append("ROCm 5.7 has poor RDNA1 support - consider ROCm 5.2")
            elif result["version"].startswith("6."):
                result["issues"].append("ROCm 6.x deprecates RDNA1 support")
        
        return result
    
    def check_gpu_compatibility(self) -> Dict[str, Any]:
        """Check GPU compatibility with LLM workloads."""
        result = {
            "gpu_count": 0,
            "architectures": [],
            "names": [],
            "problematic": False,
            "recommendations": []
        }
        
        if not self.sys_info:
            return result
        
        result["gpu_count"] = self.sys_info.gpu_count
        result["architectures"] = self.sys_info.gpu_architectures
        result["names"] = self.sys_info.gpu_names
        
        # Check for problematic AMD GPUs
        if HAS_GPU_UTILS:
            is_problem, reason = is_problematic_amd_gpu()
            result["problematic"] = is_problem
            if is_problem:
                result["recommendations"].append(f"⚠️  {reason}")
                result["recommendations"].append("Consider using CPU backend for stability")
                result["recommendations"].append("Or use --force-gpu-unsafe to override (may crash)")
        
        # Check architecture specific issues
        for arch in result["architectures"]:
            if arch.startswith("gfx10"):  # RDNA1/RDNA2
                result["recommendations"].append(f"Architecture {arch} (RDNA) detected")
                result["recommendations"].append("Use ROCm 5.2 with PyTorch 1.13.1 for best compatibility")
                result["recommendations"].append("Set MIOPEN_DEBUG_CONV_IMPLICIT_GEMM=1 for Conv2d operations")
        
        return result
    
    def check_pytorch_compatibility(self) -> Dict[str, Any]:
        """Check PyTorch and ROCm version compatibility."""
        result = {
            "pytorch_installed": False,
            "pytorch_version": None,
            "rocm_pytorch_version": None,
            "compatible": False,
            "recommendations": []
        }
        
        try:
            import torch
            result["pytorch_installed"] = True
            result["pytorch_version"] = torch.__version__
            
            # Check if it's ROCm PyTorch
            if hasattr(torch.version, 'hip'):
                result["rocm_pytorch_version"] = torch.version.hip
            
            # Check compatibility
            if self.sys_info and self.sys_info.rocm_version:
                rocm_ver = self.sys_info.rocm_version.split('.')[0:2]
                pytorch_rocm = result.get("rocm_pytorch_version", "")
                
                if pytorch_rocm:
                    pytorch_rocm_ver = pytorch_rocm.split('.')[0:2]
                    result["compatible"] = rocm_ver == pytorch_rocm_ver
                    
                    if not result["compatible"]:
                        result["recommendations"].append(
                            f"⚠️  PyTorch ROCm version ({pytorch_rocm}) doesn't match "
                            f"system ROCm ({self.sys_info.rocm_version})"
                        )
                        result["recommendations"].append(
                            "Recommended: ROCm 5.2 + PyTorch 1.13.1+rocm5.2"
                        )
        
        except ImportError:
            result["recommendations"].append("PyTorch not installed")
        except Exception as e:
            result["recommendations"].append(f"Error checking PyTorch: {e}")
        
        return result
    
    def check_ollama_compatibility(self) -> Dict[str, Any]:
        """Check Ollama GPU support."""
        result = {
            "ollama_installed": False,
            "running": False,
            "gpu_enabled": False,
            "recommendations": []
        }
        
        # Check if Ollama is installed
        try:
            check = subprocess.run(['which', 'ollama'], 
                                   capture_output=True, timeout=5)
            result["ollama_installed"] = check.returncode == 0
        except:
            pass
        
        # Check if running
        if result["ollama_installed"]:
            try:
                check = subprocess.run(['pgrep', '-x', 'ollama'], 
                                       capture_output=True, timeout=5)
                result["running"] = check.returncode == 0
            except:
                pass
        
        # Check GPU support
        if result["running"]:
            try:
                import requests
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    # Ollama responds, check if using GPU
                    # This is a simplified check - Ollama uses GPU by default on ROCm systems
                    if self.sys_info and self.sys_info.has_rocm:
                        result["gpu_enabled"] = True
            except:
                pass
        
        if not result["ollama_installed"]:
            result["recommendations"].append("Install Ollama for local LLM support")
        elif not result["running"]:
            result["recommendations"].append("Start Ollama: ollama serve")
        
        return result
    
    def get_optimal_settings(self) -> Dict[str, str]:
        """Get recommended environment settings for current GPU."""
        settings = {}
        
        if not self.sys_info or not self.sys_info.gpu_architectures:
            settings["BACKEND"] = "cpu"
            settings["REASON"] = "No GPU detected or system info unavailable"
            return settings
        
        # Check for RDNA1/RDNA2
        for arch in self.sys_info.gpu_architectures:
            if arch.startswith("gfx10"):
                # RDNA architecture
                settings["HSA_OVERRIDE_GFX_VERSION"] = "10.3.0"
                settings["MIOPEN_DEBUG_CONV_IMPLICIT_GEMM"] = "1"
                settings["MIOPEN_FIND_ENFORCE"] = "3"
                settings["PYTORCH_ROCM_ARCH"] = arch
                settings["BACKEND"] = "rocm"
                settings["REASON"] = f"RDNA GPU ({arch}) detected - using workarounds"
                
                # Check if problematic
                if HAS_GPU_UTILS:
                    is_problem, _ = is_problematic_amd_gpu()
                    if is_problem:
                        settings["RECOMMENDED_BACKEND"] = "cpu"
                        settings["WARNING"] = "This GPU may hang on large Conv2d operations"
                
                break
        else:
            # Other architectures
            settings["BACKEND"] = "rocm"
            settings["REASON"] = "AMD GPU detected"
        
        return settings
    
    def print_full_report(self):
        """Print comprehensive diagnostics report."""
        print("\n" + "=" * 70)
        print("🔍 GPU DIAGNOSTICS REPORT - Llama-GPU")
        print("=" * 70)
        
        # System Information
        if self.sys_info:
            print("\n📋 System Information:")
            print(f"   OS: {self.sys_info.os_name} {self.sys_info.os_version}")
            print(f"   Kernel: {self.sys_info.kernel_version}")
            print(f"   Python: {self.sys_info.python_version}")
        
        # ROCm Status
        print("\n🔧 ROCm Status:")
        rocm_info = self.check_rocm_installation()
        if rocm_info["installed"]:
            print(f"   ✅ ROCm Version: {rocm_info['version']}")
            print(f"   📁 ROCm Path: {rocm_info['path']}")
            print(f"   🔨 HIP Available: {'✅' if rocm_info['hip_available'] else '❌'}")
        else:
            print("   ❌ ROCm not detected")
        
        if rocm_info["issues"]:
            print("   ⚠️  Issues:")
            for issue in rocm_info["issues"]:
                print(f"      • {issue}")
        
        # GPU Compatibility
        print("\n🎮 GPU Information:")
        gpu_info = self.check_gpu_compatibility()
        print(f"   GPU Count: {gpu_info['gpu_count']}")
        if gpu_info["architectures"]:
            print(f"   Architectures: {', '.join(gpu_info['architectures'])}")
        if gpu_info["names"]:
            print(f"   GPU Names: {', '.join(gpu_info['names'])}")
        
        if gpu_info["problematic"]:
            print("   ⚠️  Problematic GPU detected!")
        
        if gpu_info["recommendations"]:
            print("   📝 Recommendations:")
            for rec in gpu_info["recommendations"]:
                print(f"      • {rec}")
        
        # PyTorch Compatibility
        print("\n🔥 PyTorch Status:")
        pytorch_info = self.check_pytorch_compatibility()
        if pytorch_info["pytorch_installed"]:
            print(f"   ✅ PyTorch: {pytorch_info['pytorch_version']}")
            if pytorch_info["rocm_pytorch_version"]:
                print(f"   🔧 ROCm Version: {pytorch_info['rocm_pytorch_version']}")
            print(f"   ✓ Compatible: {'✅' if pytorch_info['compatible'] else '⚠️'}")
        else:
            print("   ❌ PyTorch not installed")
        
        if pytorch_info["recommendations"]:
            print("   �� Recommendations:")
            for rec in pytorch_info["recommendations"]:
                print(f"      • {rec}")
        
        # Ollama Status
        print("\n🦙 Ollama Status:")
        ollama_info = self.check_ollama_compatibility()
        print(f"   Installed: {'✅' if ollama_info['ollama_installed'] else '❌'}")
        print(f"   Running: {'✅' if ollama_info['running'] else '❌'}")
        print(f"   GPU Enabled: {'✅' if ollama_info['gpu_enabled'] else '⚠️'}")
        
        if ollama_info["recommendations"]:
            print("   📝 Recommendations:")
            for rec in ollama_info["recommendations"]:
                print(f"      • {rec}")
        
        # Optimal Settings
        print("\n⚙️  Recommended Settings:")
        settings = self.get_optimal_settings()
        for key, value in settings.items():
            print(f"   export {key}={value}")
        
        print("\n" + "=" * 70)
        print("✅ Diagnostics Complete")
        print("=" * 70 + "\n")


def main():
    """Main entry point."""
    diagnostics = GPUDiagnostics()
    diagnostics.print_full_report()


if __name__ == "__main__":
    main()
