import time
from typing import Iterator, List, Optional


class LlamaGPU:
    """Minimal demo engine with CPU fallback.

    This stub ensures API and GUI work without real models/GPUs.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        prefer_gpu: bool = True,
    ) -> None:
        self.model_path = model_path
        self.prefer_gpu = prefer_gpu
        self.backend = self._detect_backend()

    def _detect_backend(self) -> str:
        import importlib
        import importlib.util

        spec = importlib.util.find_spec("torch")
        if spec is None:
            return "cpu"
        try:
            torch = importlib.import_module("torch")  # type: ignore
        except ImportError:
            return "cpu"

        cuda = getattr(torch, "cuda", None)
        is_available = getattr(cuda, "is_available", None)
        if callable(is_available) and is_available():
            return "cuda"

        version = getattr(torch, "version", None)
        if getattr(version, "hip", None):
            return "rocm"

        return "cpu"

    def infer(
        self, prompt: str, max_tokens: int = 128, temperature: float = 0.7
    ) -> str:
        prefix = f"[demo:{self.backend}]"
        return (
            f"{prefix} Response to: {prompt[:64]} "
            f"(max_tokens={max_tokens}, temp={temperature})"
        )

    def batch_infer(
        self,
        prompts: List[str],
        batch_size: int = 1,
        max_tokens: int = 128,
        temperature: float = 0.7,
    ) -> List[str]:
        _ = batch_size  # kept for API compatibility in future
        return [
            self.infer(p, max_tokens=max_tokens, temperature=temperature)
            for p in prompts
        ]

    def stream_infer(
        self, prompt: str, delay: float = 0.02, **_: object
    ) -> Iterator[str]:
        demo = f"[stream:{self.backend}] Response to: {prompt[:64]}"
        for token in demo.split(" "):
            yield token + " "
            time.sleep(delay)
