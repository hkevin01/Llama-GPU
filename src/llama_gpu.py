from backend.cpu_backend import CPUBackend
from backend.cuda_backend import CUDABackend
from backend.rocm_backend import ROCMBackend
import torch
import os

class LlamaGPU:
    def __init__(self, model_path: str, prefer_gpu: bool = True):
        self.backend = self.select_backend(prefer_gpu)
        self.backend.load_model(model_path)

    def select_backend(self, prefer_gpu: bool):
        if prefer_gpu:
            if ROCMBackend().is_available():
                print("Using ROCm backend (AMD GPU detected)")
                return ROCMBackend()
            elif CUDABackend().is_available():
                print("Using CUDA backend (NVIDIA GPU detected)")
                return CUDABackend()
        print("Using CPU backend")
        return CPUBackend()

    def infer(self, input_data):
        return self.backend.infer(input_data)

# Example usage:
# llama = LlamaGPU(model_path="path/to/model", prefer_gpu=True)
# result = llama.infer("Hello, world!")
