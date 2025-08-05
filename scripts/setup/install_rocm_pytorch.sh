#!/bin/bash
echo "🔧 Installing ROCm-enabled PyTorch for AMD GPU..."

# Navigate to project directory
cd /home/kevin/Projects/Llama-GPU

# Activate virtual environment
source venv/bin/activate

# Remove existing PyTorch installation
echo "📦 Removing existing PyTorch..."
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

# Install ROCm-enabled PyTorch
echo "📦 Installing ROCm-enabled PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2

# Test the installation
echo "🧪 Testing PyTorch ROCm installation..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
if hasattr(torch.version, 'hip') and torch.version.hip:
    print(f'✅ HIP/ROCm version: {torch.version.hip}')
    if torch.cuda.is_available():
        print(f'✅ GPU available: {torch.cuda.get_device_name(0)}')
        print(f'✅ Device count: {torch.cuda.device_count()}')
        print('🎉 ROCm setup successful!')
    else:
        print('⚠️  PyTorch installed but no GPU devices available')
        print('Try: export HIP_VISIBLE_DEVICES=0')
else:
    print('❌ PyTorch was not built with ROCm support')
"

echo "✅ ROCm PyTorch installation complete!"
