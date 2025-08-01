# Usage Guide: Llama-GPU

## Quick Setup

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Llama-GPU.git
cd Llama-GPU

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Setup

**For Local Development:**
```bash
./scripts/setup_local.sh
```

**For AWS GPU Instances:**
```bash
./scripts/setup_aws.sh
```

### 3. Download Model

```bash
# Download a specific model
./scripts/download_model.sh llama-2-7b ./models

# Or manually download and place in models/ directory
```

## Basic Usage

### Simple Inference

```python
from llama_gpu import LlamaGPU

# Initialize with automatic backend selection
llama = LlamaGPU("path/to/your/model", prefer_gpu=True)

# Single inference
result = llama.infer("Hello, how are you?")
print(result)
```

### Batch Processing

```python
# Process multiple inputs efficiently
inputs = [
    "What is machine learning?",
    "Explain quantum computing",
    "Tell me about artificial intelligence"
]

# Process all inputs at once
results = llama.batch_infer(inputs)
for i, result in enumerate(results):
    print(f"Input {i+1}: {inputs[i]}")
    print(f"Output {i+1}: {result}\n")

# Process with custom batch size
results = llama.batch_infer(inputs, batch_size=2)
```

### Streaming Inference

```python
# Real-time token generation
print("Generating story: ", end="", flush=True)
for token in llama.stream_infer("Once upon a time in a magical forest"):
    print(token, end="", flush=True)
print()  # New line at the end
```

## Advanced Usage

### AWS GPU Instance Optimization

```python
# Automatic AWS detection and optimization
llama = LlamaGPU("path/to/model", auto_detect_aws=True)

# Get detailed backend information
info = llama.get_backend_info()
print(f"Backend Type: {info['backend_type']}")
print(f"Model Path: {info['model_path']}")
print(f"Prefer GPU: {info['prefer_gpu']}")
print(f"AWS Instance: {info['aws_instance']}")

if info['aws_instance']:
    print(f"AWS GPU Info: {info['aws_gpu_info']}")
```

### Custom Backend Selection

```python
# Force CPU backend
llama_cpu = LlamaGPU("path/to/model", prefer_gpu=False)

# Force GPU preference (will use CUDA or ROCm if available)
llama_gpu = LlamaGPU("path/to/model", prefer_gpu=True)

# Disable AWS auto-detection
llama_no_aws = LlamaGPU("path/to/model", auto_detect_aws=False)
```

### Error Handling

```python
from llama_gpu import LlamaGPU
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

try:
    llama = LlamaGPU("path/to/model", prefer_gpu=True)
    result = llama.infer("Test input")
except Exception as e:
    print(f"Error during inference: {e}")
    # Fallback to CPU
    llama = LlamaGPU("path/to/model", prefer_gpu=False)
    result = llama.infer("Test input")
```

## Performance Optimization

### Benchmarking

```bash
# Benchmark all backends
python scripts/benchmark.py --model path/to/model --backend all

# Benchmark specific backend with custom batch size
python scripts/benchmark.py --model path/to/model --backend cuda --batch-size 4

# Save results to JSON
python scripts/benchmark.py --model path/to/model --backend all --output-format json > results.json
```

### Resource Monitoring

```bash
# Monitor resources during inference
python scripts/monitor_resources.py --interval 1 --duration 60

# Monitor with custom output
python scripts/monitor_resources.py --interval 0.5 --duration 30 --output-format csv > monitoring.csv
```

## Command Line Usage

### Direct Script Execution

```bash
# Run inference example
python examples/inference_example.py --model path/to/model --input "Hello world"

# Run benchmark
python scripts/benchmark.py --help  # See all options
```

### Batch Processing from Command Line

```bash
# Process multiple files
for file in inputs/*.txt; do
    python examples/inference_example.py --model path/to/model --input-file "$file" --output-file "outputs/$(basename "$file")"
done
```

## AWS-Specific Usage

### Instance Types and Optimization

The library automatically optimizes for different AWS GPU instance types:

- **p3.2xlarge, p3.8xlarge, p3.16xlarge**: Tesla V100 GPUs
- **p3dn.24xlarge**: Tesla V100 GPUs with NVLink
- **g4dn.xlarge, g4dn.2xlarge, g4dn.4xlarge, g4dn.8xlarge, g4dn.16xlarge**: Tesla T4 GPUs
- **g5.xlarge, g5.2xlarge, g5.4xlarge, g5.8xlarge, g5.12xlarge, g5.16xlarge, g5.24xlarge, g5.48xlarge**: NVIDIA A10G GPUs

### AWS Setup Script

```bash
# Run AWS setup script
./scripts/setup_aws.sh

# This script will:
# 1. Install NVIDIA drivers
# 2. Install CUDA toolkit
# 3. Install PyTorch with CUDA support
# 4. Configure environment variables
# 5. Test GPU availability
```

## Troubleshooting

### Common Issues

**1. CUDA Not Available**
```bash
# Check NVIDIA drivers
nvidia-smi

# Check CUDA installation
nvcc --version

# Check PyTorch CUDA support
python -c "import torch; print(torch.cuda.is_available())"
```

**2. ROCm Not Available**
```bash
# Check AMD drivers
rocm-smi

# Check ROCm installation
rocminfo

# Check PyTorch ROCm support
python -c "import torch; print(torch.version.hip)"
```

**3. Memory Issues**
```python
# Reduce batch size
results = llama.batch_infer(inputs, batch_size=1)

# Use smaller model variants
# Consider using quantized models
```

**4. AWS Detection Issues**
```python
# Check if running on AWS
import requests
try:
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-type', timeout=1)
    print(f"Instance type: {response.text}")
except:
    print("Not running on AWS")
```

### Performance Tips

1. **Batch Size Optimization**: Start with batch_size=1 and increase until memory limits
2. **Model Quantization**: Use quantized models for better memory efficiency
3. **GPU Memory Management**: Monitor GPU memory usage during inference
4. **Input Length**: Consider input length impact on memory usage

### Debugging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Check backend selection
llama = LlamaGPU("path/to/model", prefer_gpu=True)
info = llama.get_backend_info()
print(f"Selected backend: {info}")
```

## Environment Setup & Dependency Management

### Python
- Install dependencies: `pip install -r requirements.txt`
- Recommended: use a virtual environment (`python -m venv .venv`)
- For GPU: ensure CUDA/ROCm drivers are installed

### Node.js
- Install dependencies: `npm install`
- Use scripts for linting, formatting, and pre-commit hooks

See `requirements.txt` and `package.json` for full dependency lists.

## Onboarding
- Clone repo, run setup scripts, install dependencies
- See CONTRIBUTING.md for contribution steps

## API Usage
- See docs/api.md for async endpoints and monitoring

## Monitoring
- Resource usage endpoints: /monitor/memory, /monitor/gpu
- Logs: logs/api_requests.log, logs/test_output.log

## Examples

See the `examples/` directory for complete working examples:

- `inference_example.py`: Basic inference examples
- Additional examples for specific use cases

## Next Steps

- Read the [API Documentation](api.md) for detailed method descriptions
- Check the [Benchmarks](benchmarks.md) for performance comparisons
- Review the [Project Plan](project-plan.md) for development roadmap
