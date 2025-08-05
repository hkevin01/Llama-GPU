#!/usr/bin/env python3
"""Quick AMD/ROCm system check"""

import subprocess
import sys

print("🔍 Quick AMD/ROCm Check")
print("=" * 30)

# Check for AMD hardware
try:
    result = subprocess.run(['lspci'], capture_output=True,
                           text=True, timeout=5)
    amd_lines = [line for line in result.stdout.split('\n')
                if 'amd' in line.lower() or 'radeon' in line.lower()]
    if amd_lines:
        print("✅ AMD hardware found:")
        for line in amd_lines[:3]:  # Show first 3 matches
            print(f"  {line.strip()}")
    else:
        print("❌ No AMD hardware detected")
except Exception as e:
    print(f"⚠️ Could not check hardware: {e}")

# Check ROCm
try:
    result = subprocess.run(['rocm-smi'], capture_output=True,
                           text=True, timeout=5)
    if result.returncode == 0:
        print("✅ rocm-smi available")
    else:
        print("❌ rocm-smi not working")
except Exception as e:
    print(f"❌ rocm-smi not found: {e}")

# Check PyTorch ROCm
try:
    import torch
    print(f"✅ PyTorch {torch.__version__} installed")
    if hasattr(torch.version, 'hip') and torch.version.hip:
        print(f"✅ ROCm support: {torch.version.hip}")
        if torch.cuda.is_available():
            print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
        else:
            print("❌ No GPU devices available to PyTorch")
    else:
        print("❌ No ROCm support in PyTorch")
except ImportError:
    print("❌ PyTorch not installed")
except Exception as e:
    print(f"⚠️ PyTorch check failed: {e}")

print("\nTesting our ROCm backend...")
try:
    sys.path.append('/home/kevin/Projects/Llama-GPU')
    from utils.rocm_backend import HAS_AMD_GPU, HAS_ROCM, rocm_backend
    print(f"HAS_AMD_GPU: {HAS_AMD_GPU}")
    print(f"HAS_ROCM: {HAS_ROCM}")
    print(f"Backend available: {rocm_backend.available}")
    if rocm_backend.available:
        device_info = rocm_backend.get_device_info()
        print(f"Device info: {device_info}")
except Exception as e:
    print(f"❌ Backend test failed: {e}")
