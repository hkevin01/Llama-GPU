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
            model: Model name (e.g., 'qwen3:4b', 'deepseek-r1:7b')
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
        tools: Optional[List[Dict[str, Any]]] = None,
        think: bool = False,
        **kwargs
    ):
        """Chat completion with conversation history.

        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream responses
            tools: Optional list of tool definitions for function calling
            think: Whether thinking models should show their thinking process (default: False for speed)
            **kwargs: Additional Ollama parameters

        Returns:
            Generated text (string) or full response dict if tools are provided
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "think": think,  # Disable thinking mode for faster responses
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                **kwargs
            }
        }

        # Add tools if provided
        if tools:
            payload["tools"] = tools

        try:
            response = requests.post(
                f"{self.api_url}/chat",
                json=payload,
                stream=stream,
                timeout=120 if not stream else None  # Longer timeout for tool calls
            )
            response.raise_for_status()

            if stream:
                return self._stream_chat_response(response)
            else:
                data = response.json()
                message = data.get("message", {})

                # If tools were provided, return full message dict for tool_calls handling
                if tools:
                    return {
                        "content": message.get("content", ""),
                        "tool_calls": message.get("tool_calls", []),
                        "thinking": message.get("thinking", ""),
                        "role": message.get("role", "assistant")
                    }

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

    def quick_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        brief: bool = True,
        **kwargs
    ):
        """Quick chat with optimized settings for faster thinking.

        Still allows the model to think, but with tuned parameters
        for quicker, more focused responses.

        Args:
            model: Model name
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream responses (default False for complete responses)
            brief: Add system prompt for concise answers (default True)
            **kwargs: Override any default parameters

        Returns:
            Generated text (string) or generator if streaming
        """
        # Add brevity system prompt if requested and not already present
        if brief:
            has_system = any(m.get('role') == 'system' for m in messages)
            if not has_system:
                messages = [{'role': 'system', 'content': 'Be very brief. Keep answers short and direct.'}] + messages

        # Optimized defaults for quick thinking
        quick_settings = {
            "max_tokens": 600,      # Enough for thinking + answer
            "temperature": 0.4,     # More focused, less wandering
            "think": True,          # Allow thinking for accuracy
            "top_p": 0.8,           # More focused sampling
            "repeat_penalty": 1.15, # Reduce repetition
        }
        # Allow overrides
        quick_settings.update(kwargs)

        return self.chat(
            model=model,
            messages=messages,
            stream=stream,
            **quick_settings
        )

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
