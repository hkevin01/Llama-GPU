# LLM Backend Setup Instructions

The chat interface can connect to different LLM backends. Here's how to set them up:

## 🚀 Quick Start (Mock Server)

For immediate testing with realistic responses:

```bash
# In the llama-gui directory, run:
npm run mock-server
```

Then start the React app in another terminal:
```bash
npm start
```

## 🔧 Configuration

Edit `/src/config/llm-config.js` to change the LLM provider:

```javascript
export const LLM_CONFIG = {
  provider: 'mock', // Change this to: 'mock', 'local-api', 'openai', 'ollama'
  // ... rest of config
};
```

## 🤖 Backend Options

### 1. Mock Server (Default)
- **Purpose**: Testing and development
- **Setup**: Run `npm run mock-server`
- **Responses**: Pre-written realistic responses

### 2. Local LLaMA-GPU API Server
- **Purpose**: Real local LLM inference
- **Setup**:
  ```bash
  cd /home/kevin/Projects/Llama-GPU
  python src/api_server.py
  ```
- **Requirements**: LLaMA model files, GPU support
- **Config**: Change provider to `'local-api'`

### 3. OpenAI API
- **Purpose**: Production-quality responses
- **Setup**:
  1. Get API key from OpenAI
  2. Set environment variable: `REACT_APP_OPENAI_API_KEY=your-key`
  3. Change provider to `'openai'`
- **Cost**: Paid service

### 4. Ollama (Local LLM)
- **Purpose**: Free local LLM inference
- **Setup**:
  ```bash
  # Install Ollama
  curl -fsSL https://ollama.ai/install.sh | sh

  # Start Ollama
  ollama serve

  # Pull a model (in another terminal)
  ollama pull llama2
  ```
- **Config**: Change provider to `'ollama'`

## 🔍 Troubleshooting

- **"Could not connect to API server"**: Make sure the backend server is running
- **CORS errors**: Check that the backend has CORS enabled for your frontend URL
- **Empty responses**: Check the backend logs for errors

## 🎯 Next Steps

1. Start with the mock server to test the UI
2. Choose your preferred backend based on your needs
3. Update the configuration file accordingly
4. Install any required dependencies for your chosen backend
