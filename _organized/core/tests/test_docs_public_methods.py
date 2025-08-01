import inspect
from backend import cpu_backend, cuda_backend, rocm_backend
from llama_gpu import LlamaGPU

def test_cpu_backend_public_methods_doc():
    for name, func in inspect.getmembers(cpu_backend.CPUBackend, inspect.isfunction):
        assert func.__doc__ is not None, f"Missing docstring for {name} in CPUBackend"

def test_cuda_backend_public_methods_doc():
    for name, func in inspect.getmembers(cuda_backend.CUDABackend, inspect.isfunction):
        assert func.__doc__ is not None, f"Missing docstring for {name} in CUDABackend"

def test_rocm_backend_public_methods_doc():
    for name, func in inspect.getmembers(rocm_backend.ROCMBackend, inspect.isfunction):
        assert func.__doc__ is not None, f"Missing docstring for {name} in ROCMBackend"

def test_llama_gpu_public_methods_doc():
    for name, func in inspect.getmembers(LlamaGPU, inspect.isfunction):
        assert func.__doc__ is not None, f"Missing docstring for {name} in LlamaGPU"
