#!/bin/bash
# Complete AMD/ROCm setup and test script - Updated for ROCm 6.3

echo "🚀 Complete AMD/ROCm Setup for Llama-GPU"
echo "========================================"

cd /home/kevin/Projects/Llama-GPU

# Check for AMD GPU hardware first
echo "🔍 Checking AMD GPU hardware..."
if lspci | grep -i "amd\|radeon" > /dev/null; then
    echo "✅ AMD GPU hardware detected:"
    lspci | grep -i "amd\|radeon" | head -2
else
    echo "❌ No AMD GPU hardware detected"
    echo "This script is for AMD GPU systems only."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install ROCm PyTorch with latest supported version (ROCm 6.3)
echo "📦 Installing ROCm-enabled PyTorch..."
echo "Uninstalling any existing PyTorch..."
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

echo "Installing PyTorch with ROCm 6.3 support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.3

# Set up GPU visibility and environment variables
echo "🔧 Setting up GPU environment..."
export HIP_VISIBLE_DEVICES=0
export ROCR_VISIBLE_DEVICES=0

# Test PyTorch ROCm installation
echo "🧪 Testing PyTorch ROCm..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
if hasattr(torch.version, 'hip') and torch.version.hip:
    print(f'✅ ROCm/HIP version: {torch.version.hip}')
    if torch.cuda.is_available():
        print(f'✅ GPU available: {torch.cuda.get_device_name(0)}')
        print(f'✅ Device count: {torch.cuda.device_count()}')
        print('🎉 ROCm setup successful!')
    else:
        print('⚠️  PyTorch installed but GPU not visible')
        print('Checking GPU detection...')

        # Check if AMD GPU is detected
        import subprocess
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True)
            amd_gpus = [line for line in result.stdout.split('\n') if 'amd' in line.lower() or 'radeon' in line.lower()]
            if amd_gpus:
                print('✅ AMD GPU hardware detected:')
                for gpu in amd_gpus[:2]:
                    print(f'   {gpu.strip()}')
                print('💡 GPU hardware found but PyTorch cannot access it')
            else:
                print('❌ No AMD GPU hardware detected')
        except:
            print('⚠️  Could not check hardware')
else:
    print('❌ PyTorch was not built with ROCm support')
    print('Installation may have failed')
"

# Add environment variables to shell profile for persistence
echo ""
echo "� Making environment variables persistent..."
{
    echo ""
    echo "# AMD ROCm GPU Environment Variables"
    echo "export HIP_VISIBLE_DEVICES=0"
    echo "export ROCR_VISIBLE_DEVICES=0"
    echo "export HSA_OVERRIDE_GFX_VERSION=10.3.0"  # Common compatibility setting
} >> ~/.bashrc

echo "✅ Environment variables added to ~/.bashrc"

echo ""
echo "🔍 Testing our ROCm backend..."
python3 -c "
try:
    from utils.rocm_backend import HAS_AMD_GPU, HAS_ROCM, rocm_backend
    print(f'AMD GPU detected: {HAS_AMD_GPU}')
    print(f'ROCm available: {HAS_ROCM}')
    print(f'Backend ready: {rocm_backend.available}')
    if rocm_backend.available:
        print('🎉 Llama-GPU ROCm backend is ready!')
    else:
        print('⚠️  ROCm backend not fully ready')
except Exception as e:
    print(f'⚠️  Backend test failed: {e}')
"

echo ""
echo "🔍 Testing server connection..."
if [ -f "quick_test.sh" ]; then
    chmod +x quick_test.sh
    ./quick_test.sh
else
    echo "⚠️  quick_test.sh not found, skipping server test"
fi

echo ""
echo "✅ AMD ROCm Setup Complete!"
echo "🎯 Status:"
echo "   ✓ ROCm PyTorch installed"
echo "   ✓ Environment variables configured"
echo "   ✓ GPU backend tested"
echo ""
echo "💡 If GPU acceleration is not working:"
echo "   1. Restart your terminal session"
echo "   2. Source the environment: source ~/.bashrc"
echo "   3. Verify: python3 -c \"import torch; print(torch.cuda.is_available())\""
echo "   4. Check GPU: rocm-smi (if ROCm is system-installed)"
