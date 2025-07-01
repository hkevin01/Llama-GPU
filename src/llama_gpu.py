from backend.cpu_backend import CPUBackend
from backend.cuda_backend import CUDABackend
from backend.rocm_backend import ROCMBackend
from utils.aws_detection import is_aws_gpu_instance, get_optimal_aws_backend, get_aws_gpu_info
import torch
import os
from typing import List, Iterator, Optional

class LlamaGPU:
    """Main interface for LLaMA GPU-accelerated inference."""
    
    def __init__(self, model_path: str, prefer_gpu: bool = True, auto_detect_aws: bool = True):
        """Initialize LlamaGPU with model and preferred backend.
        
        Args:
            model_path: Path to the LLaMA model
            prefer_gpu: Whether to prefer GPU backends over CPU
            auto_detect_aws: Whether to automatically detect and optimize for AWS GPU instances
        """
        self.model_path = model_path
        self.prefer_gpu = prefer_gpu
        self.auto_detect_aws = auto_detect_aws
        self.backend = self.select_backend(prefer_gpu)
        self.backend.load_model(model_path)

    def select_backend(self, prefer_gpu: bool):
        """Select the best backend based on hardware and user preference.
        
        Args:
            prefer_gpu: Whether to prefer GPU backends over CPU
        
        Returns:
            The selected backend instance
        """
        # Check AWS GPU instance first if auto-detection is enabled
        if self.auto_detect_aws and is_aws_gpu_instance():
            aws_backend = get_optimal_aws_backend()
            gpu_info = get_aws_gpu_info()
            
            if aws_backend == 'cuda' and CUDABackend().is_available():
                print(f"Using CUDA backend on AWS GPU instance: {gpu_info}")
                return CUDABackend()
            elif aws_backend == 'rocm' and ROCMBackend().is_available():
                print(f"Using ROCm backend on AWS GPU instance: {gpu_info}")
                return ROCMBackend()
            else:
                print(f"AWS GPU detected but optimal backend not available, falling back to CPU")
                return CPUBackend()
        
        # Standard backend selection logic
        if prefer_gpu:
            if ROCMBackend().is_available():
                print("Using ROCm backend (AMD GPU detected)")
                return ROCMBackend()
            elif CUDABackend().is_available():
                print("Using CUDA backend (NVIDIA GPU detected)")
                return CUDABackend()
        print("Using CPU backend")
        return CPUBackend()

    def infer(self, input_data: str) -> str:
        """Perform inference using the selected backend.
        
        Args:
            input_data: Input text to process
            
        Returns:
            Generated text output
        """
        return self.backend.infer(input_data)

    def batch_infer(self, input_data: List[str], batch_size: Optional[int] = None) -> List[str]:
        """Perform batch inference on multiple input texts.
        
        Args:
            input_data: List of input texts to process
            batch_size: Optional batch size for processing (defaults to all inputs)
            
        Returns:
            List of generated outputs
        """
        return self.backend.batch_infer(input_data, batch_size)

    def stream_infer(self, input_data: str, max_tokens: Optional[int] = None) -> Iterator[str]:
        """Perform streaming inference, yielding tokens as they're generated.
        
        Args:
            input_data: Input text to process
            max_tokens: Maximum number of tokens to generate (None for unlimited)
            
        Yields:
            Generated text tokens one at a time
        """
        return self.backend.stream_infer(input_data, max_tokens)

    def get_backend_info(self) -> dict:
        """Get information about the current backend and hardware.
        
        Returns:
            Dictionary with backend and hardware information
        """
        info = {
            'backend_type': self.backend.__class__.__name__,
            'model_path': self.model_path,
            'prefer_gpu': self.prefer_gpu,
            'auto_detect_aws': self.auto_detect_aws
        }
        
        # Add AWS-specific information if available
        if self.auto_detect_aws and is_aws_gpu_instance():
            info['aws_instance'] = True
            info['aws_gpu_info'] = get_aws_gpu_info()
        else:
            info['aws_instance'] = False
        
        return info

# Example usage:
# llama = LlamaGPU(model_path="path/to/model", prefer_gpu=True)
# result = llama.infer("Hello, world!")
# 
# # Batch inference
# results = llama.batch_infer(["Hello", "How are you?", "Tell me a story"])
# 
# # Streaming inference
# for token in llama.stream_infer("Once upon a time"):
#     print(token, end="", flush=True)
