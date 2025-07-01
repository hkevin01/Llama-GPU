from .base import Backend
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Iterator, Optional

class ROCMBackend(Backend):
    """ROCm backend for LLaMA model inference using PyTorch with AMD GPU acceleration."""
    
    def __init__(self):
        """Initialize ROCm backend with empty model and tokenizer."""
        self.model = None
        self.tokenizer = None

    def load_model(self, model_path: str):
        """Load the LLaMA model and tokenizer for ROCm (AMD GPU) inference.
        
        Args:
            model_path: Path to the pretrained model directory
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16)
        self.model.to('cuda')  # ROCm uses 'cuda' device string for AMD GPUs

    def infer(self, input_data: str) -> str:
        """Perform inference on input data using ROCm GPU acceleration.
        
        Args:
            input_data: Input text to process
            
        Returns:
            Generated text output
        """
        inputs = self.tokenizer(input_data, return_tensors="pt").to('cuda')
        with torch.no_grad():
            outputs = self.model.generate(**inputs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def batch_infer(self, input_data: List[str], batch_size: Optional[int] = None) -> List[str]:
        """Perform batch inference on multiple input texts using ROCm GPU.
        
        Args:
            input_data: List of input texts to process
            batch_size: Optional batch size for processing (defaults to all inputs)
            
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
            batch_inputs = self.tokenizer(batch, return_tensors="pt", padding=True, truncation=True)
            
            # Move inputs to GPU
            for key, value in batch_inputs.items():
                if isinstance(value, torch.Tensor):
                    batch_inputs[key] = value.to('cuda')
            
            with torch.no_grad():
                batch_outputs = self.model.generate(**batch_inputs)
            
            batch_results = [self.tokenizer.decode(output, skip_special_tokens=True) 
                           for output in batch_outputs]
            results.extend(batch_results)
        
        return results

    def stream_infer(self, input_data: str, max_tokens: Optional[int] = None) -> Iterator[str]:
        """Perform streaming inference using ROCm GPU, yielding tokens as they're generated.
        
        Args:
            input_data: Input text to process
            max_tokens: Maximum number of tokens to generate (None for unlimited)
            
        Yields:
            Generated text tokens one at a time
        """
        inputs = self.tokenizer(input_data, return_tensors="pt").to('cuda')
        generated_tokens = []
        
        with torch.no_grad():
            for _ in range(max_tokens or 100):  # Default limit of 100 tokens
                outputs = self.model.generate(
                    **inputs, 
                    max_new_tokens=1,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                
                new_token = outputs[0][-1].unsqueeze(0)
                generated_tokens.append(new_token)
                
                # Decode the new token
                new_text = self.tokenizer.decode(new_token, skip_special_tokens=True)
                if new_text:
                    yield new_text
                
                # Update inputs for next iteration
                inputs['input_ids'] = torch.cat([inputs['input_ids'], new_token.unsqueeze(0)], dim=1)
                
                # Stop if we hit the end token
                if new_token.item() == self.tokenizer.eos_token_id:
                    break

    def is_available(self) -> bool:
        """Check if ROCm (AMD GPU) is available for this backend."""
        try:
            return torch.version.hip is not None and torch.cuda.is_available()
        except AttributeError:
            return False
