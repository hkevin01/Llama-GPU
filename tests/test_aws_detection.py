"""Tests for AWS GPU instance detection."""

import pytest
from unittest.mock import patch, Mock
import requests

def test_get_aws_instance_metadata_not_aws():
    """Test AWS metadata detection when not on AWS."""
    from utils.aws_detection import get_aws_instance_metadata
    
    with patch('requests.get', side_effect=requests.RequestException("Connection failed")):
        result = get_aws_instance_metadata()
        assert result is None

def test_get_aws_instance_metadata_on_aws():
    """Test AWS metadata detection when on AWS."""
    from utils.aws_detection import get_aws_instance_metadata
    
    mock_response = Mock()
    mock_response.status_code = 200
    
    with patch('requests.get', return_value=mock_response):
        result = get_aws_instance_metadata()
        assert result == {"available": True}

def test_get_aws_instance_type():
    """Test getting AWS instance type."""
    from utils.aws_detection import get_aws_instance_type
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "p3.2xlarge"
    
    with patch('requests.get', return_value=mock_response):
        result = get_aws_instance_type()
        assert result == "p3.2xlarge"

def test_is_aws_gpu_instance_true():
    """Test AWS GPU instance detection for GPU instances."""
    from utils.aws_detection import is_aws_gpu_instance
    
    with patch('utils.aws_detection.get_aws_instance_type', return_value="p3.2xlarge"):
        result = is_aws_gpu_instance()
        assert result is True

def test_is_aws_gpu_instance_false():
    """Test AWS GPU instance detection for non-GPU instances."""
    from utils.aws_detection import is_aws_gpu_instance
    
    with patch('utils.aws_detection.get_aws_instance_type', return_value="t3.micro"):
        result = is_aws_gpu_instance()
        assert result is False

def test_get_aws_gpu_info():
    """Test getting AWS GPU information."""
    from utils.aws_detection import get_aws_gpu_info
    
    with patch('utils.aws_detection.is_aws_gpu_instance', return_value=True), \
         patch('utils.aws_detection.get_aws_instance_type', return_value="p3.2xlarge"):
        
        result = get_aws_gpu_info()
        assert result == {
            'gpu_count': 1,
            'gpu_type': 'Tesla V100',
            'memory_gb': 16
        }

def test_get_optimal_aws_backend_cuda():
    """Test optimal backend selection for NVIDIA GPU instances."""
    from utils.aws_detection import get_optimal_aws_backend
    
    with patch('utils.aws_detection.is_aws_gpu_instance', return_value=True), \
         patch('utils.aws_detection.get_aws_gpu_info', return_value={'gpu_type': 'Tesla V100'}):
        
        result = get_optimal_aws_backend()
        assert result == 'cuda'

def test_get_optimal_aws_backend_cpu():
    """Test optimal backend selection for non-GPU instances."""
    from utils.aws_detection import get_optimal_aws_backend
    
    with patch('utils.aws_detection.is_aws_gpu_instance', return_value=False):
        result = get_optimal_aws_backend()
        assert result == 'cpu'

def test_llama_gpu_aws_detection():
    """Test LlamaGPU AWS detection integration."""
    from llama_gpu import LlamaGPU
    
    with patch('utils.aws_detection.is_aws_gpu_instance', return_value=True), \
         patch('utils.aws_detection.get_optimal_aws_backend', return_value='cuda'), \
         patch('utils.aws_detection.get_aws_gpu_info', return_value={'gpu_type': 'Tesla V100'}), \
         patch('backend.cuda_backend.CUDABackend.is_available', return_value=True), \
         patch('backend.cuda_backend.CUDABackend.load_model'):
        
        llama = LlamaGPU("test-model", prefer_gpu=True, auto_detect_aws=True)
        assert llama.backend.__class__.__name__ == "CUDABackend"

def test_llama_gpu_aws_fallback():
    """Test LlamaGPU AWS detection with fallback to CPU."""
    from llama_gpu import LlamaGPU
    
    with patch('utils.aws_detection.is_aws_gpu_instance', return_value=True), \
         patch('utils.aws_detection.get_optimal_aws_backend', return_value='cuda'), \
         patch('utils.aws_detection.get_aws_gpu_info', return_value={'gpu_type': 'Tesla V100'}), \
         patch('backend.cuda_backend.CUDABackend.is_available', return_value=False), \
         patch('backend.cpu_backend.CPUBackend.load_model'):
        
        llama = LlamaGPU("test-model", prefer_gpu=True, auto_detect_aws=True)
        assert llama.backend.__class__.__name__ == "CPUBackend"

def test_llama_gpu_backend_info():
    """Test LlamaGPU backend information retrieval."""
    from llama_gpu import LlamaGPU

    with patch('backend.cpu_backend.CPUBackend.load_model'), \
         patch('llama_gpu.is_aws_gpu_instance', return_value=True), \
         patch('llama_gpu.get_aws_gpu_info', return_value={'gpu_type': 'Tesla V100'}), \
         patch('llama_gpu.get_optimal_aws_backend', return_value='cpu'), \
         patch('backend.cuda_backend.CUDABackend.is_available', return_value=False), \
         patch('backend.rocm_backend.ROCMBackend.is_available', return_value=False), \
         patch('builtins.print'):  # Suppress print output

        llama = LlamaGPU("test-model", prefer_gpu=False, auto_detect_aws=True)
        info = llama.get_backend_info()
        
        print(f"DEBUG: info = {info}")  # Debug output
        assert info['backend_type'] == 'CPUBackend'
        assert info['model_path'] == 'test-model'
        assert info['prefer_gpu'] is False
        assert info['auto_detect_aws'] is True
        assert info['aws_instance'] is True
        assert info['aws_gpu_info'] == {'gpu_type': 'Tesla V100'} 