from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, Dict, Any

class Backend(ABC):
    @abstractmethod
    def load_model(self, model_path: str):
        """Load the model and tokenizer."""
        pass

    @abstractmethod
    def infer(self, input_data: str) -> str:
        """Perform single inference on input text."""
        pass

    @abstractmethod
    def batch_infer(self, input_data: List[str], batch_size: Optional[int] = None) -> List[str]:
        """Perform batch inference on multiple input texts.
        
        Args:
            input_data: List of input texts to process
            batch_size: Optional batch size for processing (defaults to all inputs)
            
        Returns:
            List of generated outputs
        """
        pass

    @abstractmethod
    def stream_infer(self, input_data: str, max_tokens: Optional[int] = None) -> Iterator[str]:
        """Perform streaming inference, yielding tokens as they're generated.
        
        Args:
            input_data: Input text to process
            max_tokens: Maximum number of tokens to generate (None for unlimited)
            
        Yields:
            Generated text tokens one at a time
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available."""
        pass
