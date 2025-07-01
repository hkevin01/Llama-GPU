import pytest
from llama_gpu import LlamaGPU

def test_llama_gpu_backend_selection(monkeypatch):
    monkeypatch.setattr('backend.cuda_backend.CUDABackend.is_available', lambda self: False)
    monkeypatch.setattr('backend.rocm_backend.ROCMBackend.is_available', lambda self: False)
    llama = LlamaGPU(model_path='mock-model', prefer_gpu=True)
    assert llama.backend.__class__.__name__ == 'CPUBackend'
