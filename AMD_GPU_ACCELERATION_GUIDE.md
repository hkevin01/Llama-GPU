# AMD GPU Acceleration Guide for Llama-GPU

## 🎯 Current Status
✅ **System Working**: Your Llama-GPU chat interface is fully functional
✅ **WebSocket Connected**: Server communication is established
✅ **CPU Mode**: Currently running on CPU (functional but slower)

## 🚀 AMD GPU Acceleration Setup

### Option 1: Quick Setup (Recommended)
```bash
# Make the setup script executable
chmod +x complete_amd_setup.sh

# Run the automated setup
./complete_amd_setup.sh
```

### Option 2: Advanced Setup with Multiple ROCm Versions
```bash
# Make the advanced script executable
chmod +x advanced_amd_setup.sh

# Run with version selection
./advanced_amd_setup.sh
```

### Option 3: Manual Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Remove existing PyTorch
pip uninstall -y torch torchvision torchaudio

# Install ROCm-enabled PyTorch (latest)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.3

# Set environment variables
export HIP_VISIBLE_DEVICES=0
export ROCR_VISIBLE_DEVICES=0

# Test installation
python3 -c "import torch; print(f'ROCm: {torch.version.hip}'); print(f'GPU: {torch.cuda.is_available()}')"
```

## 📊 Monitoring and Testing

### Check Current Status
```bash
python3 check_amd_status.py
```

### Monitor GPU Performance
```bash
# Show current GPU status
python3 amd_gpu_monitor.py info

# Run performance test
python3 amd_gpu_monitor.py test

# Continuous monitoring
python3 amd_gpu_monitor.py monitor
```

### Manual GPU Commands
```bash
# Check AMD hardware
lspci | grep -i "amd\|radeon"

# Monitor GPU (if ROCm system tools installed)
rocm-smi

# Watch GPU usage
watch -n 1 rocm-smi
```

## 🔧 ROCm Version Support Matrix

| ROCm Version | PyTorch Support | Stability | Recommendation |
|--------------|----------------|-----------|----------------|
| **6.3**      | ✅ Latest     | Stable    | **Recommended** |
| **6.2**      | ✅ Good       | Stable    | Alternative    |
| **5.4.2**    | ✅ Legacy     | Stable    | Fallback       |

## 🎯 Expected Performance Improvements

### CPU vs GPU Performance
- **Text Generation**: 2-5x faster with GPU
- **Model Loading**: Similar (one-time cost)
- **Memory Usage**: GPU VRAM vs System RAM
- **Power Efficiency**: Generally more efficient

### GPU Memory Requirements
- **Small Models** (<7B params): 4-8GB VRAM
- **Medium Models** (7-13B params): 8-16GB VRAM
- **Large Models** (>13B params): 16GB+ VRAM

## 🛠️ Troubleshooting

### Common Issues

**1. PyTorch Can't See GPU**
```bash
# Check environment variables
echo $HIP_VISIBLE_DEVICES
echo $ROCR_VISIBLE_DEVICES

# Set manually if needed
export HIP_VISIBLE_DEVICES=0
export ROCR_VISIBLE_DEVICES=0
```

**2. ROCm Version Mismatch**
```bash
# Try different ROCm version
pip install torch --index-url https://download.pytorch.org/whl/rocm5.4.2
```

**3. GPU Memory Issues**
```bash
# Monitor memory usage
python3 -c "import torch; print(f'Memory: {torch.cuda.memory_allocated()/1e9:.1f}GB')"

# Clear GPU cache
python3 -c "import torch; torch.cuda.empty_cache()"
```

**4. Environment Variables Not Persistent**
```bash
# Add to shell profile
echo 'export HIP_VISIBLE_DEVICES=0' >> ~/.bashrc
echo 'export ROCR_VISIBLE_DEVICES=0' >> ~/.bashrc
source ~/.bashrc
```

## 📋 Step-by-Step Verification

1. **Check Hardware**: `lspci | grep -i amd`
2. **Check PyTorch**: `python3 -c "import torch; print(torch.version.hip)"`
3. **Test GPU**: `python3 -c "import torch; print(torch.cuda.is_available())"`
4. **Run Performance Test**: `python3 amd_gpu_monitor.py test`
5. **Test Chat Interface**: Use your WebSocket chat interface
6. **Monitor Usage**: `python3 amd_gpu_monitor.py monitor`

## 🎉 Success Indicators

✅ PyTorch shows ROCm/HIP version
✅ `torch.cuda.is_available()` returns `True`
✅ GPU operations complete without errors
✅ Chat interface responses are faster
✅ GPU memory usage visible in monitoring

## 💡 Performance Tips

1. **Model Selection**: Choose models that fit in GPU memory
2. **Batch Size**: Optimize batch size for your GPU memory
3. **Memory Management**: Clear GPU cache between large operations
4. **Environment**: Keep ROCm environment variables set
5. **Monitoring**: Watch GPU usage to ensure utilization

## 🔄 Next Steps After GPU Setup

1. **Test Chat Performance**: Compare response times
2. **Monitor GPU Usage**: Watch memory and utilization
3. **Optimize Settings**: Tune batch sizes and memory usage
4. **Benchmark**: Run performance tests with your models
5. **Scale Up**: Try larger models with GPU acceleration

## 📞 Support

If you encounter issues:
1. Run `python3 check_amd_status.py` for diagnostics
2. Check the troubleshooting section above
3. Verify your AMD GPU model is ROCm-compatible
4. Consider starting with ROCm 5.4.2 for better compatibility

Remember: **Your system is already working perfectly in CPU mode**. GPU acceleration is an optional performance optimization!
