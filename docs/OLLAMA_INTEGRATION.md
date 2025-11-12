# Ollama Integration Guide

## Overview

Llama-GPU now features complete integration with Ollama, providing:
- **Multi-backend support**: Switch between LlamaGPU and Ollama backends
- **Unified API**: OpenAI-compatible REST API supporting both backends
- **CLI tools**: Command-line interface for quick interactions
- **GUI launchers**: Desktop widgets and system tray integration
- **Model management**: Easy model installation and switching

## 🚀 Quick Start

### 1. Check Status

```bash
# Check what's running
python3 tools/llm_cli.py --status
```

### 2. List Available Models

```bash
# List all models
python3 tools/llm_cli.py --list
```

### 3. Chat with AI

```bash
# Interactive mode
python3 tools/llm_cli.py -i

# One-shot query
python3 tools/llm_cli.py "What is the capital of France?"

# Specify model
python3 tools/llm_cli.py -m "deepseek-r1:7b" "Explain quantum computing"
```

## 📦 Architecture

### Backend Structure

```
Llama-GPU/
├── src/
│   ├── backends/
│   │   └── ollama/
│   │       ├── __init__.py
│   │       ├── ollama_client.py      # Ollama API client
│   │       └── ollama_backend.py     # Backend adapter
│   ├── unified_api_server.py         # Multi-backend API server
│   └── llama_gpu.py                  # Original LlamaGPU engine
├── tools/
│   ├── llm_cli.py                    # Unified CLI tool
│   └── gui/
│       ├── llm_launcher_gui.py       # GTK launcher window
│       ├── floating_llm_button.py    # Floating AI button
│       └── simple_llm_tray.py        # System tray icon
└── scripts/
    └── setup_local_llm.sh            # Setup script
```

### Communication Flow

```
┌─────────────────┐
│   User Input    │
└────────┬────────┘
         │
    ┌────▼────────────────┐
    │  CLI / GUI / API    │
    └────┬────────────────┘
         │
    ┌────▼───────────────────────┐
    │  Unified API Server        │
    │  (Multi-backend routing)   │
    └────┬───────────────┬───────┘
         │               │
    ┌────▼──────┐   ┌───▼──────────┐
    │  Ollama   │   │  LlamaGPU    │
    │  Backend  │   │  Backend     │
    └───────────┘   └──────────────┘
```

## 🔧 API Endpoints

### Unified API Server

Start the unified server:

```bash
python3 -m src.unified_api_server
```

#### Health & Status

```bash
# Health check
curl http://localhost:8000/healthz

# Liveness with backend info
curl http://localhost:8000/livez

# List backends
curl http://localhost:8000/v1/backends

# List all models
curl http://localhost:8000/v1/models
```

#### Completions

```bash
# Text completion (auto backend)
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Once upon a time",
    "max_tokens": 100
  }'

# Specify Ollama backend and model
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain AI in simple terms",
    "model": "phi4-mini:3.8b",
    "backend": "ollama",
    "max_tokens": 200,
    "temperature": 0.7
  }'
```

#### Chat Completions

```bash
# Chat with conversation history
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! Who are you?"}
    ],
    "model": "phi4-mini:3.8b",
    "backend": "ollama"
  }'
```

#### Backend Switching

```bash
# Switch active backend
curl -X POST "http://localhost:8000/v1/backend/switch?backend=ollama"
```

## 🖥️ CLI Usage

### Basic Commands

```bash
# Interactive chat
python3 tools/llm_cli.py -i

# Single query
python3 tools/llm_cli.py "Tell me a joke"

# List models
python3 tools/llm_cli.py --list

# System status
python3 tools/llm_cli.py --status
```

### Advanced Options

```bash
# Use specific model
python3 tools/llm_cli.py -m "deepseek-r1:7b" "Explain neural networks"

# Use specific backend
python3 tools/llm_cli.py -b ollama "What is machine learning?"

# Custom API URL
python3 tools/llm_cli.py --api-url http://localhost:8000 "Hello"
```

### Interactive Mode Commands

Within interactive mode:
- `/help` - Show available commands
- `/models` - List available models
- `/status` - Show system status
- `/quit` - Exit

## 🎨 GUI Tools

### 1. Floating AI Button

Always-visible AI button that stays on top:

```bash
python3 tools/gui/floating_llm_button.py
```

Features:
- Drag to reposition
- Click for menu with options
- Opens web interface or terminal chat
- Shows status information

### 2. LLM Launcher Window

Full-featured launcher window:

```bash
python3 tools/gui/llm_launcher_gui.py
```

Features:
- Web interface button
- Terminal chat launcher
- Status checker
- Minimize/hide option

### 3. System Tray Icon

Minimal system tray integration:

```bash
python3 tools/gui/simple_llm_tray.py
```

Features:
- Lives in system tray
- Quick access menu
- Unobtrusive design

## 🔌 Python API Usage

### Using Ollama Backend Directly

```python
from src.backends.ollama import OllamaClient, OllamaBackend

# Initialize client
client = OllamaClient()

# List models
models = client.list_models()
print(f"Available models: {[m['name'] for m in models]}")

# Generate text
response = client.generate(
    model="phi4-mini:3.8b",
    prompt="What is Python?",
    max_tokens=200
)
print(response)

# Streaming generation
for chunk in client.generate(
    model="phi4-mini:3.8b",
    prompt="Tell me a story",
    stream=True
):
    print(chunk, end="", flush=True)

# Chat with history
messages = [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help you?"},
    {"role": "user", "content": "Tell me about AI"}
]

response = client.chat(
    model="phi4-mini:3.8b",
    messages=messages
)
print(response)
```

### Using Backend Adapter

```python
from src.backends.ollama import OllamaBackend

# Initialize backend
backend = OllamaBackend(default_model="phi4-mini:3.8b")
backend.initialize()

# Check availability
if backend.is_available():
    # Simple inference
    result = backend.infer("What is machine learning?")
    print(result)
    
    # Chat
    messages = [{"role": "user", "content": "Hello!"}]
    response = backend.chat(messages)
    print(response)
    
    # Get backend info
    info = backend.get_device_info()
    print(info)
```

## 🛠️ Configuration

### Environment Variables

```bash
# API Server Configuration
export HOST=0.0.0.0
export PORT=8000
export BACKEND=ollama              # auto, ollama, or llama-gpu
export ALLOWED_ORIGINS=*

# Optional API Key Protection
export REQUIRE_API_KEY=true
export API_KEY=your-secret-key
```

### Ollama Configuration

```bash
# Ollama service URL (default: http://localhost:11434)
export OLLAMA_HOST=http://localhost:11434
```

## 📊 Available Models

### Currently Installed (Your System)

- **phi4-mini:3.8b** (2.5 GB) - Fast, efficient model
- **deepseek-r1:7b** (4.7 GB) - Reasoning-focused model

### Installing Additional Models

```bash
# Via Ollama CLI
ollama pull llama2:7b
ollama pull mistral:7b
ollama pull codellama:7b

# Via Python
from src.backends.ollama import OllamaClient
client = OllamaClient()
client.pull_model("llama2:7b")
```

## 🧪 Testing

### Test Ollama Integration

```python
python3 -c "
from src.backends.ollama import OllamaClient

client = OllamaClient()
print('Ollama available:', client.is_available())
print('Models:', [m['name'] for m in client.list_models()])

response = client.generate(
    model='phi4-mini:3.8b',
    prompt='Say hello!'
)
print('Response:', response)
"
```

### Test Unified API

```bash
# Start server in one terminal
python3 -m src.unified_api_server

# Test in another terminal
curl http://localhost:8000/livez
curl http://localhost:8000/v1/backends
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "backend": "ollama"}'
```

## 🐛 Troubleshooting

### Ollama Not Available

```bash
# Check if Ollama is running
systemctl status ollama

# Or check process
ps aux | grep ollama

# Start Ollama
ollama serve
```

### No Models Found

```bash
# List installed models
ollama list

# Pull a model
ollama pull phi4-mini:3.8b
```

### API Connection Issues

```bash
# Check if API is running
curl http://localhost:8000/healthz

# Check Ollama API
curl http://localhost:11434/api/tags
```

### Python Import Errors

```bash
# Install dependencies
pip install requests fastapi uvicorn

# Verify Python path
python3 -c "import sys; print(sys.path)"
```

## 🎯 Use Cases

### 1. Quick Terminal AI Assistant

```bash
# Add alias to ~/.bashrc
alias ai='python3 /home/kevin/Projects/Llama-GPU/tools/llm_cli.py'

# Then use anywhere
ai "How do I grep for patterns?"
ai -i  # Interactive mode
```

### 2. Desktop AI Companion

```bash
# Auto-start on login (add to startup applications)
python3 /home/kevin/Projects/Llama-GPU/tools/gui/floating_llm_button.py
```

### 3. Development API

```python
# In your application
import requests

response = requests.post(
    "http://localhost:8000/v1/completions",
    json={
        "prompt": "Generate a Python function to sort a list",
        "model": "phi4-mini:3.8b",
        "backend": "ollama"
    }
)
print(response.json()["choices"][0]["text"])
```

## 📚 Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Open WebUI](http://localhost:8080) - Your running web interface
- [LlamaGPU Project](../README.md) - Main project documentation

## 🤝 Contributing

Found a bug or have a feature request? Please open an issue or submit a pull request!

---

**Last Updated**: November 11, 2025
**Version**: 0.2.0
