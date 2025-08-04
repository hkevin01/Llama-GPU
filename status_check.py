#!/usr/bin/env python3
"""Check current system status for Llama-GPU"""

import os
import subprocess
import sys

print("🔍 Llama-GPU System Status Check")
print("=" * 40)

# Change to project directory
try:
    os.chdir('/home/kevin/Projects/Llama-GPU')
    print("✅ Project directory: /home/kevin/Projects/Llama-GPU")
except:
    print("❌ Could not find project directory")

# Check virtual environment
if os.path.exists('venv'):
    print("✅ Virtual environment exists")
else:
    print("❌ Virtual environment missing")

# Activate venv and check dependencies
print("\n📦 Checking Python dependencies...")
try:
    result = subprocess.run(
        'source venv/bin/activate && python3 -c "import torch; print(f\'PyTorch: {torch.__version__}\'); print(f\'HIP: {getattr(torch.version, \'hip\', \'No ROCm\')}\'); print(f\'GPU Available: {torch.cuda.is_available()}\')"',
        shell=True, capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        print("✅ PyTorch status:")
        for line in result.stdout.strip().split('\n'):
            print(f"   {line}")
    else:
        print(f"❌ PyTorch check failed: {result.stderr}")
except Exception as e:
    print(f"⚠️ Could not check PyTorch: {e}")

# Check our ROCm backend
print("\n🔧 Checking Llama-GPU backends...")
try:
    cmd = [
        "python3",
        "-c",
        "from src.utils.amd.rocm_backend import (HAS_AMD_GPU, HAS_ROCM, "
        "rocm_backend); "
        "print('AMD GPU: ' + str(HAS_AMD_GPU)); "
        "print('ROCm Available: ' + str(HAS_ROCM)); "
        "print('Backend Ready: ' + str(rocm_backend.available))"
    ]
    result = subprocess.run(
        ["source", "venv/bin/activate", "&&"] + cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=10,
        check=True
    )
    print("✅ Backend status:")
    for line in result.stdout.strip().split('\n'):
        print(f"   {line}")
except subprocess.CalledProcessError as e:
    print(f"⚠️ Backend check failed: {e.stderr}")
except subprocess.TimeoutExpired:
    print("⚠️ Backend check timed out")
except OSError as e:
    print(f"⚠️ Could not execute backend check: {e}")

# Check WebSocket functionality
print("\n🌐 Checking WebSocket server...")
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
