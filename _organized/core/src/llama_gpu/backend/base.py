from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class Backend(ABC):
    def __init__(self):
        """Initialize the backend with empty model and tokenizer."""
        self.model: Optional[Any] = None
        self.tokenizer: Optional[Any] = None

    def _load_model_and_tokenizer(
        self,
        model_path: str,
        device: str,
        dtype: torch.dtype,
        quant_type: Optional[str] = None
    ) -> None:
        """
        Load the model and tokenizer from the given path, move to device and dtype.
        Optionally apply quantization.

        Args:
            model_path: Path to the pretrained model directory
            device: Device string ('cpu' or 'cuda')
            dtype: PyTorch dtype (e.g., torch.float32, torch.float16)
            quant_type: Optional quantization type ('int8', 'float16', etc.)
        """
        from utils.quantization import apply_quantization
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=dtype
        )
        self.model.to(device)
        if quant_type:
            self.model = apply_quantization(self.model, quant_type)

    def _infer(self, input_data: str, device: str) -> str:
        """
        Perform single inference on input text.

        Args:
            input_data: Input text to process
            device: Device string ('cpu' or 'cuda')
        Returns:
            Generated text output
        """
        inputs = self.tokenizer(input_data, return_tensors="pt")
        if device != 'cpu':
            inputs = {
                k: v.to(device) if isinstance(v, torch.Tensor) else v
                for k, v in inputs.items()
            }
        with torch.no_grad():
            outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _batch_infer(
        self,
        input_data: List[str],
        batch_size: Optional[int],
        device: str
    ) -> List[str]:
        """
        Perform batch inference on multiple input texts.

        Args:
            input_data: List of input texts to process
            batch_size: Optional batch size for processing
            device: Device string ('cpu' or 'cuda')
        Returns:
            List of generated outputs
        """
        if not input_data:
            return []
        if batch_size is None:
            batch_size = len(input_data)
        results = []
        for i in range(0, len(input_data), batch_size):
            batch = input_data[i:i + batch_size]
            batch_inputs = self.tokenizer(
                batch,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            if device != 'cpu':
                batch_inputs = {
                    k: v.to(device) if isinstance(v, torch.Tensor) else v
                    for k, v in batch_inputs.items()
                }
            with torch.no_grad():
                batch_outputs = self.model.generate(**batch_inputs)
            batch_results = [
                self.tokenizer.decode(output, skip_special_tokens=True)
                for output in batch_outputs
            ]
            results.extend(batch_results)
        return results

    def _stream_infer(
        self,
        input_data: str,
        max_tokens: Optional[int],
        device: str
    ) -> Iterator[str]:
        """
        Perform streaming inference, yielding tokens as they're generated.

        Args:
            input_data: Input text to process
            max_tokens: Maximum number of tokens to generate (None for unlimited)
            device: Device string ('cpu' or 'cuda')
        Yields:
            Generated text tokens one at a time
        """
        inputs = self.tokenizer(input_data, return_tensors="pt")
        if device != 'cpu':
            inputs = {
                k: v.to(device) if isinstance(v, torch.Tensor) else v
                for k, v in inputs.items()
            }
        with torch.no_grad():
            for _ in range(max_tokens or 100):
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=1,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                new_token = outputs[0][-1].unsqueeze(0)
                new_text = self.tokenizer.decode(new_token, skip_special_tokens=True)
                if new_text:
                    yield new_text
                inputs['input_ids'] = torch.cat(
                    [inputs['input_ids'], new_token.unsqueeze(0)],
                    dim=1
                )
                if new_token.item() == self.tokenizer.eos_token_id:
                    break

    def get_memory_usage(self) -> dict:
        """
        Report current memory usage for the backend (GPU or CPU).

        Returns:
            Dictionary with memory usage stats.
        """
        from utils.memory import get_gpu_memory_usage, get_cpu_memory_usage
        if torch.cuda.is_available():
            return get_gpu_memory_usage()
        else:
            return get_cpu_memory_usage()

    @abstractmethod
    def load_model(
        self,
        model_path: str,
        quant_type: Optional[str] = None
    ) -> None:
        """Load the model and tokenizer, optionally with quantization."""

    @abstractmethod
    def infer(self, input_data: str) -> str:
        """Perform single inference on input text."""

    @abstractmethod
    def batch_infer(
        self,
        input_data: List[str],
        batch_size: Optional[int] = None
    ) -> List[str]:
        """Perform batch inference on multiple input texts."""

    @abstractmethod
    def stream_infer(
        self,
        input_data: str,
        max_tokens: Optional[int] = None
    ) -> Iterator[str]:
        """
        Perform streaming inference, yielding tokens as they're generated.
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
