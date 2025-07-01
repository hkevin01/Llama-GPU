import pytest
from backend.rocm_backend import ROCMBackend

def test_rocm_backend_is_available(monkeypatch):
    monkeypatch.setattr('torch.cuda.is_available', lambda: True)
    monkeypatch.setattr('torch.version', type('ver', (), {'hip': 'mock'})())
    backend = ROCMBackend()
    assert backend.is_available() is True
