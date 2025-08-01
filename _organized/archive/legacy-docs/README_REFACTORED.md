# LLaMA GPU

> A high-performance GPU-accelerated inference library for LLaMA models with automatic backend selection, multi-GPU support, and web-based management interface.

[![Build Status](https://github.com/hkevin01/Llama-GPU/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/hkevin01/Llama-GPU/actions)
[![Test Coverage](https://codecov.io/gh/hkevin01/Llama-GPU/branch/main/graph/badge.svg)](https://codecov.io/gh/hkevin01/Llama-GPU)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue)](https://python.org)

## 🚀 Features

- **🔄 Multi-Backend Support**: Automatic selection between CPU, CUDA (NVIDIA), and ROCm (AMD)
- **⚡ Multi-GPU Acceleration**: Tensor parallelism, pipeline parallelism, and intelligent load balancing
- **🎛️ Web Dashboard**: Professional web interface for system monitoring and plugin management
- **📊 Real-time Monitoring**: Live performance metrics, resource usage, and system health
- **🔌 Plugin Architecture**: Dynamic plugin loading with comprehensive management tools
- **☁️ AWS Optimization**: Automatic detection and optimization for AWS GPU instances
- **📈 Quantization Support**: INT8/FP16 quantization for memory efficiency
- **🌊 Streaming Inference**: Real-time token generation with WebSocket support
- **📦 Batch Processing**: Efficient batch inference with dynamic batching
- **🔧 Production Ready**: FastAPI server with OpenAI-compatible endpoints

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Web Dashboard](#web-dashboard)
- [API Reference](#api-reference)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- CUDA 11.8+ (for NVIDIA GPU support)
- ROCm 5.0+ (for AMD GPU support)

### Installation

```bash
# Clone the repository
git clone https://github.com/hkevin01/Llama-GPU.git
cd Llama-GPU

# Set up environment (choose one)
./scripts/setup_local.sh    # For local development
./scripts/setup_aws.sh      # For AWS GPU instances

# Install dependencies
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

# Streaming inference
for token in llama.stream_infer("Once upon a time"):
    print(token, end="", flush=True)
```

## 🎛️ Web Dashboard

Start the web dashboard for visual management:

```bash
# Start the dashboard
python start_dashboard.py

# Access at http://localhost:5000
```

**Dashboard Features:**
- 📊 Real-time system monitoring with interactive charts
- 🔌 Plugin management with load/unload capabilities
- 📈 Performance benchmarking and metrics export
- 🖥️ System resource monitoring (GPU, CPU, Memory)
- 📱 Responsive design for desktop and mobile

## 🔧 API Server

Start the production API server:

```bash
# Start FastAPI server
python -m src.api_server

# API available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

**Endpoints:**
- `POST /infer` - Single inference
- `POST /batch_infer` - Batch processing
- `POST /stream_infer` - Streaming inference
- `GET /monitor/memory` - Memory usage
- `GET /monitor/gpu` - GPU status

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](INSTALLATION.md) | Detailed setup and deployment instructions |
| [API Reference](API.md) | Complete API documentation |
| [Requirements](REQUIREMENTS.md) | Functional and non-functional requirements |
| [System Design](DESIGN.md) | Architecture and design decisions |
| [Testing Guide](TESTING.md) | Testing strategies and procedures |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions |
| [Contributing](CONTRIBUTING.md) | Contribution guidelines |
| [Changelog](CHANGELOG.md) | Version history and changes |

## 🏗️ Project Structure

```
LLaMA-GPU/
├── src/                    # Core source code
│   ├── backend/           # Backend implementations
│   ├── utils/             # Utility modules
│   ├── dashboard.py       # Web dashboard
│   └── api_server.py      # FastAPI server
├── tests/                 # Test suite (100+ tests)
├── docs/                  # Documentation
├── scripts/               # Setup and utility scripts
├── examples/              # Usage examples
└── logs/                  # Application logs
```

## 📊 Project Status

- **Build Status**: ✅ All tests passing (100+ test cases)
- **Current Phase**: Production ready with GUI dashboard
- **Test Coverage**: 90%+ coverage across all modules
- **Documentation**: Complete with examples and troubleshooting

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 Check the [Documentation](docs/)
- 🐛 Report issues on [GitHub Issues](https://github.com/hkevin01/Llama-GPU/issues)
- 💬 Join discussions on [GitHub Discussions](https://github.com/hkevin01/Llama-GPU/discussions)
- 📧 Contact: [maintainer@example.com](mailto:maintainer@example.com)

## 🙏 Acknowledgments

- LLaMA model architecture by Meta AI
- PyTorch and Transformers libraries
- Community contributors and testers

---

**⭐ Star this repository if you find it useful!**
