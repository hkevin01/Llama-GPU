import os
from pathlib import Path
from typing import Optional

from transformers import AutoModelForCausalLM, AutoTokenizer


class ModelManager:
    """Utility for downloading, caching, and loading models from HuggingFace Hub."""
    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir or os.environ.get("LLAMA_GPU_MODEL_CACHE", "~/.cache/llama-gpu/models")).expanduser()
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_model_path(self, model_name: str, revision: Optional[str] = None) -> Path:
        """Return the local path for a model, optionally by revision."""
        if revision:
            return self.cache_dir / f"{model_name.replace('/', '_')}--{revision}"
        return self.cache_dir / model_name.replace('/', '_')

    def download_model(self, model_name: str, revision: Optional[str] = None) -> Path:
        """Download model and tokenizer from HuggingFace Hub if not cached."""
        model_path = self.get_model_path(model_name, revision)
        if not model_path.exists():
            print(f"Downloading model {model_name} to {model_path}")
            model_path.mkdir(parents=True, exist_ok=True)
            # Download model and tokenizer
            AutoModelForCausalLM.from_pretrained(model_name, cache_dir=str(model_path), revision=revision)
            AutoTokenizer.from_pretrained(model_name, cache_dir=str(model_path), revision=revision)
        else:
            print(f"Model {model_name} already cached at {model_path}")
        return model_path

    def load_model(self, model_name: str, revision: Optional[str] = None, device: str = "cpu"):
        """Load model and tokenizer from cache or HuggingFace Hub."""
        model_path = self.download_model(model_name, revision)
        tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        model = AutoModelForCausalLM.from_pretrained(str(model_path))
        model.to(device)
        return model, tokenizer

    # Stub for version management (to be expanded)
    def list_cached_models(self):
        return [p for p in self.cache_dir.iterdir() if p.is_dir()] 