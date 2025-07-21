"""
Tests for quantization module.

This module tests INT8/INT4 quantization, dynamic quantization,
quantized model management, and performance benchmarking.
"""

import os
import tempfile
import time
from unittest.mock import Mock, patch

import pytest
import torch
import torch.nn as nn
from torch.ao.quantization import QConfig

from src.quantization import (
    QuantizationCache,
    QuantizationConfig,
    QuantizationManager,
    QuantizationType,
    QuantizedInference,
)
from utils.quantization import apply_quantization
from backend.cpu_backend import CPUBackend


class SimpleModel(nn.Module):
    """Simple model for testing quantization."""
    
    def __init__(self, vocab_size=1000, hidden_size=128):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.linear1 = nn.Linear(hidden_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, vocab_size)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.embedding(x)
        x = self.relu(self.linear1(x))
        x = self.linear2(x)
        return x


@pytest.fixture
def simple_model():
    """Create a simple model for testing."""
    return SimpleModel()


@pytest.fixture
def quantization_config():
    """Create a basic quantization configuration."""
    return QuantizationConfig(
        quantization_type=QuantizationType.INT8,
        dynamic=True,
        memory_efficient=True
    )


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


class TestQuantizationConfig:
    """Test quantization configuration."""
    
    def test_config_creation(self):
        """Test creating quantization configuration."""
        config = QuantizationConfig(
            quantization_type=QuantizationType.INT8,
            dynamic=True,
            per_channel=True
        )
        
        assert config.quantization_type == QuantizationType.INT8
        assert config.dynamic is True
        assert config.per_channel is True
        assert config.symmetric is True  # default
        assert config.reduce_range is True  # default
    
    def test_config_defaults(self):
        """Test configuration defaults."""
        config = QuantizationConfig()
        
        assert config.quantization_type == QuantizationType.INT8
        assert config.dynamic is True
        assert config.per_channel is True
        assert config.symmetric is True
        assert config.reduce_range is True
        assert config.memory_efficient is True
        assert config.preserve_accuracy is True


class TestQuantizationManager:
    """Test quantization manager functionality."""
    
    def test_manager_initialization(self, quantization_config):
        """Test quantization manager initialization."""
        manager = QuantizationManager(quantization_config)
        
        assert manager.config == quantization_config
        assert manager.quantized_models == {}
        assert manager.quantization_stats["total_models"] == 0
        assert manager.quantization_stats["memory_saved"] == 0.0
    
    def test_dynamic_quantization(self, simple_model, quantization_config):
        """Test dynamic quantization."""
        manager = QuantizationManager(quantization_config)
        
        # Change to dynamic quantization
        manager.config.quantization_type = QuantizationType.DYNAMIC
        
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        assert quantized_model is not None
        assert "test_model" in manager.quantized_models
        assert manager.quantization_stats["total_models"] == 1
    
    def test_int8_quantization(self, simple_model, quantization_config):
        """Test INT8 quantization."""
        manager = QuantizationManager(quantization_config)
        manager.config.quantization_type = QuantizationType.INT8
        
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        assert quantized_model is not None
        assert "test_model" in manager.quantized_models
    
    def test_int4_quantization(self, simple_model, quantization_config):
        """Test INT4 quantization."""
        manager = QuantizationManager(quantization_config)
        manager.config.quantization_type = QuantizationType.INT4
        
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        assert quantized_model is not None
        assert "test_model" in manager.quantized_models
    
    def test_fp16_quantization(self, simple_model, quantization_config):
        """Test FP16 quantization."""
        manager = QuantizationManager(quantization_config)
        manager.config.quantization_type = QuantizationType.FP16
        
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        assert quantized_model is not None
        assert "test_model" in manager.quantized_models
    
    def test_bf16_quantization(self, simple_model, quantization_config):
        """Test BF16 quantization."""
        manager = QuantizationManager(quantization_config)
        manager.config.quantization_type = QuantizationType.BF16
        
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        assert quantized_model is not None
        assert "test_model" in manager.quantized_models
    
    def test_invalid_quantization_type(self, simple_model, quantization_config):
        """Test handling of invalid quantization type."""
        manager = QuantizationManager(quantization_config)
        manager.config.quantization_type = "invalid"
        
        with pytest.raises(ValueError, match="Unsupported quantization type"):
            manager.quantize_model(simple_model, "test_model")
    
    def test_get_quantized_model(self, simple_model, quantization_config):
        """Test retrieving quantized model."""
        manager = QuantizationManager(quantization_config)
        manager.quantize_model(simple_model, "test_model")
        
        retrieved_model = manager.get_quantized_model("test_model")
        assert retrieved_model is not None
        
        # Test non-existent model
        non_existent = manager.get_quantized_model("non_existent")
        assert non_existent is None
    
    def test_get_quantization_stats(self, simple_model, quantization_config):
        """Test getting quantization statistics."""
        manager = QuantizationManager(quantization_config)
        manager.quantize_model(simple_model, "test_model")
        
        stats = manager.get_quantization_stats("test_model")
        assert "model_name" in stats
        assert "quantization_type" in stats
        assert "memory_saved" in stats
        assert "quantization_time" in stats
    
    def test_get_overall_stats(self, simple_model, quantization_config):
        """Test getting overall statistics."""
        manager = QuantizationManager(quantization_config)
        manager.quantize_model(simple_model, "test_model1")
        manager.quantize_model(simple_model, "test_model2")
        
        overall_stats = manager.get_overall_stats()
        assert overall_stats["total_models"] == 2
        assert "memory_saved" in overall_stats
        assert "accuracy_loss" in overall_stats
        assert "quantization_times" in overall_stats


class TestQuantizedInference:
    """Test quantized inference functionality."""
    
    def test_inference_initialization(self, simple_model, quantization_config):
        """Test quantized inference initialization."""
        manager = QuantizationManager(quantization_config)
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        inference = QuantizedInference(quantized_model, quantization_config)
        
        assert inference.quantized_model == quantized_model
        assert inference.config == quantization_config
        assert inference.tokenizer is None  # No tokenizer provided
    
    @patch('src.quantization.AutoTokenizer.from_pretrained')
    def test_generate_with_tokenizer(self, mock_tokenizer, simple_model, quantization_config):
        """Test generation with tokenizer."""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.encode.return_value = [1, 2, 3, 4]
        mock_tokenizer_instance.decode.return_value = "Generated text"
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        manager = QuantizationManager(quantization_config)
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        inference = QuantizedInference(quantized_model, quantization_config)
        
        # Mock the model forward pass
        with patch.object(quantized_model, 'forward') as mock_forward:
            mock_forward.return_value = torch.randn(1, 4, 1000)  # batch, seq_len, vocab_size
            
            result = inference.generate("Hello", max_tokens=10)
            
            assert isinstance(result, str)
            assert "Generated text" in result
    
    def test_generate_without_tokenizer(self, simple_model, quantization_config):
        """Test generation without tokenizer."""
        manager = QuantizationManager(quantization_config)
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        inference = QuantizedInference(quantized_model, quantization_config)
        
        # Mock the model forward pass
        with patch.object(quantized_model, 'forward') as mock_forward:
            mock_forward.return_value = torch.randn(1, 4, 1000)
            
            result = inference.generate("Hello", max_tokens=10)
            
            assert isinstance(result, str)
            assert "Generated text" in result  # Default fallback
    
    def test_benchmark_performance(self, simple_model, quantization_config):
        """Test performance benchmarking."""
        manager = QuantizationManager(quantization_config)
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        inference = QuantizedInference(quantized_model, quantization_config)
        
        test_prompts = ["Hello", "How are you?", "Tell me a story"]
        
        # Mock the model forward pass
        with patch.object(quantized_model, 'forward') as mock_forward:
            mock_forward.return_value = torch.randn(1, 4, 1000)
            
            benchmark_results = inference.benchmark_performance(test_prompts, max_tokens=10)
            
            assert "total_time" in benchmark_results
            assert "avg_time_per_prompt" in benchmark_results
            assert "tokens_per_second" in benchmark_results
            assert "memory_usage" in benchmark_results
            assert "throughput" in benchmark_results


class TestQuantizationCache:
    """Test quantization cache functionality."""
    
    def test_cache_initialization(self, temp_cache_dir):
        """Test cache initialization."""
        cache = QuantizationCache(temp_cache_dir)
        
        assert cache.cache_dir == temp_cache_dir
        assert cache.cache_index == {}
        assert os.path.exists(temp_cache_dir)
    
    def test_cache_model(self, simple_model, quantization_config, temp_cache_dir):
        """Test caching a quantized model."""
        cache = QuantizationCache(temp_cache_dir)
        
        # Mock the model saving
        with patch('torch.save') as mock_save:
            cache.cache_model("test_model", simple_model, quantization_config)
            
            mock_save.assert_called_once()
            assert "test_model" in cache.cache_index
    
    def test_load_cached_model(self, simple_model, quantization_config, temp_cache_dir):
        """Test loading a cached model."""
        cache = QuantizationCache(temp_cache_dir)
        
        # First cache the model
        with patch('torch.save'):
            cache.cache_model("test_model", simple_model, quantization_config)
        
        # Then load it
        with patch('torch.load') as mock_load:
            mock_load.return_value = simple_model.state_dict()
            
            loaded_model = cache.load_cached_model("test_model", QuantizationType.INT8)
            
            assert loaded_model is not None
            mock_load.assert_called_once()
    
    def test_load_nonexistent_model(self, temp_cache_dir):
        """Test loading a non-existent cached model."""
        cache = QuantizationCache(temp_cache_dir)
        
        loaded_model = cache.load_cached_model("nonexistent", QuantizationType.INT8)
        
        assert loaded_model is None
    
    def test_get_cache_stats(self, simple_model, quantization_config, temp_cache_dir):
        """Test getting cache statistics."""
        cache = QuantizationCache(temp_cache_dir)
        
        # Cache a model
        with patch('torch.save'):
            cache.cache_model("test_model", simple_model, quantization_config)
        
        stats = cache.get_cache_stats()
        
        assert "total_models" in stats
        assert "cache_size" in stats
        assert "models" in stats
        assert stats["total_models"] == 1


class TestQuantizationIntegration:
    """Integration tests for quantization functionality."""
    
    def test_full_quantization_pipeline(self, simple_model, quantization_config):
        """Test complete quantization pipeline."""
        # Initialize manager
        manager = QuantizationManager(quantization_config)
        
        # Quantize model
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        # Create inference engine
        inference = QuantizedInference(quantized_model, quantization_config)
        
        # Test generation
        with patch.object(quantized_model, 'forward') as mock_forward:
            mock_forward.return_value = torch.randn(1, 4, 1000)
            
            result = inference.generate("Test prompt", max_tokens=5)
            
            assert isinstance(result, str)
        
        # Check statistics
        stats = manager.get_overall_stats()
        assert stats["total_models"] == 1
        assert "memory_saved" in stats
    
    def test_multiple_quantization_types(self, simple_model):
        """Test multiple quantization types."""
        quantization_types = [
            QuantizationType.INT8,
            QuantizationType.INT4,
            QuantizationType.FP16,
            QuantizationType.BF16,
            QuantizationType.DYNAMIC
        ]
        
        for qtype in quantization_types:
            config = QuantizationConfig(quantization_type=qtype)
            manager = QuantizationManager(config)
            
            quantized_model = manager.quantize_model(simple_model, f"test_{qtype.value}")
            
            assert quantized_model is not None
            assert f"test_{qtype.value}" in manager.quantized_models
    
    def test_cache_integration(self, simple_model, quantization_config, temp_cache_dir):
        """Test cache integration with quantization pipeline."""
        cache = QuantizationCache(temp_cache_dir)
        manager = QuantizationManager(quantization_config)
        
        # Quantize and cache model
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        with patch('torch.save'):
            cache.cache_model("test_model", quantized_model, quantization_config)
        
        # Load from cache
        with patch('torch.load') as mock_load:
            mock_load.return_value = simple_model.state_dict()
            
            cached_model = cache.load_cached_model("test_model", QuantizationType.INT8)
            
            assert cached_model is not None
        
        # Check cache stats
        stats = cache.get_cache_stats()
        assert stats["total_models"] == 1


class TestQuantizationPerformance:
    """Performance tests for quantization."""
    
    def test_memory_savings(self, simple_model, quantization_config):
        """Test memory savings from quantization."""
        manager = QuantizationManager(quantization_config)
        
        # Get original model size
        original_size = manager._get_model_size(simple_model)
        
        # Quantize model
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        # Get quantized model size
        quantized_size = manager._get_model_size(quantized_model)
        
        # Check that quantized model is smaller or equal
        assert quantized_size <= original_size
        
        # Check statistics
        stats = manager.get_quantization_stats("test_model")
        assert stats["memory_saved"] >= 0
    
    def test_quantization_speed(self, simple_model, quantization_config):
        """Test quantization speed."""
        manager = QuantizationManager(quantization_config)
        
        start_time = time.time()
        quantized_model = manager.quantize_model(simple_model, "test_model")
        end_time = time.time()
        
        quantization_time = end_time - start_time
        
        # Check that quantization completes in reasonable time (< 10 seconds)
        assert quantization_time < 10.0
        
        # Check statistics
        stats = manager.get_quantization_stats("test_model")
        assert stats["quantization_time"] > 0
    
    def test_inference_speed(self, simple_model, quantization_config):
        """Test quantized inference speed."""
        manager = QuantizationManager(quantization_config)
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        inference = QuantizedInference(quantized_model, quantization_config)
        
        test_prompts = ["Hello", "How are you?", "Tell me a story"]
        
        # Mock the model forward pass
        with patch.object(quantized_model, 'forward') as mock_forward:
            mock_forward.return_value = torch.randn(1, 4, 1000)
            
            start_time = time.time()
            benchmark_results = inference.benchmark_performance(test_prompts, max_tokens=10)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Check that inference completes in reasonable time
            assert total_time < 5.0
            assert benchmark_results["total_time"] > 0
            assert benchmark_results["avg_time_per_prompt"] > 0


class TestQuantizationErrorHandling:
    """Test error handling in quantization."""
    
    def test_invalid_model_quantization(self, quantization_config):
        """Test quantization with invalid model."""
        manager = QuantizationManager(quantization_config)
        
        # Test with None model
        with pytest.raises(Exception):
            manager.quantize_model(None, "test_model")
    
    def test_invalid_config_quantization(self, simple_model):
        """Test quantization with invalid configuration."""
        # Test with None config
        with pytest.raises(Exception):
            manager = QuantizationManager(None)
            manager.quantize_model(simple_model, "test_model")
    
    def test_cache_errors(self, temp_cache_dir):
        """Test cache error handling."""
        cache = QuantizationCache(temp_cache_dir)
        
        # Test with invalid model
        with pytest.raises(Exception):
            cache.cache_model("test_model", None, None)
    
    def test_inference_errors(self, simple_model, quantization_config):
        """Test inference error handling."""
        manager = QuantizationManager(quantization_config)
        quantized_model = manager.quantize_model(simple_model, "test_model")
        
        inference = QuantizedInference(quantized_model, quantization_config)
        
        # Test with invalid prompt
        with pytest.raises(Exception):
            inference.generate(None, max_tokens=10)
        
        # Test with invalid max_tokens
        with pytest.raises(Exception):
            inference.generate("Hello", max_tokens=-1)


class TestQuantizationUtilsAndBackend:
    """Test quantization utilities and backend integration."""
    
    def log_test_result(test_name, result):
        with open('logs/test_output.log', 'a') as f:
            f.write(f"{test_name}: {result}\n")

    def test_apply_int8_quantization(self):
        model = torch.nn.Linear(10, 10)
        quantized_model = apply_quantization(model, quant_type="int8")
        result = hasattr(quantized_model, 'weight') and isinstance(quantized_model, torch.nn.Module)
        log_test_result('test_apply_int8_quantization', result)
        assert result

    def test_apply_float16_quantization(self):
        model = torch.nn.Linear(10, 10)
        quantized_model = apply_quantization(model, quant_type="float16")
        result = quantized_model.weight.dtype == torch.float16
        log_test_result('test_apply_float16_quantization', result)
        assert result

    def test_cpu_backend_quantized_load(self):
        backend = CPUBackend()
        backend.model = torch.nn.Linear(10, 10)
        backend.model = apply_quantization(backend.model, quant_type="int8")
        result = isinstance(backend.model, torch.nn.Module)
        log_test_result('test_cpu_backend_quantized_load', result)
        assert result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])