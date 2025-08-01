from typing import Iterator, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .base import Backend


class CPUBackend(Backend):
    """CPU backend for LLaMA model inference using PyTorch."""
    def __init__(self) -> None:
        """Initialize CPU backend with empty model and tokenizer."""
        super().__init__()

    def load_model(
        self,
        model_path: str,
        quant_type: Optional[str] = None
    ) -> None:
        """
        Load the LLaMA model and tokenizer for CPU inference, optionally quantized.

        Args:
            model_path: Path to the LLaMA model
            quant_type: Optional quantization type ('int8', 'float16', etc.)
        """
        self._load_model_and_tokenizer(
            model_path,
            device='cpu',
            dtype=torch.float32,
            quant_type=quant_type
        )

    def infer(self, input_data: str) -> str:
        """Perform inference on input data using the loaded model."""
        return self._infer(input_data, device='cpu')

    def batch_infer(
        self,
        input_data: List[str],
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Perform batch inference on multiple input texts."""
        return self._batch_infer(input_data, batch_size, device='cpu')

    def stream_infer(
        self,
        input_data: str,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """Perform streaming inference, yielding tokens as they're generated."""
        return self._stream_infer(input_data, max_tokens, device='cpu')

    def is_available(self) -> bool:
        """Check if the CPU backend is available (always True)."""
        return True
