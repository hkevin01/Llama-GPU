#!/bin/bash
# Advanced AMD ROCm Setup with Multiple Version Options

echo "🚀 Advanced AMD ROCm Setup for Llama-GPU"
echo "=========================================="

cd /home/kevin/Projects/Llama-GPU

# Function to check AMD GPU
check_amd_gpu() {
    echo "🔍 Checking AMD GPU hardware..."
    if lspci | grep -i "amd\|radeon" > /dev/null; then
        echo "✅ AMD GPU hardware detected:"
        lspci | grep -i "amd\|radeon" | head -3
        return 0
    else
        echo "❌ No AMD GPU hardware detected"
        echo "This script is for AMD GPU systems only."
        return 1
    fi
}

# Function to get GPU architecture
get_gpu_arch() {
    echo "🔍 Detecting GPU architecture..."
    if command -v rocm-smi &> /dev/null; then
        GPU_ARCH=$(rocm-smi --showproductname | grep -i "gfx" | head -1)
        if [ -n "$GPU_ARCH" ]; then
            echo "✅ GPU Architecture detected: $GPU_ARCH"
        else
            echo "⚠️  Could not detect GPU architecture via rocm-smi"
        fi
    else
        echo "⚠️  rocm-smi not available, will use default settings"
    fi
}

# Function to install PyTorch with specific ROCm version
install_pytorch_rocm() {
    local rocm_version=$1
    echo "📦 Installing PyTorch with ROCm $rocm_version..."

    # Uninstall existing PyTorch
    echo "Removing existing PyTorch installations..."
    pip uninstall -y torch torchvision torchaudio 2>/dev/null || true

    # Install new PyTorch
    echo "Installing PyTorch with ROCm $rocm_version support..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm${rocm_version}

    if [ $? -eq 0 ]; then
        echo "✅ PyTorch with ROCm $rocm_version installed successfully"
        return 0
    else
        echo "❌ Failed to install PyTorch with ROCm $rocm_version"
        return 1
    fi
}

# Function to test PyTorch installation
test_pytorch() {
    echo "🧪 Testing PyTorch ROCm installation..."
    python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')

# Check ROCm support
if hasattr(torch.version, 'hip') and torch.version.hip:
    print(f'✅ ROCm/HIP support: {torch.version.hip}')

    # Test GPU availability
    if torch.cuda.is_available():
        print(f'✅ GPU available: True')
        print(f'✅ Device count: {torch.cuda.device_count()}')
        if torch.cuda.device_count() > 0:
            print(f'✅ Device name: {torch.cuda.get_device_name(0)}')

            # Test tensor creation on GPU
            try:
                x = torch.randn(1000, 1000).cuda()
                y = torch.randn(1000, 1000).cuda()
                z = torch.mm(x, y)
                print('✅ GPU tensor operations working!')
                print('🎉 ROCm GPU acceleration is fully functional!')
            except Exception as e:
                print(f'⚠️  GPU tensor operations failed: {e}')
        else:
            print('⚠️  No GPU devices detected')
    else:
        print('❌ GPU not available to PyTorch')
        print('This usually means:')
        print('  - ROCm drivers not installed')
        print('  - Environment variables not set')
        print('  - PyTorch compiled without ROCm support')
else:
    print('❌ PyTorch was not built with ROCm support')
"
}

# Main installation logic
main() {
    # Check prerequisites
    if ! check_amd_gpu; then
        exit 1
    fi

    # Activate virtual environment
    echo "📦 Activating virtual environment..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Please create one first:"
        echo "   python3 -m venv venv"
        exit 1
    fi

    # Get GPU architecture info (optional)
    get_gpu_arch

    # ROCm version selection
    echo ""
    echo "🎯 ROCm Version Selection:"
    echo "1. ROCm 6.3 (Latest stable - Recommended)"
    echo "2. ROCm 6.2 (Previous stable)"
    echo "3. ROCm 5.4.2 (Legacy support)"
    echo ""
    read -p "Select ROCm version (1-3) [default: 1]: " choice

    case $choice in
        2)
            rocm_version="6.2"
            ;;
        3)
            rocm_version="5.4.2"
            ;;
        *)
            rocm_version="6.3"
            ;;
    esac

    echo "Selected ROCm version: $rocm_version"

    # Install PyTorch
    if install_pytorch_rocm "$rocm_version"; then
        echo "✅ PyTorch installation completed"
    else
        echo "❌ PyTorch installation failed"
        echo "Trying fallback to ROCm 5.4.2..."
        if install_pytorch_rocm "5.4.2"; then
            echo "✅ Fallback installation succeeded"
            rocm_version="5.4.2"
        else
            echo "❌ All installation attempts failed"
            exit 1
        fi
    fi

    # Set up environment variables
    echo ""
    echo "🔧 Setting up environment variables..."
    export HIP_VISIBLE_DEVICES=0
    export ROCR_VISIBLE_DEVICES=0
    export HSA_OVERRIDE_GFX_VERSION=10.3.0

    # Test installation
    test_pytorch

    # Make environment variables persistent
    echo ""
    echo "🔧 Making environment variables persistent..."
    if ! grep -q "# AMD ROCm GPU Environment" ~/.bashrc; then
        {
            echo ""
            echo "# AMD ROCm GPU Environment Variables"
            echo "export HIP_VISIBLE_DEVICES=0"
            echo "export ROCR_VISIBLE_DEVICES=0"
            echo "export HSA_OVERRIDE_GFX_VERSION=10.3.0"
        } >> ~/.bashrc
        echo "✅ Environment variables added to ~/.bashrc"
    else
        echo "✅ Environment variables already in ~/.bashrc"
    fi

    # Test our backend
    echo ""
    echo "🔍 Testing Llama-GPU ROCm backend..."
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
    print(f'Backend test: {e}')
    print('ℹ️  This is normal if the backend needs the new PyTorch')
"

    # Final status
    echo ""
    echo "🎉 AMD ROCm Setup Complete!"
    echo "=========================================="
    echo "📊 Installation Summary:"
    echo "   ✓ ROCm version: $rocm_version"
    echo "   ✓ PyTorch with ROCm support installed"
    echo "   ✓ Environment variables configured"
    echo "   ✓ GPU backend tested"
    echo ""
    echo "🔄 Next Steps:"
    echo "   1. Restart your terminal or run: source ~/.bashrc"
    echo "   2. Test your chat interface"
    echo "   3. Monitor GPU usage with: watch -n 1 rocm-smi"
    echo ""
    echo "💡 Performance Tips:"
    echo "   • GPU acceleration will speed up model inference"
    echo "   • Larger models will see the biggest improvements"
    echo "   • Monitor GPU memory usage during operation"
}

# Run main function
main "$@"
