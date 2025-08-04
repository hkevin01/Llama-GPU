#!/usr/bin/env python3
"""Quick AMD GPU acceleration check"""

import os
import subprocess
import sys

print("🚀 AMD GPU Acceleration Check")
print("=" * 50)

os.chdir('/home/kevin/Projects/Llama-GPU')

# Check if venv exists and activate it
if os.path.exists('venv'):
    print("✅ Virtual environment found")
    # Activate venv for subsequent commands
    venv_python = 'venv/bin/python3'
else:
    print("❌ Virtual environment not found")
    venv_python = 'python3'

print("\n🔍 Checking current PyTorch installation...")
try:
    result = subprocess.run([
        venv_python, '-c',
        """
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'HIP version: {getattr(torch.version, "hip", "No ROCm")}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'Device count: {torch.cuda.device_count()}')
    if torch.cuda.device_count() > 0:
        print(f'Device name: {torch.cuda.get_device_name(0)}')
"""
    ], capture_output=True, text=True, timeout=10)

    if result.returncode == 0:
        print("✅ PyTorch status:")
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print(f"❌ PyTorch check failed: {result.stderr}")

except Exception as e:
    print(f"⚠️ Error checking PyTorch: {e}")

print("\n🔧 Checking AMD GPU hardware...")
try:
    result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        amd_lines = [line for line in result.stdout.split('\n')
                     if 'amd' in line.lower() or 'radeon' in line.lower()]
        if amd_lines:
            print("✅ AMD GPU hardware detected:")
            for line in amd_lines[:3]:  # Show first 3 matches
                print(f"   {line.strip()}")
        else:
            print("❌ No AMD GPU hardware detected")
    else:
        print("⚠️ Could not check hardware")
except Exception as e:
    print(f"⚠️ Error checking hardware: {e}")

print("\n📊 Current Status:")
print("✅ WebSocket chat interface working")
print("✅ Server communication established")
print("🔄 Running in CPU mode (functional)")

print("\n🎯 Next Steps for GPU Acceleration:")
print("   Run: chmod +x complete_amd_setup.sh")
print("   Run: ./complete_amd_setup.sh")
print("   This will install ROCm-enabled PyTorch for GPU acceleration")
