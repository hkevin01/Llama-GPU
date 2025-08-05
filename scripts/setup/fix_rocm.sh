#!/bin/bash
echo "🔧 Installing ROCm PyTorch for AMD GPU..."

cd /home/kevin/Projects/Llama-GPU
source venv/bin/activate

echo "📦 Uninstalling existing PyTorch..."
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

echo "📦 Installing ROCm-enabled PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2

echo "🧪 Testing PyTorch ROCm..."
python3 -c "
import torch
print(f'PyTorch: {torch.__version__}')
if hasattr(torch.version, 'hip') and torch.version.hip:
    print(f'✅ ROCm/HIP: {torch.version.hip}')
    if torch.cuda.is_available():
        print(f'✅ GPU: {torch.cuda.get_device_name(0)}')
        print('🎉 ROCm setup successful!')
    else:
        print('⚠️  GPU not visible, try: export HIP_VISIBLE_DEVICES=0')
else:
    print('❌ No ROCm support')
"

echo "✅ Done! Now test with: ./quick_test.sh"
