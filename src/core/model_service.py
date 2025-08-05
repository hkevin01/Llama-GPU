"""Model service for managing the Llama model."""

import logging
import time
from typing import Dict, Optional

import torch

from src.core.exceptions import ModelError, ModelNotReadyError


class ModelService:
    """Service for managing the Llama model."""

    def __init__(
        self,
        model_path: str,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        max_length: int = 2048,
        temperature: float = 0.7
    ) -> None:
        """Initialize the model service.

        Args:
            model_path: Path to the model weights
            device: Device to run the model on
            max_length: Maximum sequence length
            temperature: Sampling temperature
        """
        self.model_path = model_path
        self.device = device
        self.max_length = max_length
        self.temperature = temperature

        self.model = None
        self.tokenizer = None
        self.is_ready = False
        self.last_error = None
        self.logger = logging.getLogger(__name__)

    async def initialize(self) -> None:
        """Initialize the model and tokenizer."""
        try:
            start_time = time.time()
            self.logger.info(f"Loading model from {self.model_path}")

            # Import here to avoid loading until needed
            from transformers import AutoModelForCausalLM, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                device_map=self.device,
                torch_dtype=torch.float16
            )

            self.is_ready = True
            elapsed = time.time() - start_time
            self.logger.info(f"Model loaded successfully in {elapsed:.2f}s")

        except Exception as e:
            self.is_ready = False
            self.last_error = str(e)
            self.logger.error(f"Failed to load model: {str(e)}")
            raise ModelError(f"Model initialization failed: {str(e)}")

    async def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """Generate text from the model.

        Args:
            prompt: Input prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Override default temperature

        Returns:
            Dict: Generated text and metadata

        Raises:
            ModelNotReadyError: If model is not ready
            ModelError: If generation fails
        """
        if not self.is_ready:
            raise ModelNotReadyError("Model is not ready")

        try:
            start_time = time.time()

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length
            ).to(self.device)

            gen_kwargs = {
                "max_new_tokens": max_new_tokens or self.max_length,
                "temperature": temperature or self.temperature,
                "do_sample": True
            }

            outputs = self.model.generate(**inputs, **gen_kwargs)
            text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            elapsed = time.time() - start_time
            tokens_generated = outputs.shape[1] - inputs["input_ids"].shape[1]

            # Log performance metrics
            logging.getLogger('performance').info(
                f"type=generation "
                f"tokens={tokens_generated} "
                f"duration={elapsed:.3f} "
                f"tokens_per_second={tokens_generated/elapsed:.2f}"
            )

            return {
                "text": text,
                "tokens_generated": tokens_generated,
                "duration": elapsed,
                "tokens_per_second": tokens_generated / elapsed
            }

        except Exception as e:
            self.logger.error(f"Generation error: {str(e)}")
            raise ModelError(f"Generation failed: {str(e)}")

    def get_status(self) -> Dict:
        """Get current model status.

        Returns:
            Dict: Model status information
        """
        return {
            "ready": self.is_ready,
            "device": self.device,
            "last_error": self.last_error,
            "model_path": self.model_path,
            "max_length": self.max_length,
            "temperature": self.temperature
        }

    async def cleanup(self) -> None:
        """Clean up model resources."""
        try:
            if self.model is not None:
                self.model.cpu()
                del self.model
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            self.is_ready = False
            self.logger.info("Model cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
