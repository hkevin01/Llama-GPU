#!/usr/bin/env python3
"""Install ROCm-enabled PyTorch for AMD GPU systems"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    print("🔧 Installing ROCm-enabled PyTorch for AMD GPU")
    print("=" * 50)

    # Change to project directory
    os.chdir('/home/kevin/Projects/Llama-GPU')

    # Activate virtual environment and install
    commands = [
        ("source venv/bin/activate && pip uninstall -y torch torchvision torchaudio",
         "Removing existing PyTorch"),
        ("source venv/bin/activate && pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2",
         "Installing ROCm-enabled PyTorch"),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"❌ Failed at: {desc}")
            return False

    # Test the installation
    print("\n🧪 Testing PyTorch ROCm installation...")
    test_script = '''
import torch
print(f"PyTorch version: {torch.__version__}")
if hasattr(torch.version, "hip") and torch.version.hip:
    print(f"✅ HIP/ROCm version: {torch.version.hip}")
    if torch.cuda.is_available():
        print(f"✅ GPU available: {torch.cuda.get_device_name(0)}")
        print(f"✅ Device count: {torch.cuda.device_count()}")
        print("🎉 ROCm setup successful!")
    else:
        print("⚠️  PyTorch installed but no GPU devices available")
        print("Try: export HIP_VISIBLE_DEVICES=0")
else:
    print("❌ PyTorch was not built with ROCm support")
'''

    success = run_command(f"source venv/bin/activate && python3 -c '{test_script}'",
                         "Testing PyTorch ROCm installation")

    if success:
        print("\n🎉 ROCm PyTorch installation complete!")
        print("Now run: ./quick_test.sh")
    else:
        print("\n❌ Installation test failed")

    return success

if __name__ == "__main__":
    main()
