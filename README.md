# Llama-GPU

A high-performance GPU-accelerated inference library for LLaMA models, supporting local computers and AWS GPU instances with automatic backend selection and optimization.

## Features

- **Multi-Backend Support**: CPU, CUDA (NVIDIA), and ROCm (AMD) backends
- **Automatic AWS Detection**: Optimizes for AWS GPU instances (p3, p3dn, g4dn, etc.)
- **Batch Inference**: Process multiple inputs efficiently
- **Streaming Inference**: Real-time token generation
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Comprehensive Testing**: 41 test cases covering all functionality

## Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/Llama-GPU.git
   cd Llama-GPU
   ```

2. **Set up the environment**:
   ```bash
   # For local development
   ./scripts/setup_local.sh
   
   # For AWS GPU instances
   ./scripts/setup_aws.sh
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Usage

```python
from llama_gpu import LlamaGPU

# Initialize with automatic backend selection
llama = LlamaGPU("path/to/your/model", prefer_gpu=True)

# Single inference
result = llama.infer("Hello, how are you?")
print(result)

# Batch inference
inputs = ["Hello", "How are you?", "Tell me a story"]
results = llama.batch_infer(inputs, batch_size=2)
print(results)

# Streaming inference
for token in llama.stream_infer("Once upon a time"):
    print(token, end="", flush=True)
```

### AWS GPU Instance Usage

The library automatically detects AWS GPU instances and optimizes accordingly:

```python
# Automatic AWS detection and optimization
llama = LlamaGPU("path/to/model", auto_detect_aws=True)

# Get backend information
info = llama.get_backend_info()
print(f"Backend: {info['backend_type']}")
print(f"AWS Instance: {info['aws_instance']}")
if info['aws_instance']:
    print(f"GPU Info: {info['aws_gpu_info']}")
```

## Project Structure

```
Llama-GPU/
├── src/                    # Core source code
│   ├── backend/           # Backend implementations (CPU, CUDA, ROCm)
│   ├── utils/             # Utility functions (AWS detection, logging)
│   └── llama_gpu.py       # Main interface
├── scripts/               # Setup and utility scripts
├── tests/                 # Comprehensive test suite
├── docs/                  # Documentation
├── examples/              # Usage examples
└── logs/                  # Log files
```

## Backend Selection

The library automatically selects the best available backend:

1. **AWS GPU Detection**: If running on AWS with GPU instances, optimizes for the specific GPU type
2. **Local GPU**: Prefers ROCm (AMD) or CUDA (NVIDIA) if available
3. **CPU Fallback**: Falls back to CPU if no GPU backends are available

## Performance Benchmarking

Run performance benchmarks to compare backends:

```bash
python scripts/benchmark.py --model path/to/model --backend all --output-format json
```

Available options:
- `--backend`: cpu, cuda, rocm, or all
- `--batch-size`: Batch size for testing
- `--output-format`: human, csv, or json

## Monitoring Resources

Monitor GPU and system resources during inference:

```bash
python scripts/monitor_resources.py --interval 1 --duration 60
```

## Troubleshooting

### Common Issues

1. **CUDA not available**:
   - Ensure NVIDIA drivers are installed
   - Check CUDA installation: `nvidia-smi`
   - Verify PyTorch CUDA support: `python -c "import torch; print(torch.cuda.is_available())"`

2. **ROCm not available**:
   - Ensure AMD GPU drivers are installed
   - Check ROCm installation: `rocm-smi`
   - Verify PyTorch ROCm support

3. **AWS detection not working**:
   - Ensure running on AWS EC2 instance
   - Check instance metadata service connectivity
   - Verify instance type has GPU support

4. **Memory issues**:
   - Reduce batch size
   - Use smaller model variants
   - Monitor memory usage with resource monitoring script

### Getting Help

- Check the [API Documentation](docs/api.md)
- Review [Usage Examples](docs/usage.md)
- Run tests: `python -m pytest tests/ -v`
- Check logs in the `logs/` directory

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_backend.py -v
python -m pytest tests/test_aws_detection.py -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built on top of PyTorch and Transformers
- Inspired by the LLaMA model architecture
- AWS GPU instance optimization based on real-world performance data
