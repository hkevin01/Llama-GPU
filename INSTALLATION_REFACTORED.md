# Installation Guide

## Document Information

- **Project**: LLaMA GPU
- **Version**: 1.0.0
- **Last Updated**: August 1, 2025
- **Compatibility**: Linux, Windows, macOS

## Table of Contents

- [1. System Requirements](#1-system-requirements)
- [2. Pre-Installation Setup](#2-pre-installation-setup)
- [3. Installation Methods](#3-installation-methods)
- [4. Configuration](#4-configuration)
- [5. Verification](#5-verification)
- [6. Troubleshooting](#6-troubleshooting)
- [7. Advanced Installation](#7-advanced-installation)

## 1. System Requirements

### 1.1 Hardware Requirements

#### Minimum Requirements
- **CPU**: 4 cores (Intel Core i5 / AMD Ryzen 5 equivalent)
- **RAM**: 8GB system memory
- **Storage**: 10GB available disk space
- **GPU**: Optional (NVIDIA GTX 1060 6GB / AMD RX 580 8GB or better)
- **Network**: Stable internet connection for model downloads

#### Recommended Requirements
- **CPU**: 8+ cores (Intel Core i7/i9 / AMD Ryzen 7/9)
- **RAM**: 32GB+ system memory
- **Storage**: 50GB+ SSD storage
- **GPU**: NVIDIA RTX 3080/4080 (12GB+) or AMD MI100/MI200 series
- **Network**: High-speed internet (100+ Mbps) for faster downloads

#### Production Requirements
- **CPU**: 16+ cores (Intel Xeon / AMD EPYC)
- **RAM**: 64GB+ system memory
- **Storage**: 100GB+ NVMe SSD
- **GPU**: NVIDIA A100 (40/80GB) or multiple RTX 4090s
- **Network**: Gigabit ethernet with low latency

### 1.2 Software Requirements

#### Operating Systems
- **Linux**: Ubuntu 20.04+, CentOS 8+, RHEL 8+, Debian 11+
- **Windows**: Windows 10/11 (64-bit) - Limited support
- **macOS**: macOS 11+ (CPU inference only)

#### Python Environment
- **Python**: 3.8, 3.9, 3.10, or 3.11 (recommended: 3.10)
- **pip**: Latest version (>= 21.0)
- **virtualenv** or **conda**: For environment isolation

#### GPU Drivers & Libraries

**For NVIDIA GPUs:**
- **NVIDIA Driver**: 525.x or newer
- **CUDA Toolkit**: 11.8 or 12.x
- **cuDNN**: 8.6+ (usually included with PyTorch)

**For AMD GPUs:**
- **ROCm**: 5.4.0 or newer
- **AMD GPU Driver**: Latest AMDGPU driver

## 2. Pre-Installation Setup

### 2.1 Environment Preparation

#### Create Virtual Environment

**Using conda (recommended):**
```bash
# Install Miniconda if not already installed
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create new environment
conda create -n llama-gpu python=3.10
conda activate llama-gpu
```

**Using venv:**
```bash
python3.10 -m venv llama-gpu-env
source llama-gpu-env/bin/activate  # Linux/macOS
# OR
llama-gpu-env\Scripts\activate     # Windows
```

#### Update System Packages

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git wget curl build-essential
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum groupinstall -y "Development Tools"
sudo yum install -y git wget curl
```

**macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install git wget curl
```

### 2.2 GPU Driver Installation

#### NVIDIA GPU Setup

**Install NVIDIA Driver:**
```bash
# Ubuntu
sudo apt install -y nvidia-driver-535
sudo reboot

# Verify installation
nvidia-smi
```

**Install CUDA Toolkit:**
```bash
# Ubuntu 20.04/22.04
wget https://developer.download.nvidia.com/compute/cuda/12.3.0/local_installers/cuda_12.3.0_545.23.06_linux.run
sudo sh cuda_12.3.0_545.23.06_linux.run

# Add to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

#### AMD GPU Setup

**Install ROCm:**
```bash
# Ubuntu 20.04/22.04
wget -q -O - https://repo.radeon.com/rocm/rocm.gpg.key | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/debian/ ubuntu main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update
sudo apt install -y rocm-dkms rocm-libs

# Add user to render group
sudo usermod -a -G render,video $USER
sudo reboot

# Verify installation
rocm-smi
```

### 2.3 Verify GPU Installation

**Check NVIDIA GPU:**
```bash
nvidia-smi
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

**Check AMD GPU:**
```bash
rocm-smi
python -c "import torch; print(f'ROCm available: {torch.cuda.is_available()}')"
```

## 3. Installation Methods

### 3.1 Method 1: Quick Install (Recommended)

**Clone and Install:**
```bash
# Clone repository
git clone https://github.com/your-username/Llama-GPU.git
cd Llama-GPU

# Run automated installation script
chmod +x install.sh
./install.sh
```

**Installation Script Options:**
```bash
# Full installation with all features
./install.sh --full

# CPU-only installation
./install.sh --cpu-only

# Development installation
./install.sh --dev

# Custom backend
./install.sh --backend=cuda  # or rocm, cpu
```

### 3.2 Method 2: Manual Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/Llama-GPU.git
cd Llama-GPU
```

#### Step 2: Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# OR for ROCm support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.4.2

# OR for CPU only
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### Step 3: Install LLaMA GPU
```bash
# Development installation
pip install -e .

# OR production installation
pip install .
```

### 3.3 Method 3: Docker Installation

#### Prerequisites
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install NVIDIA Container Toolkit (for GPU support)
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

#### Build Docker Image
```bash
# Clone repository
git clone https://github.com/your-username/Llama-GPU.git
cd Llama-GPU

# Build Docker image
docker build -t llama-gpu:latest .

# OR build with specific backend
docker build --build-arg BACKEND=cuda -t llama-gpu:cuda .
```

#### Run Docker Container
```bash
# Run with GPU support
docker run --gpus all -p 5000:5000 -v $(pwd)/models:/app/models llama-gpu:latest

# Run CPU only
docker run -p 5000:5000 -v $(pwd)/models:/app/models llama-gpu:latest

# Run with custom configuration
docker run --gpus all -p 5000:5000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/config:/app/config \
  -e LLAMA_BACKEND=cuda \
  -e LLAMA_MAX_MEMORY=80% \
  llama-gpu:latest
```

### 3.4 Method 4: Package Manager Installation

#### Using pip (when published)
```bash
# Install from PyPI
pip install llama-gpu

# Install with GPU support
pip install llama-gpu[cuda]  # for NVIDIA
pip install llama-gpu[rocm]  # for AMD
pip install llama-gpu[all]   # for all backends

# Install development version
pip install llama-gpu[dev]
```

#### Using conda (when published)
```bash
# Install from conda-forge
conda install -c conda-forge llama-gpu

# Install with specific backend
conda install -c conda-forge llama-gpu-cuda
conda install -c conda-forge llama-gpu-rocm
```

## 4. Configuration

### 4.1 Initial Configuration

#### Create Configuration File
```bash
# Copy default configuration
cp config/config.example.yaml config/config.yaml

# Edit configuration
nano config/config.yaml
```

#### Basic Configuration
```yaml
# config/config.yaml
server:
  host: "0.0.0.0"
  port: 5000
  debug: false

inference:
  backend: "auto"  # auto, cuda, rocm, cpu
  max_memory: "80%"
  default_model: "llama2-7b"
  max_batch_size: 32

models:
  cache_dir: "./models"
  download_source: "huggingface"
  quantization: "fp16"

plugins:
  enabled: true
  directory: "./plugins"
  auto_load: ["core"]

monitoring:
  enabled: true
  metrics_retention: "7d"
  log_level: "INFO"

security:
  api_keys_enabled: false
  cors_enabled: true
  rate_limiting: true
```

### 4.2 Environment Variables

Create `.env` file for environment-specific settings:
```bash
# .env
LLAMA_CONFIG_PATH=./config/config.yaml
LLAMA_BACKEND=cuda
LLAMA_MAX_MEMORY=80%
LLAMA_MODEL_CACHE=./models
LLAMA_PLUGIN_PATH=./plugins
LLAMA_LOG_LEVEL=INFO
LLAMA_API_KEY=your_secret_api_key_here
CUDA_VISIBLE_DEVICES=0,1
HF_HOME=./cache/huggingface
```

### 4.3 Model Download

#### Automatic Model Download
```bash
# Download default models
python -m llama_gpu.tools.download_models

# Download specific model
python -m llama_gpu.tools.download_models --model llama2-7b-chat

# List available models
python -m llama_gpu.tools.download_models --list
```

#### Manual Model Setup
```bash
# Create models directory
mkdir -p models

# Download from HuggingFace
git lfs install
git clone https://huggingface.co/meta-llama/Llama-2-7b-chat-hf models/llama2-7b-chat

# OR use HuggingFace CLI
pip install huggingface_hub
huggingface-cli download meta-llama/Llama-2-7b-chat-hf --local-dir models/llama2-7b-chat
```

### 4.4 Plugin Configuration

#### Install Built-in Plugins
```bash
# Initialize plugin directory
python -m llama_gpu.tools.init_plugins

# Install specific plugins
python -m llama_gpu.tools.install_plugin --name model_adapter
python -m llama_gpu.tools.install_plugin --name response_filter

# List available plugins
python -m llama_gpu.tools.list_plugins
```

## 5. Verification

### 5.1 Installation Verification

#### Run System Check
```bash
# Comprehensive system check
python -m llama_gpu.tools.system_check

# Basic functionality test
python -m llama_gpu.tools.test_installation

# GPU compatibility check
python -m llama_gpu.tools.gpu_check
```

#### Manual Verification
```python
# test_installation.py
import llama_gpu
from llama_gpu import LlamaGPU, get_system_info

# Check installation
print(f"LLaMA GPU version: {llama_gpu.__version__}")

# Check system capabilities
system_info = get_system_info()
print(f"Available backends: {system_info['backends']}")
print(f"GPU devices: {system_info['gpu_devices']}")

# Test basic functionality
llama = LlamaGPU(backend='auto')
result = llama.infer("Hello, world!")
print(f"Test result: {result}")
```

### 5.2 Web Dashboard Test

#### Start Dashboard
```bash
# Start development server
python -m llama_gpu.dashboard --debug

# Start production server
python -m llama_gpu.dashboard --host 0.0.0.0 --port 5000

# Start with specific configuration
python -m llama_gpu.dashboard --config config/config.yaml
```

#### Access Dashboard
1. Open browser to `http://localhost:5000`
2. Check system status page
3. Verify GPU metrics display
4. Test plugin management interface

### 5.3 API Testing

#### Test REST API
```bash
# Start API server
python -m llama_gpu.api

# Test in another terminal
curl -X POST "http://localhost:5000/api/v1/infer" \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello, world!", "max_tokens": 50}'
```

#### Python API Test
```python
# test_api.py
import requests

# Test inference endpoint
response = requests.post(
    'http://localhost:5000/api/v1/infer',
    json={
        'text': 'Explain artificial intelligence in one sentence.',
        'max_tokens': 100
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Success: {result['result']['generated_text']}")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

## 6. Troubleshooting

### 6.1 Common Installation Issues

#### Python Version Issues
```bash
# Check Python version
python --version

# If using wrong version, create new environment
conda create -n llama-gpu python=3.10
conda activate llama-gpu
```

#### CUDA Installation Issues
```bash
# Check CUDA installation
nvidia-smi
nvcc --version

# If CUDA not found, add to PATH
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Memory Issues
```bash
# Check available memory
free -h
nvidia-smi

# Reduce memory usage in config
echo "inference:
  max_memory: '60%'
  max_batch_size: 8" >> config/config.yaml
```

#### Permission Issues
```bash
# Fix directory permissions
sudo chown -R $USER:$USER ./models ./cache ./logs

# Add user to GPU groups
sudo usermod -a -G render,video $USER
sudo reboot
```

### 6.2 Runtime Issues

#### Model Loading Failures
```bash
# Check model files
ls -la models/
du -sh models/*

# Re-download corrupted models
rm -rf models/llama2-7b
python -m llama_gpu.tools.download_models --model llama2-7b --force
```

#### GPU Out of Memory
```yaml
# Reduce memory usage in config.yaml
inference:
  max_memory: "70%"
  quantization: "int8"  # Use 8-bit quantization
  gradient_checkpointing: true
```

#### Plugin Loading Issues
```bash
# Check plugin dependencies
python -m llama_gpu.tools.check_plugins

# Reinstall plugins
python -m llama_gpu.tools.reinstall_plugins

# Disable problematic plugins
echo "plugins:
  auto_load: []
  enabled: false" >> config/config.yaml
```

### 6.3 Performance Issues

#### Slow Inference
```yaml
# Optimize configuration
inference:
  backend: "cuda"  # Force specific backend
  quantization: "fp16"
  torch_compile: true
  batch_size_optimization: true
```

#### High Memory Usage
```bash
# Monitor memory usage
python -m llama_gpu.tools.monitor --memory

# Clear cache periodically
python -c "
import torch
torch.cuda.empty_cache()
import gc
gc.collect()
"
```

### 6.4 Network Issues

#### Model Download Failures
```bash
# Use alternative download method
export HF_ENDPOINT="https://hf-mirror.com"
python -m llama_gpu.tools.download_models --model llama2-7b

# Download manually and place in models/
wget https://huggingface.co/meta-llama/Llama-2-7b-chat-hf/resolve/main/pytorch_model.bin
```

#### Dashboard Connection Issues
```bash
# Check firewall settings
sudo ufw allow 5000

# Bind to all interfaces
python -m llama_gpu.dashboard --host 0.0.0.0

# Check if port is in use
netstat -tulnp | grep :5000
```

## 7. Advanced Installation

### 7.1 Multi-GPU Setup

#### Configure Multiple GPUs
```yaml
# config/config.yaml
inference:
  backend: "cuda"
  gpu_devices: [0, 1, 2, 3]  # Use specific GPUs
  parallel_strategy: "tensor_parallel"  # or "pipeline_parallel"
  load_balancing: true
```

#### CUDA Environment for Multi-GPU
```bash
# Set visible devices
export CUDA_VISIBLE_DEVICES=0,1,2,3

# Check GPU topology
nvidia-smi topo -m

# Install additional dependencies for multi-GPU
pip install accelerate deepspeed
```

### 7.2 Distributed Setup

#### Configure Distributed Inference
```yaml
# config/distributed.yaml
distributed:
  enabled: true
  backend: "nccl"
  world_size: 4
  rank: 0
  master_addr: "192.168.1.100"
  master_port: 29500
```

#### Launch Distributed Workers
```bash
# Launch on each node
torchrun --nproc_per_node=2 --nnodes=2 --node_rank=0 \
         --master_addr=192.168.1.100 --master_port=29500 \
         -m llama_gpu.distributed.launch --config config/distributed.yaml
```

### 7.3 Production Deployment

#### systemd Service Configuration
```bash
# Create service file
sudo nano /etc/systemd/system/llama-gpu.service
```

```ini
[Unit]
Description=LLaMA GPU Inference Server
After=network.target

[Service]
Type=simple
User=llama-gpu
Group=llama-gpu
WorkingDirectory=/opt/llama-gpu
Environment=PATH=/opt/llama-gpu/venv/bin
ExecStart=/opt/llama-gpu/venv/bin/python -m llama_gpu.api --config /opt/llama-gpu/config/production.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable llama-gpu
sudo systemctl start llama-gpu
sudo systemctl status llama-gpu
```

#### Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/llama-gpu
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 7.4 Monitoring and Logging

#### Prometheus Integration
```yaml
# config/monitoring.yaml
monitoring:
  prometheus:
    enabled: true
    port: 9090
    metrics_path: "/metrics"

  grafana:
    enabled: true
    dashboard_url: "http://localhost:3000"
```

#### Log Configuration
```yaml
# config/logging.yaml
logging:
  version: 1
  formatters:
    standard:
      format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  handlers:
    file:
      class: logging.handlers.RotatingFileHandler
      filename: logs/llama-gpu.log
      maxBytes: 10485760  # 10MB
      backupCount: 5
      formatter: standard
  root:
    level: INFO
    handlers: [file]
```

---

**Installation Status**: ✅ Complete
**Tested Platforms**: Ubuntu 22.04, CentOS 8, Windows 11, macOS 12
**Last Updated**: August 1, 2025
**Support**: See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for additional help
