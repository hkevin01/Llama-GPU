from unittest.mock import MagicMock

import pytest

from backend.cpu_backend import CPUBackend
from backend.cuda_backend import CUDABackend
from backend.rocm_backend import ROCMBackend


@pytest.mark.parametrize("backend_cls", [CPUBackend, CUDABackend, ROCMBackend])
def test_backend_is_available(backend_cls):
    backend = backend_cls()
    assert isinstance(backend.is_available(), bool)


@pytest.mark.parametrize("backend_cls", [CPUBackend, CUDABackend, ROCMBackend])
def test_batch_infer_with_mocks(backend_cls):
    backend = backend_cls()
    backend.model = MagicMock()
    backend.tokenizer = MagicMock()
    backend.model.generate.return_value = [[0, 1, 2], [3, 4, 5]]
    backend.tokenizer.decode.side_effect = (
        lambda ids, skip_special_tokens=True: f"mock output {ids}"
    )
    backend.tokenizer.__call__ = MagicMock(
        return_value={'input_ids': [[0, 1, 2], [3, 4, 5]]}
    )
    results = backend.batch_infer(["input1", "input2"], batch_size=2)
    assert len(results) == 2
    assert all("mock output" in r for r in results)


@pytest.mark.parametrize("backend_cls", [CPUBackend, CUDABackend, ROCMBackend])
def test_stream_infer_with_mocks(backend_cls):
    backend = backend_cls()
    backend.model = MagicMock()
    backend.tokenizer = MagicMock()
    # Simulate streaming 3 tokens
    backend.model.generate.side_effect = [
        [[0, 1]], [[0, 1, 2]], [[0, 1, 2, 3]]
    ]
    backend.tokenizer.decode.side_effect = (
        lambda ids, skip_special_tokens=True: f"token{len(ids)}"
    )
    backend.tokenizer.__call__ = MagicMock(
        return_value={'input_ids': [[0, 1]]}
    )
    tokens = list(backend.stream_infer("input", max_tokens=3))
    assert len(tokens) == 3
    assert all(t.startswith("token") for t in tokens)


@pytest.mark.parametrize("backend_cls", [CPUBackend, CUDABackend, ROCMBackend])
def test_batch_infer_empty_input(backend_cls):
    backend = backend_cls()
    backend.model = MagicMock()
    backend.tokenizer = MagicMock()
    results = backend.batch_infer([], batch_size=2)
    assert results == []


@pytest.mark.parametrize("backend_cls", [CPUBackend, CUDABackend, ROCMBackend])
def test_infer_error_handling(backend_cls):
    backend = backend_cls()
    backend.model = None
    backend.tokenizer = None
    with pytest.raises(Exception):
        backend.infer("input")


def log_test_result(test_name, result):
    with open('logs/test_output.log', 'a') as f:
        f.write(f"{test_name}: {result}\n")


def test_memory_usage_reporting():
    from backend.cpu_backend import CPUBackend
    backend = CPUBackend()
    mem_stats = backend.get_memory_usage()
    result = 'total_mb' in mem_stats or 'allocated_mb' in mem_stats
    log_test_result('test_memory_usage_reporting', result)
    assert result


def test_streaming_infer_logging():
    from backend.cpu_backend import CPUBackend
    backend = CPUBackend()
    backend.model = torch.nn.Linear(10, 10)
    backend.tokenizer = None  # Mock or skip actual tokenizer for test
    try:
        # Simulate streaming output
        tokens = list(backend.stream_infer("test", max_tokens=3))
        result = len(tokens) == 3
    except Exception:
        result = False
    log_test_result('test_streaming_infer_logging', result)
    assert result


def test_batch_infer_logging():
    from backend.cpu_backend import CPUBackend
    backend = CPUBackend()
    backend.model = torch.nn.Linear(10, 10)
    backend.tokenizer = None  # Mock or skip actual tokenizer for test
    try:
        outputs = backend.batch_infer(["a", "b", "c"], batch_size=2)
        result = isinstance(outputs, list)
    except Exception:
        result = False
    log_test_result('test_batch_infer_logging', result)
    assert result
