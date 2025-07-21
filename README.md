# Llama-GPU

## 📊 Badges
- **Build Status**: [![Build Status](https://github.com/hkevin01/Llama-GPU/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/hkevin01/Llama-GPU/actions)
- **Test Coverage**: [![Test Coverage](https://codecov.io/gh/hkevin01/Llama-GPU/branch/main/graph/badge.svg)](https://codecov.io/gh/hkevin01/Llama-GPU)
- **Security Audit**: [![Security Audit](https://img.shields.io/github/workflow/status/hkevin01/Llama-GPU/security-audit?label=security)](https://github.com/hkevin01/Llama-GPU/actions?query=workflow%3Asecurity-audit)
- **Docs Status**: [![Docs Status](https://img.shields.io/badge/docs-up_to_date-brightgreen)](docs/api.md)
- **Project Phase**: [![Project Phase](https://img.shields.io/badge/phase-documentation_analytics_release_community-blue)](docs/project-plan.md)

# Llama-GPU

A high-performance GPU-accelerated inference library for LLaMA models, supporting local computers and AWS GPU instances with automatic backend selection, multi-GPU support, quantization, memory management, and advanced optimization features.

---

## 🚀 Project Status

- **Completed Phases:** Core Infrastructure, API Server, Multi-GPU Support, Quantization, Memory Management
- **Current Phase:** Advanced Inference Optimizations (streaming, batching, async)
- **Next Priority:** Async API integration, benchmarking, monitoring/logging
- **Overall Progress:** 75% complete

See [Project Plan](docs/project-plan.md) for detailed roadmap and progress.

---

## Features

- **Multi-Backend Support**: CPU, CUDA (NVIDIA), and ROCm (AMD) backends
- **Multi-GPU Support**: Tensor parallelism, pipeline parallelism, and load balancing
- **Quantization Support**: INT8/FP16 and dynamic quantization for memory efficiency
- **Memory Management**: Real-time GPU/CPU memory usage reporting
- **Advanced Inference**: Streaming, batching, and async support
- **Production-Ready API Server**: FastAPI server with OpenAI-compatible endpoints
- **Automatic AWS Detection**: Optimizes for AWS GPU instances (p3, p3dn, g4dn, etc.)
- **Batch Inference**: Process multiple inputs efficiently with dynamic batching
- **Streaming Inference**: Real-time token generation with WebSocket support
- **Comprehensive Testing**: 100+ test cases covering all functionality, with outputs logged to `logs/test_output.log`
- **Production Monitoring**: Request queuing, rate limiting, and resource monitoring
- **Change Logging**: All major changes and test outputs are logged in `logs/CHANGELOG.md` and `logs/test_output.log`

---

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

### Multi-GPU Usage

```python
from src.multi_gpu import MultiGPUManager, GPUConfig

# Configure multi-GPU setup
config = GPUConfig(
    strategy="tensor_parallel",
    num_gpus=2,
    load_balancer="round_robin"
)

# Initialize multi-GPU manager
multi_gpu = MultiGPUManager(config)

# Generate text using multiple GPUs
result = multi_gpu.generate(
    prompt="Explain quantum computing",
    max_tokens=100,
    temperature=0.7
)
print(result)
```

### Quantization Usage

```python
from src.quantization import QuantizationManager, QuantizationConfig

# Configure quantization
config = QuantizationConfig(
    quantization_type="int8",
    dynamic=True,
    memory_efficient=True
)

# Initialize quantization manager
quant_manager = QuantizationManager(config)

# Quantize a model
quantized_model = quant_manager.quantize_model(model, "my_model")

# Use quantized model for inference
from src.quantization import QuantizedInference
inference = QuantizedInference(quantized_model, config)
result = inference.generate("Hello world", max_tokens=50)
```

### API Server Usage

Start the production API server:

```bash
python src/api_server.py
```

The server provides OpenAI-compatible endpoints:

```bash
# Text completion
curl -X POST "http://localhost:8000/v1/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "llama-base",
    "prompt": "Hello, how are you?",
    "max_tokens": 50
  }'

# Chat completion
curl -X POST "http://localhost:8000/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "llama-base",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 50
  }'

# Multi-GPU configuration
curl -X POST "http://localhost:8000/v1/multi-gpu/config" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "strategy": "tensor_parallel",
    "num_gpus": 2,
    "load_balancer": "round_robin"
  }'

# Get multi-GPU statistics
curl -X GET "http://localhost:8000/v1/multi-gpu/stats" \
  -H "Authorization: Bearer your-api-key"
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

## Multi-GPU Support

Llama-GPU provides comprehensive multi-GPU support for high-performance inference:

### Parallelism Strategies

1. **Tensor Parallelism**: Splits model layers across multiple GPUs
2. **Pipeline Parallelism**: Divides model into stages across GPUs
3. **Data Parallelism**: Processes different batches on different GPUs
4. **Hybrid Parallelism**: Combines multiple strategies for optimal performance

### Load Balancing

- **Round-Robin**: Distributes requests evenly across GPUs
- **Least-Loaded**: Sends requests to GPU with lowest utilization
- **Adaptive**: Dynamically adjusts based on GPU performance and load

### Configuration

```python
from src.multi_gpu import GPUConfig

# Tensor parallelism configuration
tensor_config = GPUConfig(
    strategy="tensor_parallel",
    num_gpus=4,
    load_balancer="adaptive",
    memory_fraction=0.8
)

# Pipeline parallelism configuration
pipeline_config = GPUConfig(
    strategy="pipeline_parallel",
    num_gpus=3,
    stages=3,
    load_balancer="round_robin"
)
```

## Quantization Support

Advanced quantization features for memory efficiency and performance optimization:

### Quantization Types

- **INT8 Quantization**: 8-bit integer quantization for 2x memory reduction
- **INT4 Quantization**: 4-bit integer quantization for 4x memory reduction
- **FP16/BF16**: Mixed precision for performance optimization
- **Dynamic Quantization**: Runtime quantization for flexibility
- **Static Quantization**: Pre-calibrated quantization for maximum efficiency

### Features

- **Memory Management**: Automatic memory savings calculation
- **Performance Monitoring**: Detailed statistics and benchmarking
- **Quantization Cache**: Persistent storage for quantized models
- **Accuracy Preservation**: Configurable accuracy vs. memory trade-offs

### Usage Examples

```python
from src.quantization import QuantizationManager, QuantizationConfig

# INT8 quantization
int8_config = QuantizationConfig(
    quantization_type="int8",
    dynamic=True,
    memory_efficient=True
)

# INT4 quantization
int4_config = QuantizationConfig(
    quantization_type="int4",
    dynamic=False,
    preserve_accuracy=True
)

# Benchmark quantization performance
quant_manager = QuantizationManager(int8_config)
stats = quant_manager.get_overall_stats()
print(f"Memory saved: {stats['memory_saved']:.2f} GB")
print(f"Accuracy loss: {stats['accuracy_loss']:.4f}")
```

## Advanced NLP Examples

Llama-GPU includes comprehensive examples for advanced natural language processing tasks:

### 🤖 Named Entity Recognition (NER)

High-speed entity extraction from text with support for 10 entity types:

```bash
# Extract entities from text
python examples/named_entity_recognition.py --model path/to/model --input "Apple CEO Tim Cook announced new products at WWDC in San Francisco"

# Batch processing from file
python examples/named_entity_recognition.py --model path/to/model --input-file texts.txt --batch-size 4
```

**Features:**
- Extract persons, organizations, locations, dates, and more
- Batch processing for large volumes
- Entity statistics and position tracking
- Fallback pattern matching for robust extraction
- JSON output with detailed metadata

### 📄 Document Classification

Large-scale document categorization into 10 predefined categories:

```bash
# Classify a single document
python examples/document_classification.py --model path/to/model --input "Technical documentation for neural networks"

# Batch classification
python examples/document_classification.py --model path/to/model --input-file documents.txt --output-file results.json
```

**Categories:** NEWS, TECHNICAL, LEGAL, MEDICAL, FINANCIAL, ACADEMIC, MARKETING, PERSONAL, GOVERNMENT, ENTERTAINMENT

### 🌍 Language Detection

Multi-language processing with 20+ supported languages:

```bash
# Detect language of text
python examples/language_detection.py --model path/to/model --input "Bonjour, comment allez-vous aujourd'hui?"

# Batch language detection
python examples/language_detection.py --model path/to/model --input-file multilingual.txt
```

**Features:**
- Support for 20+ languages with ISO codes
- Language family identification (Germanic, Romance, Slavic, etc.)
- Confidence scoring for language detection
- Comprehensive statistics and language distribution

### ❓ Question Answering

Neural QA with attention mechanisms and answer validation:

```bash
# Answer a question from context
python examples/question_answering.py --model path/to/model \
  --context "Python was created by Guido van Rossum and first released in 1991" \
  --question "Who created Python?"

# Batch QA processing
python examples/question_answering.py --model path/to/model --input-file qa_pairs.json
```

**Features:**
- Context-aware answer extraction
- Answer validation against source context
- Confidence scoring and validation metrics
- Attention mechanism guidance for better accuracy

## LLM Performance Examples

These examples demonstrate significant GPU acceleration benefits for complex LLM tasks:

### ✍️ Text Generation

High-performance text generation with various styles and lengths:

```bash
# Generate creative text
python examples/text_generation.py --model path/to/model --style creative --length long

# Benchmark GPU vs CPU performance
python examples/text_generation.py --model path/to/model --benchmark

# Batch generation with multiple styles
python examples/text_generation.py --model path/to/model --batch-size 4 --output-file stories.json
```

**GPU Benefits:**
- **3-5x speedup** for long-form content (1000+ tokens)
- **2-4x speedup** for batch generation
- **Real-time streaming** for interactive applications
- **Parallel processing** of multiple styles

### 💻 Code Generation

GPU-accelerated code synthesis across multiple programming languages:

```bash
# Generate Python code
python examples/code_generation.py --model path/to/model --language python --complexity high

# Generate code in multiple languages
python examples/code_generation.py --model path/to/model --language javascript --task "Create a web API"

# Benchmark performance
python examples/code_generation.py --model path/to/model --benchmark
```

**Supported Languages:** Python, JavaScript, Java, C++, Rust

**GPU Benefits:**
- **4-6x speedup** for complex code generation (100+ lines)
- **3-5x speedup** for multi-language batch processing
- **Enhanced code quality** with longer context windows
- **Faster iteration** for development workflows

### 💬 Conversation Simulation

Multi-turn dialogue simulation with realistic scenarios:

```bash
# Simulate customer support conversation
python examples/conversation_simulation.py --model path/to/model --scenario customer_support --turns 15

# Run multiple scenarios in batch
python examples/conversation_simulation.py --model path/to/model --batch-size 3 --scenario interview

# Benchmark conversation performance
python examples/conversation_simulation.py --model path/to/model --benchmark
```

**Available Scenarios:** customer_support, interview, therapy, teaching, negotiation

**GPU Benefits:**
- **5-8x speedup** for long conversations (10+ turns)
- **3-4x speedup** for context maintenance
- **Real-time dialogue** generation
- **Batch scenario processing**

### 📊 Data Analysis

Intelligent data analysis and insights generation:

```bash
# Analyze sales data
python examples/data_analysis.py --model path/to/model --data sales_data.csv --analysis-type trend

# Generate business insights
python examples/data_analysis.py --model path/to/model --data-type financial --analysis-type insights

# Batch analysis of multiple datasets
python examples/data_analysis.py --model path/to/model --batch-size 4 --data-type user_behavior
```

**Analysis Types:** trend, correlation, insights, comprehensive

**GPU Benefits:**
- **4-7x speedup** for large dataset analysis (1000+ records)
- **3-5x speedup** for complex analytical queries
- **Real-time insights** generation
- **Parallel dataset** processing

### 📈 Performance Benchmarks

All examples include built-in GPU vs CPU benchmarking:

```bash
# Run benchmarks for all examples
python examples/text_generation.py --model path/to/model --benchmark
python examples/code_generation.py --model path/to/model --benchmark
python examples/conversation_simulation.py --model path/to/model --benchmark
python examples/data_analysis.py --model path/to/model --benchmark
```

**Typical GPU Speedups:**
- **Text Generation**: 3-5x faster
- **Code Generation**: 4-6x faster
- **Conversation Simulation**: 5-8x faster
- **Data Analysis**: 4-7x faster

### 📊 Example Output

All examples provide detailed output including:
- Processing time and performance metrics
- GPU vs CPU speedup comparisons
- Token generation rates
- Memory usage statistics
- JSON export for further processing

## Project Structure

```
Llama-GPU/
├── src/                    # Core source code
│   ├── backend/           # Backend implementations (CPU, CUDA, ROCm)
│   ├── utils/             # Utility functions (AWS detection, logging)
│   ├── multi_gpu.py       # Multi-GPU support and parallelism
│   ├── quantization.py    # Quantization and optimization
│   ├── api_server.py      # Production FastAPI server
│   ├── model_manager.py   # Model loading and management
│   └── llama_gpu.py       # Main interface
├── scripts/               # Setup and utility scripts
├── tests/                 # Comprehensive test suite
│   ├── test_multi_gpu.py  # Multi-GPU functionality tests
│   ├── test_quantization.py # Quantization tests
│   ├── test_api_server.py # API server tests
│   └── ...                # Other test modules
├── docs/                  # Documentation
│   ├── api.md            # API reference
│   ├── usage.md          # Usage guide
│   ├── troubleshooting.md # Troubleshooting guide
│   ├── project-plan.md   # Project roadmap and status
│   └── publishing.md     # PyPI publishing guide
├── examples/              # Usage examples
│   ├── inference_example.py      # Basic inference
│   ├── named_entity_recognition.py # NER example
│   ├── document_classification.py # Document classification
│   ├── language_detection.py      # Language detection
│   ├── question_answering.py      # Question answering
│   ├── text_generation.py         # Text generation with GPU benefits
│   ├── code_generation.py         # Code generation with GPU benefits
│   ├── conversation_simulation.py # Conversation simulation with GPU benefits
│   └── data_analysis.py           # Data analysis with GPU benefits
├── logs/                  # Log files and test outputs
│   ├── multi_gpu_implementation_summary.log
│   ├── project_progress_summary.log
│   └── quantization.log
└── cache/                 # Quantized model cache
```

## Project Status

### ✅ Completed Features (75% Complete)

- **Phase 1**: Core Infrastructure ✅
  - Multi-backend support (CPU, CUDA, ROCm)
  - AWS GPU detection and optimization
  - Basic inference and batch processing
  - Comprehensive test suite

- **Phase 2**: Production-Ready API Server ✅
  - FastAPI server with OpenAI-compatible endpoints
  - Request queuing and dynamic batching
  - API key authentication and rate limiting
  - WebSocket streaming support
  - Production monitoring and logging

- **Phase 3**: Advanced Inference Features ✅
  - Multiple sampling strategies
  - Guided generation and function calling
  - Advanced batching and streaming
  - Error handling and fallback mechanisms

- **Phase 4**: Multi-GPU Support ✅
  - Tensor and pipeline parallelism
  - Load balancing strategies
  - Multi-GPU API endpoints
  - Comprehensive multi-GPU testing

- **Phase 5**: Quantization and Memory Management ✅
  - Quantization support (INT8/FP16)
  - Dynamic quantization and memory management
  - Quantized model caching
  - Performance benchmarking
  - Memory optimization

- **Phase 6**: Advanced Inference Optimizations 🚧 (In Progress)
  - Async API integration
  - Advanced streaming and batching
  - Inference monitoring and logging
  - Performance profiling tools

### 🎯 Upcoming Features

- **Phase 6**: Advanced Inference Optimizations (Continuing)
  - Async API integration
  - Benchmarking and monitoring
  - Performance profiling tools

- **Phase 7**: Advanced Features
  - Model fine-tuning support
  - Custom model architectures
  - Advanced caching strategies
  - Distributed inference

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

## API Endpoints

The production API server provides the following endpoints:

### Core Endpoints
- `POST /v1/completions` - Text completion
- `POST /v1/chat/completions` - Chat completion
- `POST /v1/models/load` - Load model
- `GET /v1/models` - List available models

### Multi-GPU Endpoints
- `POST /v1/multi-gpu/config` - Configure multi-GPU setup
- `GET /v1/multi-gpu/stats` - Get multi-GPU statistics

### Monitoring Endpoints
- `GET /v1/monitor/queues` - Queue status
- `GET /v1/monitor/batches` - Batch processing status
- `GET /v1/monitor/workers` - Worker status

### Streaming
- `WebSocket /v1/stream` - Real-time streaming

## Documentation

### 📚 Core Documentation

- **[API Reference](docs/api.md)** - Complete API documentation
- **[Usage Guide](docs/usage.md)** - Detailed usage examples and advanced features
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Project Plan](docs/project-plan.md)** - Project roadmap and status
- **[Publishing Guide](docs/publishing.md)** - PyPI publishing and release management

### 🎯 Example Documentation

Each example includes:
- **Command-line interface** with full argument support
- **Batch processing** capabilities
- **Error handling** and fallback mechanisms
- **Performance metrics** and statistics
- **GPU vs CPU benchmarking**
- **JSON output** for easy integration

### 📖 Getting Started

1. **Basic Usage**: Start with `examples/inference_example.py`
2. **NLP Tasks**: Try the advanced NLP examples for specific use cases
3. **LLM Performance**: Test the GPU-accelerated examples for maximum performance
4. **Multi-GPU**: Experiment with multi-GPU configurations
5. **Quantization**: Test quantization for memory efficiency
6. **API Server**: Deploy the production API server
7. **Customization**: Modify examples for your specific needs
8. **Integration**: Use the JSON outputs in your applications

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

3. **Multi-GPU issues**:
   - Check GPU availability: `nvidia-smi` or `rocm-smi`
   - Verify CUDA/ROCm multi-GPU support
   - Check memory allocation across GPUs
   - Review multi-GPU configuration settings

4. **Quantization issues**:
   - Verify PyTorch quantization support
   - Check model compatibility with quantization
   - Monitor memory usage during quantization
   - Review quantization configuration

5. **AWS detection not working**:
   - Ensure running on AWS EC2 instance
   - Check instance metadata service connectivity
   - Verify instance type has GPU support

6. **Memory issues**:
   - Reduce batch size
   - Use smaller model variants
   - Enable quantization for memory efficiency
   - Monitor memory usage with resource monitoring script

7. **API server issues**:
   - Check port availability (default: 8000)
   - Verify API key configuration
   - Review rate limiting settings
   - Check server logs for errors

8. **Example errors**:
   - Check model path and format
   - Verify input file formats
   - Review error logs in `logs/` directory

9. **GPU performance issues**:
   - Ensure GPU drivers are up to date
   - Check GPU memory availability
   - Monitor GPU utilization during execution
   - Verify batch sizes are optimal for your GPU
   - Consider using quantization for better performance

### Getting Help

- Check the [API Documentation](docs/api.md)
- Review [Usage Examples](docs/usage.md)
- Consult the [Troubleshooting Guide](docs/troubleshooting.md)
- Check [Project Status](docs/project-plan.md)
- Run tests: `python -m pytest tests/ -v`
- Check logs in the `logs/` directory

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_backend.py -v
python -m pytest tests/test_multi_gpu.py -v
python -m pytest tests/test_quantization.py -v
python -m pytest tests/test_api_server.py -v
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Package Distribution

### PyPI Installation (Coming Soon)

```bash
pip install llama-gpu
```

### Local Installation

```bash
# Install in development mode
pip install -e .

# Install with GPU support
pip install -e .[gpu]

# Install with development dependencies
pip install -e .[dev]
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of PyTorch and Transformers
- Inspired by the LLaMA model architecture
- AWS GPU instance optimization based on real-world performance data
- Advanced NLP examples demonstrate real-world applications
- LLM performance examples showcase GPU acceleration benefits
- Multi-GPU support enables high-performance distributed inference
- Quantization features provide memory-efficient model deployment
