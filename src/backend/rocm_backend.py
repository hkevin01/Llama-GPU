"""ROCm backend for LLaMA model inference using PyTorch with AMD GPUs."""

import logging
from typing import Any, Dict, Iterator, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .base import Backend

logger = logging.getLogger(__name__)

class ROCMBackend(Backend):
    """ROCm backend implementation."""

    def __init__(self) -> None:
        """Initialize ROCm backend."""
        super().__init__()

    def load_model(
        self,
        model_path: str,
        quant_type: Optional[str] = None
    ) -> None:
        """
        Load the model and tokenizer for ROCm inference.

        Args:
            model_path: Path to the model
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
        """Stream inference using ROCm GPU."""
        return self._stream_infer(input_data, max_tokens, device='cuda')

    def is_available(self) -> bool:
        """Check if ROCm (AMD GPU) is available for this backend."""
        try:
            return torch.version.hip is not None and torch.cuda.is_available()
        except AttributeError:
            return False

    def get_gpu_info(self) -> Dict[str, Any]:
        """Get information about available AMD GPUs."""
        if not self.is_available():
            return {}

        gpu_info = {}
        try:
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                gpu_info[f'rocm:{i}'] = {
                    'name': props.name,
                    'total_memory': props.total_memory // 1024 ** 2,
                    'major': props.major,
                    'minor': props.minor
                }
        except (RuntimeError, AttributeError) as e:
            logger.error("Error getting GPU info: %s", e)
            return {}

        return gpu_info
