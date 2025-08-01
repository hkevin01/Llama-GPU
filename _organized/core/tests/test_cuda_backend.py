import pytest
from backend.cuda_backend import CUDABackend

def test_cuda_backend_is_available(monkeypatch):
    monkeypatch.setattr('torch.cuda.is_available', lambda: True)
    backend = CUDABackend()
    assert backend.is_available() is True
