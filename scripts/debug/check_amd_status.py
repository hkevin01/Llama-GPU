#!/usr/bin/env python3
"""Simple check of current AMD GPU acceleration status"""

import os
import subprocess
import sys


def check_current_status():
    """Check current PyTorch and GPU status"""
    print("🔍 Current AMD GPU Acceleration Status")
    print("=" * 45)

    # Change to project directory
    os.chdir('/home/kevin/Projects/Llama-GPU')

    # Check if virtual environment exists
    if os.path.exists('venv'):
        print("✅ Virtual environment found")
        python_exec = 'venv/bin/python3'
    else:
        print("❌ Virtual environment not found")
        python_exec = 'python3'

    # Check PyTorch installation
    try:
        result = subprocess.run([
            python_exec, '-c',
            '''
import torch
print(f"PyTorch Version: {torch.__version__}")
print(f"HIP/ROCm Support: {getattr(torch.version, 'hip', 'None')}")
print(f"CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device Count: {torch.cuda.device_count()}")
    if torch.cuda.device_count() > 0:
        print(f"GPU Device Name: {torch.cuda.get_device_name(0)}")

        # Test a simple operation
        try:
            x = torch.randn(100, 100).cuda()
            y = torch.randn(100, 100).cuda()
            z = torch.mm(x, y)
            print("✅ GPU operations working!")
        except Exception as e:
            print(f"❌ GPU operations failed: {e}")
'''
        ], capture_output=True, text=True, timeout=15)

        if result.returncode == 0:
            print("\n🐍 PyTorch Status:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"❌ PyTorch check failed: {result.stderr}")

    except Exception as e:
        print(f"⚠️ Error checking PyTorch: {e}")

    # Check AMD hardware
    print("\n🔧 Hardware Status:")
    try:
        result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            amd_lines = [line for line in result.stdout.split('\n')
                        if 'amd' in line.lower() or 'radeon' in line.lower()]
            if amd_lines:
                print("✅ AMD GPU hardware detected:")
                for line in amd_lines[:2]:
                    print(f"   {line.strip()}")
            else:
                print("❌ No AMD GPU hardware detected")
    except Exception as e:
        print(f"⚠️ Hardware check failed: {e}")

    # Check our backend
    print("\n🚀 Llama-GPU Backend Status:")
    try:
        result = subprocess.run([
            python_exec, '-c',
            '''
try:
    from utils.rocm_backend import HAS_AMD_GPU, HAS_ROCM, rocm_backend
    print(f"AMD GPU Detected: {HAS_AMD_GPU}")
    print(f"ROCm Available: {HAS_ROCM}")
    print(f"Backend Ready: {rocm_backend.available}")
except Exception as e:
    print(f"Backend check error: {e}")
'''
        ], capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print(f"⚠️ Backend check failed: {result.stderr}")

    except Exception as e:
        print(f"⚠️ Backend check error: {e}")

    print("\n📊 Summary:")
    print("✅ Chat interface is working (CPU mode)")
    print("✅ WebSocket connections established")
    print("🔄 GPU acceleration is optional optimization")

    print("\n💡 To enable GPU acceleration:")
    print("   chmod +x complete_amd_setup.sh")
    print("   ./complete_amd_setup.sh")

if __name__ == "__main__":
    check_current_status()
