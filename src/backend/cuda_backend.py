from typing import Iterator, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .base import Backend


class CUDABackend(Backend):
    """CUDA backend for LLaMA model inference using PyTorch with GPU acceleration."""
    def __init__(self) -> None:
        """Initialize CUDA backend with empty model and tokenizer."""
        super().__init__()

    def load_model(self, model_path: str) -> None:
        """Load the LLaMA model and tokenizer for CUDA GPU inference."""
        self._load_model_and_tokenizer(model_path, device='cuda', dtype=torch.float16)

    def infer(self, input_data: str) -> str:
        """Perform inference on input data using CUDA GPU acceleration."""
        return self._infer(input_data, device='cuda')

    def batch_infer(self, input_data: List[str], batch_size: Optional[int] = None) -> List[str]:
        """Perform batch inference on multiple input texts using CUDA GPU."""
        return self._batch_infer(input_data, batch_size, device='cuda')

    def stream_infer(self, input_data: str, max_tokens: Optional[int] = None) -> Iterator[str]:
        """Perform streaming inference using CUDA GPU, yielding tokens as they're generated."""
        return self._stream_infer(input_data, max_tokens, device='cuda')

    def is_available(self) -> bool:
        """Check if CUDA GPU is available for this backend."""
        return torch.cuda.is_available()
