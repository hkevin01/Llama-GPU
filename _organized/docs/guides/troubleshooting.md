# Troubleshooting Guide

This guide covers common issues and their solutions when using Llama-GPU.

## Installation Issues

### Python Environment Problems

**Issue**: `ModuleNotFoundError` or import errors
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Verify installation
pip list | grep torch
pip list | grep transformers
```

**Issue**: Version conflicts
```bash
# Solution: Clean install
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### GPU Driver Issues

**Issue**: CUDA not available
```bash
# Check NVIDIA drivers
nvidia-smi

# If not available, install drivers:
# Ubuntu/Debian:
sudo apt update
sudo apt install nvidia-driver-470

# CentOS/RHEL:
sudo yum install nvidia-driver
```

**Issue**: ROCm not available
```bash
# Check AMD drivers
rocm-smi

# If not available, install ROCm:
# Ubuntu:
wget https://repo.radeon.com/amdgpu-install/5.7.3/ubuntu/jammy/amdgpu-install_5.7.3.50703-1_all.deb
sudo apt install ./amdgpu-install_5.7.3.50703-1_all.deb
sudo amdgpu-install --usecase=hiplibsdk,rocm
```

## Runtime Issues

### Memory Problems

**Issue**: `CUDA out of memory` or `RuntimeError: CUDA error: out of memory`
```python
# Solution 1: Reduce batch size
results = llama.batch_infer(inputs, batch_size=1)

# Solution 2: Clear GPU cache
import torch
torch.cuda.empty_cache()

# Solution 3: Use smaller model
# Consider using quantized models (4-bit, 8-bit)

# Solution 4: Monitor memory usage
python scripts/monitor_resources.py --interval 1 --duration 30
```

**Issue**: System memory exhaustion
```bash
# Check available memory
free -h

# Solution: Close other applications or use swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Backend Selection Issues

**Issue**: Wrong backend selected
```python
# Check current backend
info = llama.get_backend_info()
print(f"Current backend: {info['backend_type']}")

# Force specific backend
llama = LlamaGPU("path/to/model", prefer_gpu=False)  # Force CPU
llama = LlamaGPU("path/to/model", prefer_gpu=True)   # Force GPU preference
```

**Issue**: AWS detection not working
```python
# Check if running on AWS
import requests
try:
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-type', timeout=1)
    print(f"Instance type: {response.text}")
except:
    print("Not running on AWS")

# Manual AWS detection
from utils.aws_detection import is_aws_gpu_instance, get_aws_gpu_info
print(f"AWS GPU instance: {is_aws_gpu_instance()}")
print(f"AWS GPU info: {get_aws_gpu_info()}")
```

### Model Loading Issues

**Issue**: Model not found
```bash
# Check model path
ls -la path/to/model/

# Verify model files exist
find path/to/model/ -name "*.bin" -o -name "*.safetensors" | head -5

# Download model if missing
./scripts/download_model.sh llama-2-7b ./models
```

**Issue**: Model format not supported
```python
# Check model format
from transformers import AutoTokenizer, AutoModelForCausalLM

# Try loading with transformers
tokenizer = AutoTokenizer.from_pretrained("path/to/model")
model = AutoModelForCausalLM.from_pretrained("path/to/model")
```

## Performance Issues

### Slow Inference

**Issue**: CPU inference is slow
```python
# Solution 1: Enable GPU
llama = LlamaGPU("path/to/model", prefer_gpu=True)

# Solution 2: Use batch processing
results = llama.batch_infer(inputs, batch_size=4)

# Solution 3: Optimize input length
# Shorter inputs generally process faster
```

**Issue**: GPU inference is slow
```bash
# Check GPU utilization
nvidia-smi -l 1

# Check for thermal throttling
nvidia-smi -q -d temperature

# Solution: Monitor and optimize
python scripts/monitor_resources.py --interval 0.5 --duration 60
```

### Benchmark Issues

**Issue**: Benchmark script fails
```bash
# Check script permissions
chmod +x scripts/benchmark.py

# Run with verbose output
python scripts/benchmark.py --model path/to/model --backend cpu -v

# Check for missing dependencies
pip install psutil matplotlib
```

## AWS-Specific Issues

### Instance Configuration

**Issue**: GPU not detected on AWS
```bash
# Check instance type
curl http://169.254.169.254/latest/meta-data/instance-type

# Verify GPU instance type (should be p3, p3dn, g4dn, g5, etc.)
# If not GPU instance, launch appropriate instance type

# Check GPU availability
nvidia-smi
```

**Issue**: AWS setup script fails
```bash
# Run setup script with debug
bash -x scripts/setup_aws.sh

# Manual setup steps:
sudo apt update
sudo apt install nvidia-driver-470
sudo apt install nvidia-cuda-toolkit
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Permission Issues

**Issue**: Permission denied errors
```bash
# Fix script permissions
chmod +x scripts/*.sh

# Run with sudo if needed
sudo ./scripts/setup_aws.sh

# Check file ownership
ls -la scripts/
```

## Testing Issues

### Test Failures

**Issue**: Tests fail due to missing GPU
```bash
# Run only CPU tests
python -m pytest tests/test_cpu_backend.py -v

# Run tests with mocking
python -m pytest tests/ -v --tb=short

# Check test environment
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

**Issue**: Import errors in tests
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Run tests from project root
cd /path/to/Llama-GPU
python -m pytest tests/ -v
```

## Debugging

### Enable Debug Logging

```python
import logging

# Set debug level
logging.basicConfig(level=logging.DEBUG)

# Check backend selection
llama = LlamaGPU("path/to/model", prefer_gpu=True)
info = llama.get_backend_info()
print(f"Backend info: {info}")
```

### Check System Resources

```bash
# CPU and memory
htop

# GPU resources
nvidia-smi -l 1

# Disk space
df -h

# Network connectivity (for AWS)
ping 8.8.8.8
```

### Common Error Messages

**`ImportError: No module named 'torch'`**
```bash
pip install torch torchvision torchaudio
```

**`RuntimeError: CUDA error: no kernel image is available for execution`**
```bash
# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**`OSError: [Errno 28] No space left on device`**
```bash
# Check disk space
df -h

# Clean up temporary files
rm -rf /tmp/*
```

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Run the test suite**: `python -m pytest tests/ -v`
3. **Check system requirements**: GPU drivers, CUDA/ROCm, Python version
4. **Review logs**: Check `logs/` directory for error messages
5. **Try minimal example**: Use the basic usage example from README

### Providing Debug Information

When reporting issues, include:

```bash
# System information
uname -a
python --version
pip list | grep torch

# GPU information
nvidia-smi  # or rocm-smi

# Test results
python -m pytest tests/ -v --tb=long

# Error logs
tail -50 logs/llama_gpu.log
```

### Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check `docs/` directory
- **Examples**: Review `examples/` directory
- **Tests**: Use test cases as usage examples 