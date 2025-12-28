"""Ollama backend adapter for Llama-GPU inference engine."""

from typing import Optional, Dict, List, Any
import logging
from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class OllamaBackend:
    """Backend adapter for Ollama models."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_model: str = "qwen3:4b"
    ):
        """Initialize Ollama backend.
        
        Args:
            base_url: Ollama API URL
            default_model: Default model to use
        """
        self.client = OllamaClient(base_url)
        self.default_model = default_model
        self._is_available = None
        
    def initialize(self) -> bool:
        """Initialize and check if backend is available."""
        self._is_available = self.client.is_available()
        if self._is_available:
            models = self.client.list_models()
            logger.info(f"Ollama backend initialized with {len(models)} models")
            if models:
                logger.info(f"Available models: {[m['name'] for m in models]}")
        else:
            logger.warning("Ollama backend not available")
        return self._is_available
    
    def is_available(self) -> bool:
        """Check if backend is available."""
        if self._is_available is None:
            self.initialize()
        return self._is_available or False
    
    def infer(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ) -> str:
        """Run inference on prompt.
        
        Args:
            prompt: Input text
            model: Model name (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream (not used in sync mode)
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        model = model or self.default_model
        
        try:
            response = self.client.generate(
                model=model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return f"Error: {str(e)}"
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Run chat completion.
        
        Args:
            messages: List of conversation messages
            model: Model name (uses default if None)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Generated response
        """
        model = model or self.default_model
        
        try:
            response = self.client.chat(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
                **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return f"Error: {str(e)}"
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models."""
        return self.client.list_models()
    
    def get_model_info(self, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get information about a model.
        
        Args:
            model: Model name (uses default if None)
            
        Returns:
            Model information dictionary
        """
        model = model or self.default_model
        return self.client.show_model_info(model)
    
    def load_model(self, model: str) -> bool:
        """Load/pull a model if not available.
        
        Args:
            model: Model name to load
            
        Returns:
            True if successful
        """
        models = self.list_models()
        if any(m['name'] == model for m in models):
            logger.info(f"Model {model} already available")
            return True
        
        logger.info(f"Pulling model {model}...")
        return self.client.pull_model(model)
    
    def get_backend_type(self) -> str:
        """Get backend type identifier."""
        return "ollama"
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device/backend information."""
        return {
            "backend": "ollama",
            "available": self.is_available(),
            "models": [m['name'] for m in self.list_models()],
            "default_model": self.default_model
        }
