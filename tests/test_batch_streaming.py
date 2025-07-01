"""Tests for batch and streaming inference features."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import torch

def test_cpu_backend_batch_inference():
    """Test CPU backend batch inference."""
    from backend.cpu_backend import CPUBackend
    
    # Mock the model and tokenizer
    backend = CPUBackend()
    backend.model = Mock()
    backend.tokenizer = Mock()
    
    # Mock tokenizer behavior
    backend.tokenizer.return_value = {'input_ids': torch.tensor([[1, 2, 3], [4, 5, 6]])}
    backend.tokenizer.decode.return_value = "mocked output"
    
    # Mock model behavior
    backend.model.generate.return_value = torch.tensor([[1, 2, 3, 4], [4, 5, 6, 7]])
    
    # Test batch inference
    inputs = ["Hello", "How are you?"]
    results = backend.batch_infer(inputs, batch_size=2)
    
    assert len(results) == 2
    assert all(result == "mocked output" for result in results)
    assert backend.tokenizer.call_count == 1
    assert backend.model.generate.call_count == 1

def test_cuda_backend_batch_inference():
    """Test CUDA backend batch inference."""
    from backend.cuda_backend import CUDABackend
    
    with patch('torch.cuda.is_available', return_value=True):
        backend = CUDABackend()
        backend.model = Mock()
        backend.tokenizer = Mock()
        
        # Mock tokenizer behavior for batch processing
        mock_tensor1 = Mock()
        mock_tensor1.to.return_value = mock_tensor1
        mock_tensor2 = Mock()
        mock_tensor2.to.return_value = mock_tensor2
        
        backend.tokenizer.side_effect = [
            {'input_ids': mock_tensor1},  # First batch (single item)
            {'input_ids': mock_tensor2}   # Second batch (single item)
        ]
        backend.tokenizer.decode.return_value = "mocked output"
        
        # Mock model behavior for each batch
        backend.model.generate.side_effect = [
            torch.tensor([[1, 2, 3, 4]]),  # First batch output
            torch.tensor([[4, 5, 6, 7]])   # Second batch output
        ]
        
        # Test batch inference with batch_size=1 (processes 2 items in 2 batches)
        inputs = ["Hello", "How are you?"]
        results = backend.batch_infer(inputs, batch_size=1)
        
        assert len(results) == 2
        assert all(result == "mocked output" for result in results)

def test_streaming_inference():
    """Test streaming inference functionality."""
    from backend.cpu_backend import CPUBackend
    
    backend = CPUBackend()
    backend.model = Mock()
    backend.tokenizer = Mock()
    
    # Mock tokenizer behavior
    backend.tokenizer.return_value = {'input_ids': torch.tensor([[1, 2, 3]])}
    backend.tokenizer.decode.side_effect = ["token1", "token2", "token3"]
    backend.tokenizer.eos_token_id = 999
    
    # Mock model behavior for streaming
    backend.model.generate.side_effect = [
        torch.tensor([[1, 2, 3, 10]]),  # First token
        torch.tensor([[1, 2, 3, 10, 20]]),  # Second token
        torch.tensor([[1, 2, 3, 10, 20, 999]])  # EOS token
    ]
    
    # Test streaming inference
    tokens = list(backend.stream_infer("Hello", max_tokens=3))
    
    assert len(tokens) == 3
    assert tokens == ["token1", "token2", "token3"]

def test_llama_gpu_batch_inference():
    """Test LlamaGPU batch inference interface."""
    from llama_gpu import LlamaGPU
    
    with patch('backend.cpu_backend.CPUBackend.load_model'), \
         patch('backend.cpu_backend.CPUBackend.batch_infer', return_value=["output1", "output2"]):
        
        llama = LlamaGPU("test-model", prefer_gpu=False)
        results = llama.batch_infer(["input1", "input2"])
        
        assert results == ["output1", "output2"]

def test_llama_gpu_streaming_inference():
    """Test LlamaGPU streaming inference interface."""
    from llama_gpu import LlamaGPU
    
    with patch('backend.cpu_backend.CPUBackend.load_model'), \
         patch('backend.cpu_backend.CPUBackend.stream_infer', return_value=iter(["token1", "token2"])):
        
        llama = LlamaGPU("test-model", prefer_gpu=False)
        tokens = list(llama.stream_infer("Hello", max_tokens=2))
        
        assert tokens == ["token1", "token2"]

def test_batch_size_handling():
    """Test batch size handling in batch inference."""
    from backend.cpu_backend import CPUBackend
    
    backend = CPUBackend()
    backend.model = Mock()
    backend.tokenizer = Mock()
    
    # Mock tokenizer behavior for multiple calls
    backend.tokenizer.side_effect = [
        {'input_ids': torch.tensor([[1, 2, 3], [4, 5, 6]])},  # First batch
        {'input_ids': torch.tensor([[7, 8, 9], [10, 11, 12]])}  # Second batch
    ]
    backend.tokenizer.decode.return_value = "mocked output"
    backend.model.generate.side_effect = [
        torch.tensor([[1, 2, 3, 4], [4, 5, 6, 7]]),  # First batch output
        torch.tensor([[7, 8, 9, 10], [10, 11, 12, 13]])  # Second batch output
    ]
    
    # Test with different batch sizes
    inputs = ["input1", "input2", "input3", "input4"]
    
    # Test with batch_size=2
    results = backend.batch_infer(inputs, batch_size=2)
    assert len(results) == 4
    
    # Test with batch_size=None (should process all at once)
    # Reset mocks and set up for single batch processing
    backend.tokenizer.reset_mock()
    backend.model.generate.reset_mock()
    backend.tokenizer.side_effect = None
    backend.model.generate.side_effect = None
    backend.tokenizer.return_value = {'input_ids': torch.tensor([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])}
    backend.model.generate.return_value = torch.tensor([[1, 2, 3, 4], [4, 5, 6, 7], [7, 8, 9, 10], [10, 11, 12, 13]])
    
    results = backend.batch_infer(inputs, batch_size=None)
    assert len(results) == 4

def test_empty_batch_input():
    """Test handling of empty batch input."""
    from backend.cpu_backend import CPUBackend
    
    backend = CPUBackend()
    backend.model = Mock()
    backend.tokenizer = Mock()
    
    # Test with empty list
    results = backend.batch_infer([])
    assert results == []
    
    # Verify no calls to model or tokenizer
    assert not backend.tokenizer.called
    assert not backend.model.generate.called 