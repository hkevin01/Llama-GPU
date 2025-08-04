#!/bin/bash
echo "🔧 AMD/ROCm Setup Script for Llama-GPU"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "mock_api_server.py" ]; then
    echo "❌ Error: Please run this script from the Llama-GPU root directory"
    exit 1
fi

# Check for AMD hardware
echo "🔍 Checking for AMD hardware..."
if lspci | grep -i amd; then
    echo "✅ AMD hardware detected"
elif lspci | grep -i radeon; then
    echo "✅ AMD Radeon hardware detected"
else
    echo "⚠️  No AMD hardware detected in lspci output"
    echo "This script is designed for AMD GPU systems"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create/activate virtual environment
echo "📦 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Created virtual environment"
fi

source venv/bin/activate
echo "✅ Activated virtual environment"

# Uninstall any existing PyTorch
echo "🧹 Removing any existing PyTorch installation..."
pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

# Install ROCm-enabled PyTorch
echo "📦 Installing ROCm-enabled PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2

if [ $? -eq 0 ]; then
    echo "✅ ROCm-enabled PyTorch installed successfully"
else
    echo "❌ Failed to install ROCm-enabled PyTorch"
    echo "You may need to install ROCm first:"
    echo "  • Ubuntu: https://docs.amd.com/bundle/ROCm-Installation-Guide-v5.4.2"
    echo "  • Or try a different ROCm version"
    exit 1
fi

# Install other required packages
echo "📦 Installing other required dependencies..."
pip install fastapi uvicorn websockets python-multipart requests

# Test the installation
echo "🧪 Testing PyTorch ROCm installation..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
if hasattr(torch.version, 'hip') and torch.version.hip:
    print(f'✅ HIP version: {torch.version.hip}')
    if torch.cuda.is_available():
        print(f'✅ GPU available: {torch.cuda.get_device_name(0)}')
        print(f'✅ Device count: {torch.cuda.device_count()}')
    else:
        print('⚠️  PyTorch installed but no GPU devices available')
        print('Check ROCm installation and HIP_VISIBLE_DEVICES')
else:
    print('❌ PyTorch was not built with ROCm support')
    print('Installation may have failed')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup complete!"
    echo "✅ AMD/ROCm environment is ready"
    echo ""
    echo "Next steps:"
    echo "1. Test the connection: ./quick_test.sh"
    echo "2. Start the GUI: cd llama-gui && npm start"
    echo ""
    echo "If you encounter issues:"
    echo "• Check ROCm installation: rocm-smi"
    echo "• Set GPU visibility: export HIP_VISIBLE_DEVICES=0"
    echo "• Check troubleshooting in README.md"
else
    echo "❌ Setup verification failed"
    echo "Check the error messages above"
fi
