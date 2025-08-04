#!/usr/bin/env python3
"""
AMD/ROCm Hardware Detection Script for Llama-GPU
Tests AMD GPU availability and ROCm configuration
"""

import logging
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def check_amd_hardware():
    """Check for AMD hardware presence"""
    print("🔍 Checking for AMD hardware...")

    # Check for AMD GPUs via lspci
    try:
        result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            amd_lines = [line for line in result.stdout.lower().split('\n')
                        if 'amd' in line or 'radeon' in line or 'rx ' in line]
            if amd_lines:
                print("✅ AMD hardware detected:")
                for line in amd_lines:
                    print(f"    {line.strip()}")
                return True
            else:
                print("❌ No AMD hardware found in lspci output")
                return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  Could not run lspci to check hardware")
        return False

def check_rocm_installation():
    """Check ROCm installation status"""
    print("\n🔍 Checking ROCm installation...")

    # Check rocm-smi
    try:
        result = subprocess.run(['rocm-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ rocm-smi is available")
            print("ROCm output:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print(f"❌ rocm-smi failed with return code {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ rocm-smi not found - ROCm may not be installed")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  rocm-smi timed out")
        return False

def check_hip():
    """Check HIP installation"""
    print("\n🔍 Checking HIP installation...")

    try:
        result = subprocess.run(['hipconfig', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ HIP is available")
            print(f"HIP version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("❌ hipconfig not found")

    # Alternative check
    try:
        result = subprocess.run(['hip-config', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ HIP is available (hip-config)")
            print(f"HIP version: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        print("❌ hip-config not found")

    print("❌ HIP not found")
    return False

def check_pytorch_rocm():
    """Check PyTorch ROCm support"""
    print("\n🔍 Checking PyTorch ROCm support...")

    try:
        import torch
        print("✅ PyTorch is installed")
        print(f"PyTorch version: {torch.__version__}")

        # Check for ROCm support
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            print(f"✅ PyTorch has ROCm/HIP support: {torch.version.hip}")

            # Check if CUDA (which includes ROCm in PyTorch) is available
            if torch.cuda.is_available():
                print("✅ PyTorch CUDA/ROCm backend is available")
                print(f"Device count: {torch.cuda.device_count()}")
                if torch.cuda.device_count() > 0:
                    print(f"Device name: {torch.cuda.get_device_name(0)}")
                    print(f"Device properties: {torch.cuda.get_device_properties(0)}")
                return True
            else:
                print("❌ PyTorch CUDA/ROCm backend not available")
                return False
        else:
            print("❌ PyTorch was not built with ROCm support")
            print("To install ROCm-enabled PyTorch:")
            print("pip install torch --index-url https://download.pytorch.org/whl/rocm5.4.2")
            return False

    except ImportError:
        print("❌ PyTorch not installed")
        print("To install ROCm-enabled PyTorch:")
        print("pip install torch --index-url https://download.pytorch.org/whl/rocm5.4.2")
        return False

def check_environment_variables():
    """Check relevant environment variables"""
    print("\n🔍 Checking environment variables...")

    import os
    rocm_vars = ['ROCM_PATH', 'HIP_PATH', 'DEVICE_LIB_PATH', 'HIP_VISIBLE_DEVICES']

    found_vars = False
    for var in rocm_vars:
        if var in os.environ:
            print(f"✅ {var} = {os.environ[var]}")
            found_vars = True

    if not found_vars:
        print("ℹ️  No ROCm environment variables found")
        print("You may need to source ROCm environment setup:")
        print("source /opt/rocm/bin/rocm-env.sh")

def main():
    """Main detection routine"""
    print("🚀 AMD/ROCm Hardware Detection for Llama-GPU")
    print("=" * 50)

    has_amd_hw = check_amd_hardware()
    has_rocm = check_rocm_installation()
    has_hip = check_hip()
    has_pytorch_rocm = check_pytorch_rocm()
    check_environment_variables()

    print("\n" + "=" * 50)
    print("📋 Summary:")

    if has_amd_hw:
        print("✅ AMD hardware detected")
    else:
        print("❌ No AMD hardware found")

    if has_rocm:
        print("✅ ROCm tools available")
    else:
        print("❌ ROCm tools not found")

    if has_hip:
        print("✅ HIP available")
    else:
        print("❌ HIP not found")

    if has_pytorch_rocm:
        print("✅ PyTorch with ROCm support")
    else:
        print("❌ PyTorch ROCm support missing")

    if has_amd_hw and has_rocm and has_pytorch_rocm:
        print("\n🎉 System appears ready for AMD/ROCm acceleration!")
    elif has_amd_hw:
        print("\n⚠️  AMD hardware detected but ROCm setup incomplete")
        print("Install missing components for full GPU acceleration")
    else:
        print("\n❌ No AMD GPU acceleration available")

if __name__ == "__main__":
    main()
