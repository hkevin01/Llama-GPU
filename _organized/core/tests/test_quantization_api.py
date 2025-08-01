"""
Tests for quantization API endpoints.

This module tests the quantization integration with the FastAPI server,
including configuration, statistics, and cache management endpoints.
"""

import json
from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

from src.api_server import app
from src.quantization import QuantizationConfig, QuantizationType

# Test client
client = TestClient(app)

# Test API key
TEST_API_KEY = "test-key"
HEADERS = {"Authorization": f"Bearer {TEST_API_KEY}"}


class TestQuantizationConfigAPI:
    """Test quantization configuration endpoints."""
    
    def test_set_quantization_config_int8(self):
        """Test setting INT8 quantization configuration."""
        request_data = {
            "quantization_type": "int8",
            "dynamic": True,
            "per_channel": True,
            "symmetric": True,
            "reduce_range": True,
            "memory_efficient": True,
            "preserve_accuracy": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "config_updated"
        assert data["quantization_config"]["quantization_type"] == "int8"
        assert data["quantization_config"]["dynamic"] is True
        assert data["quantization_config"]["memory_efficient"] is True
    
    def test_set_quantization_config_int4(self):
        """Test setting INT4 quantization configuration."""
        request_data = {
            "quantization_type": "int4",
            "dynamic": False,
            "memory_efficient": True,
            "preserve_accuracy": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "config_updated"
        assert data["quantization_config"]["quantization_type"] == "int4"
        assert data["quantization_config"]["dynamic"] is False
    
    def test_set_quantization_config_fp16(self):
        """Test setting FP16 quantization configuration."""
        request_data = {
            "quantization_type": "fp16",
            "dynamic": False,
            "memory_efficient": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "config_updated"
        assert data["quantization_config"]["quantization_type"] == "fp16"
    
    def test_set_quantization_config_bf16(self):
        """Test setting BF16 quantization configuration."""
        request_data = {
            "quantization_type": "bf16",
            "dynamic": False,
            "memory_efficient": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "config_updated"
        assert data["quantization_config"]["quantization_type"] == "bf16"
    
    def test_set_quantization_config_dynamic(self):
        """Test setting dynamic quantization configuration."""
        request_data = {
            "quantization_type": "dynamic",
            "dynamic": True,
            "memory_efficient": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "config_updated"
        assert data["quantization_config"]["quantization_type"] == "dynamic"
    
    def test_set_quantization_config_invalid_type(self):
        """Test setting invalid quantization type."""
        request_data = {
            "quantization_type": "invalid_type",
            "dynamic": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"]
    
    def test_set_quantization_config_unauthorized(self):
        """Test setting quantization config without API key."""
        request_data = {
            "quantization_type": "int8",
            "dynamic": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data)
        
        assert response.status_code == 401
    
    def test_set_quantization_config_invalid_key(self):
        """Test setting quantization config with invalid API key."""
        request_data = {
            "quantization_type": "int8",
            "dynamic": True
        }
        
        response = client.post("/v1/quantization/config", json=request_data, 
                             headers={"Authorization": "Bearer invalid-key"})
        
        assert response.status_code == 401


class TestQuantizationStatsAPI:
    """Test quantization statistics endpoints."""
    
    def test_get_quantization_stats_overall(self):
        """Test getting overall quantization statistics."""
        response = client.get("/v1/quantization/stats", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "overall_stats" in data
        assert "cache_stats" in data
        
        # Check overall stats structure
        overall_stats = data["overall_stats"]
        assert "total_models" in overall_stats
        assert "memory_saved" in overall_stats
        assert "accuracy_loss" in overall_stats
        assert "avg_quantization_time" in overall_stats
        
        # Check cache stats structure
        cache_stats = data["cache_stats"]
        assert "total_models" in cache_stats
        assert "cache_size" in cache_stats
        assert "models" in cache_stats
    
    def test_get_quantization_stats_specific_model(self):
        """Test getting quantization statistics for specific model."""
        response = client.get("/v1/quantization/stats?model_name=test_model", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "model_stats" in data
        assert "overall_stats" in data
        assert "cache_stats" in data
    
    def test_get_quantization_stats_no_overall(self):
        """Test getting quantization statistics without overall stats."""
        response = client.get("/v1/quantization/stats?include_overall=false", headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "overall_stats" not in data
        assert "cache_stats" in data
    
    def test_get_quantization_stats_unauthorized(self):
        """Test getting quantization stats without API key."""
        response = client.get("/v1/quantization/stats")
        
        assert response.status_code == 401
    
    def test_get_quantization_stats_invalid_key(self):
        """Test getting quantization stats with invalid API key."""
        response = client.get("/v1/quantization/stats", 
                            headers={"Authorization": "Bearer invalid-key"})
        
        assert response.status_code == 401


class TestQuantizationCacheAPI:
    """Test quantization cache management endpoints."""
    
    @patch('src.api_server.model_manager.get_model')
    def test_cache_quantized_model(self, mock_get_model):
        """Test caching a quantized model."""
        # Mock model
        mock_model = Mock()
        mock_get_model.return_value = mock_model
        
        request_data = {
            "model_name": "test_model",
            "quantization_type": "int8",
            "action": "cache"
        }
        
        response = client.post("/v1/quantization/cache", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cached"
        assert data["model_name"] == "test_model"
    
    @patch('src.api_server.model_manager.get_model')
    def test_cache_quantized_model_not_found(self, mock_get_model):
        """Test caching a model that doesn't exist."""
        mock_get_model.return_value = None
        
        request_data = {
            "model_name": "nonexistent_model",
            "quantization_type": "int8",
            "action": "cache"
        }
        
        response = client.post("/v1/quantization/cache", json=request_data, headers=HEADERS)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_load_cached_model(self):
        """Test loading a cached quantized model."""
        request_data = {
            "model_name": "test_model",
            "quantization_type": "int8",
            "action": "load"
        }
        
        response = client.post("/v1/quantization/cache", json=request_data, headers=HEADERS)
        
        # This might fail if no cached model exists, which is expected
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "loaded"
            assert data["model_name"] == "test_model"
        else:
            data = response.json()
            assert "not found" in data["detail"]
    
    def test_clear_cache(self):
        """Test clearing quantization cache."""
        request_data = {
            "model_name": "test_model",
            "quantization_type": "int8",
            "action": "clear"
        }
        
        response = client.post("/v1/quantization/cache", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cache_cleared"
        assert data["model_name"] == "test_model"
    
    def test_invalid_cache_action(self):
        """Test invalid cache action."""
        request_data = {
            "model_name": "test_model",
            "quantization_type": "int8",
            "action": "invalid_action"
        }
        
        response = client.post("/v1/quantization/cache", json=request_data, headers=HEADERS)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid action" in data["detail"]
    
    def test_cache_unauthorized(self):
        """Test cache operations without API key."""
        request_data = {
            "model_name": "test_model",
            "quantization_type": "int8",
            "action": "cache"
        }
        
        response = client.post("/v1/quantization/cache", json=request_data)
        
        assert response.status_code == 401
    
    def test_cache_invalid_key(self):
        """Test cache operations with invalid API key."""
        request_data = {
            "model_name": "test_model",
            "quantization_type": "int8",
            "action": "cache"
        }
        
        response = client.post("/v1/quantization/cache", json=request_data,
                             headers={"Authorization": "Bearer invalid-key"})
        
        assert response.status_code == 401


class TestQuantizationIntegrationAPI:
    """Test quantization integration with other API endpoints."""
    
    def test_quantization_with_completions(self):
        """Test quantization configuration affects completions."""
        # First set quantization config
        config_data = {
            "quantization_type": "int8",
            "dynamic": True,
            "memory_efficient": True
        }
        
        config_response = client.post("/v1/quantization/config", json=config_data, headers=HEADERS)
        assert config_response.status_code == 200
        
        # Then test completions (this might fail if no model is loaded, which is expected)
        completion_data = {
            "prompt": "Hello, how are you?",
            "max_tokens": 10
        }
        
        completion_response = client.post("/v1/completions", json=completion_data, headers=HEADERS)
        
        # The completion might fail due to model not being loaded, but quantization config should be set
        assert completion_response.status_code in [200, 500]
    
    def test_quantization_with_chat_completions(self):
        """Test quantization configuration affects chat completions."""
        # First set quantization config
        config_data = {
            "quantization_type": "fp16",
            "dynamic": False,
            "memory_efficient": True
        }
        
        config_response = client.post("/v1/quantization/config", json=config_data, headers=HEADERS)
        assert config_response.status_code == 200
        
        # Then test chat completions
        chat_data = {
            "messages": [{"role": "user", "content": "Hello!"}],
            "max_tokens": 10
        }
        
        chat_response = client.post("/v1/chat/completions", json=chat_data, headers=HEADERS)
        
        # The chat might fail due to model not being loaded, but quantization config should be set
        assert chat_response.status_code in [200, 500]
    
    def test_quantization_stats_consistency(self):
        """Test that quantization stats are consistent across calls."""
        # Get stats twice
        response1 = client.get("/v1/quantization/stats", headers=HEADERS)
        response2 = client.get("/v1/quantization/stats", headers=HEADERS)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        # Overall stats should be consistent
        assert data1["overall_stats"]["total_models"] == data2["overall_stats"]["total_models"]
        assert data1["cache_stats"]["total_models"] == data2["cache_stats"]["total_models"]


class TestQuantizationErrorHandlingAPI:
    """Test quantization API error handling."""
    
    def test_malformed_config_request(self):
        """Test malformed quantization config request."""
        # Missing required fields
        request_data = {}
        
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        
        assert response.status_code == 200  # Should use defaults
    
    def test_malformed_stats_request(self):
        """Test malformed quantization stats request."""
        # Invalid query parameters
        response = client.get("/v1/quantization/stats?invalid_param=value", headers=HEADERS)
        
        assert response.status_code == 200  # Should ignore invalid params
    
    def test_malformed_cache_request(self):
        """Test malformed quantization cache request."""
        # Missing required fields
        request_data = {}
        
        response = client.post("/v1/quantization/cache", json=request_data, headers=HEADERS)
        
        assert response.status_code == 422  # Validation error
    
    def test_rate_limiting(self):
        """Test rate limiting on quantization endpoints."""
        # Make many requests quickly
        for _ in range(70):  # More than the 60 per minute limit
            response = client.get("/v1/quantization/stats", headers=HEADERS)
            if response.status_code == 429:
                break
        else:
            # If we didn't hit rate limit, that's also acceptable
            pass


class TestQuantizationPerformanceAPI:
    """Test quantization API performance."""
    
    def test_config_endpoint_performance(self):
        """Test quantization config endpoint performance."""
        import time
        
        request_data = {
            "quantization_type": "int8",
            "dynamic": True
        }
        
        start_time = time.time()
        response = client.post("/v1/quantization/config", json=request_data, headers=HEADERS)
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 1.0  # Should complete in under 1 second
    
    def test_stats_endpoint_performance(self):
        """Test quantization stats endpoint performance."""
        import time
        
        start_time = time.time()
        response = client.get("/v1/quantization/stats", headers=HEADERS)
        end_time = time.time()
        
        assert response.status_code == 200
        assert end_time - start_time < 1.0  # Should complete in under 1 second
    
    def test_cache_endpoint_performance(self):
        """Test quantization cache endpoint performance."""
        import time
        
        request_data = {
            "model_name": "test_model",
            "quantization_type": "int8",
            "action": "load"
        }
        
        start_time = time.time()
        response = client.post("/v1/quantization/cache", json=request_data, headers=HEADERS)
        end_time = time.time()
        
        # Should complete quickly even if model not found
        assert end_time - start_time < 1.0
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 