"""Ollama API client for direct model interaction."""

import json
import requests
from typing import Dict, List, Optional, Generator, Any
import logging

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize Ollama client.

        Args:
            base_url: Base URL for Ollama API (default: http://localhost:11434)
        """
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api"

    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models."""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def generate(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ):
        """Generate text completion.

        Args:
            model: Model name (e.g., 'phi4-mini:3.8b', 'deepseek-r1:7b')
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream responses
            **kwargs: Additional Ollama parameters

        Returns:
            Generated text (string) or generator if streaming
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                stream=stream,
                timeout=60 if not stream else None
            )
            response.raise_for_status()

            if stream:
                return self._stream_response(response)
            else:
                data = response.json()
                return data.get("response", "")

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def _stream_response(self, response) -> Generator[str, None, None]:
        """Stream response chunks."""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 512,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ):
        """Chat completion with conversation history.

        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream responses
            **kwargs: Additional Ollama parameters

        Returns:
            Generated text (string) or generator if streaming
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }

        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                stream=stream,
                timeout=60 if not stream else None
            )
            response.raise_for_status()

            if stream:
                return self._stream_chat_response(response)
            else:
                data = response.json()
                message = data.get("message", {})
                return message.get("content", "")

        except Exception as e:
            logger.error(f"Chat failed: {e}")
            raise

    def _stream_chat_response(self, response) -> Generator[str, None, None]:
        """Stream chat response chunks."""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "message" in data:
                        content = data["message"].get("content", "")
                        if content:
                            yield content
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue

    def pull_model(self, model: str) -> bool:
        """Pull/download a model from Ollama registry.

        Args:
            model: Model name to pull

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.api_url}/pull",
                json={"name": model},
                stream=True,
                timeout=None
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        logger.info(f"Pull status: {status}")
                    except json.JSONDecodeError:
                        continue

            return True
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
            return False

    def delete_model(self, model: str) -> bool:
        """Delete a model from local storage.

        Args:
            model: Model name to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.api_url}/delete",
                json={"name": model},
                timeout=10
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to delete model: {e}")
            return False

    def show_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a model.

        Args:
            model: Model name

        Returns:
            Model information dictionary or None if not found
        """
        try:
            response = requests.post(
                f"{self.api_url}/show",
                json={"name": model},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return None
