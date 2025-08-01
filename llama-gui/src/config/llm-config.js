// LLM Backend Configuration
// Change these settings to connect to different LLM providers

export const LLM_CONFIG = {
  // Current backend - change this to switch providers
  // Options: 'mock', 'local-api', 'openai', 'ollama'
  provider: 'mock',

  // Configuration for each provider
  providers: {
    // Mock server for testing (starts with npm run mock-server)
    mock: {
      baseUrl: 'http://localhost:8000',
      endpoint: '/v1/chat/completions',
      model: 'llama-base',
      headers: {
        'Content-Type': 'application/json'
      }
    },

    // Local LLaMA-GPU API server
    'local-api': {
      baseUrl: 'http://localhost:8001',
      endpoint: '/v1/chat/completions',
      model: 'llama-7b',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-key'
      }
    },

    // OpenAI API (requires API key in environment)
    openai: {
      baseUrl: 'https://api.openai.com',
      endpoint: '/v1/chat/completions',
      model: 'gpt-3.5-turbo',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.REACT_APP_OPENAI_API_KEY || 'your-api-key-here'}`
      }
    },

    // Ollama local server (install Ollama and run: ollama serve)
    ollama: {
      baseUrl: 'http://localhost:11434',
      endpoint: '/v1/chat/completions',
      model: 'llama2',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  }
};

// Get current provider configuration
export const getCurrentConfig = () => {
  const config = LLM_CONFIG.providers[LLM_CONFIG.provider];
  if (!config) {
    throw new Error(`Unknown LLM provider: ${LLM_CONFIG.provider}`);
  }
  return {
    url: `${config.baseUrl}${config.endpoint}`,
    ...config
  };
};

// Helper to check if provider is available
export const checkProviderHealth = async (provider = LLM_CONFIG.provider) => {
  const config = LLM_CONFIG.providers[provider];
  if (!config) return false;

  try {
    const response = await fetch(`${config.baseUrl}/health`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });
    return response.ok;
  } catch {
    return false;
  }
};
