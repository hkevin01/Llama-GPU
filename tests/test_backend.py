import pytest
from backend.cpu_backend import CPUBackend
from backend.cuda_backend import CUDABackend
from backend.rocm_backend import ROCMBackend

@pytest.mark.parametrize("backend_cls", [CPUBackend, CUDABackend, ROCMBackend])
def test_backend_is_available(backend_cls):
    backend = backend_cls()
    assert isinstance(backend.is_available(), bool)
