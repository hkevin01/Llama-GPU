from typing import Iterator, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .base import Backend


class ROCMBackend(Backend):
    """ROCm backend for LLaMA model inference using PyTorch with AMD GPU acceleration."""
    def __init__(self) -> None:
        """Initialize ROCm backend with empty model and tokenizer."""
        super().__init__()

    def load_model(
        self,
        model_path: str,
        quant_type: Optional[str] = None
    ) -> None:
        """
        Load the LLaMA model and tokenizer for ROCm (AMD GPU) inference, optionally quantized.

        Args:
            model_path: Path to the LLaMA model
            quant_type: Optional quantization type ('int8', 'float16', etc.)
        """
        self._load_model_and_tokenizer(
            model_path,
            device='cuda',
            dtype=torch.float16,
            quant_type=quant_type
        )

    def infer(self, input_data: str) -> str:
        """Perform inference on input data using ROCm GPU acceleration."""
        return self._infer(input_data, device='cuda')

    def batch_infer(
        self,
        input_data: List[str],
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Perform batch inference on multiple input texts using ROCm GPU."""
        return self._batch_infer(input_data, batch_size, device='cuda')

    def stream_infer(
        self,
        input_data: str,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """Perform streaming inference using ROCm GPU, yielding tokens as they're generated."""
        return self._stream_infer(input_data, max_tokens, device='cuda')

    def is_available(self) -> bool:
        """Check if ROCm (AMD GPU) is available for this backend."""
        try:
            return torch.version.hip is not None and torch.cuda.is_available()
        except AttributeError:
            return False
