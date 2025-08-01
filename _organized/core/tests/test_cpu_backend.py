import pytest
from backend.cpu_backend import CPUBackend

def test_cpu_backend_is_available():
    backend = CPUBackend()
    assert backend.is_available() is True

def test_cpu_backend_load_and_infer(monkeypatch):
    backend = CPUBackend()
    # Mock model and tokenizer for fast test
    backend.model = type('MockModel', (), {'generate': lambda self, **kwargs: [[0, 1, 2]]})()
    backend.tokenizer = type('MockTokenizer', (), {
        'decode': lambda self, ids, skip_special_tokens=True: 'mock output',
        '__call__': lambda self, x, return_tensors=None: {'input_ids': [[0, 1, 2]]}
    })()
    result = backend.infer('test input')
    assert result == 'mock output'
