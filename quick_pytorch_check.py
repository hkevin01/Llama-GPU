#!/usr/bin/env python3
import torch

print("🔍 Current PyTorch Status")
print("=" * 30)
print(f"PyTorch Version: {torch.__version__}")
print(f"HIP/ROCm Support: {getattr(torch.version, 'hip', 'No ROCm')}")
print(f"GPU Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"GPU Device Count: {torch.cuda.device_count()}")
    if torch.cuda.device_count() > 0:
        print(f"GPU Device Name: {torch.cuda.get_device_name(0)}")
else:
    print("GPU: Not available to PyTorch")

print("\n🔧 AMD Hardware Check:")
import subprocess

try:
    result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
    amd_lines = [line for line in result.stdout.split('\n')
                 if 'amd' in line.lower() or 'radeon' in line.lower()]
    if amd_lines:
        print("✅ AMD GPU hardware detected:")
        for line in amd_lines[:2]:
            print(f"   {line.strip()}")
    else:
        print("❌ No AMD GPU hardware detected")
except:
    print("⚠️ Could not check hardware")
