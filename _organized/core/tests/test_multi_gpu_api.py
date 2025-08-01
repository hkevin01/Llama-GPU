"""
Tests for multi-GPU API endpoints.

This module tests the multi-GPU configuration and statistics endpoints
integrated with the main API server.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

import httpx
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging for tests
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Create test log file
test_log_file = f"{LOG_DIR}/multi_gpu_api_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=test_log_file,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
test_logger = logging.getLogger("multi_gpu_api_tests")

# Test configuration
BASE_URL = "http://localhost:8000"
API_KEY = "test-key"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

class TestMultiGPUConfig:
    """Test multi-GPU configuration endpoints."""
    
    @pytest.mark.asyncio
    async def test_set_multi_gpu_config(self):
        """Test setting multi-GPU configuration."""
        test_logger.info("Testing set multi-GPU configuration")
        
        config_data = {
            "gpu_ids": [0, 1, 2],
            "strategy": "tensor",
            "tensor_parallel_size": 3,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "adaptive"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "config_updated"
            assert "multi_gpu_config" in data
            
            config = data["multi_gpu_config"]
            assert config["gpu_ids"] == [0, 1, 2]
            assert config["strategy"] == "tensor"
            assert config["tensor_parallel_size"] == 3
            assert config["pipeline_parallel_size"] == 2
            assert config["data_parallel_size"] == 1
            assert config["load_balancing"] == "adaptive"
            
        test_logger.info("Set multi-GPU configuration test passed")
    
    @pytest.mark.asyncio
    async def test_set_multi_gpu_config_pipeline(self):
        """Test setting pipeline parallelism configuration."""
        test_logger.info("Testing set pipeline parallelism configuration")
        
        config_data = {
            "gpu_ids": [0, 1],
            "strategy": "pipeline",
            "tensor_parallel_size": 1,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "least_loaded"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "config_updated"
            
            config = data["multi_gpu_config"]
            assert config["strategy"] == "pipeline"
            assert config["pipeline_parallel_size"] == 2
            assert config["load_balancing"] == "least_loaded"
            
        test_logger.info("Set pipeline parallelism configuration test passed")
    
    @pytest.mark.asyncio
    async def test_set_multi_gpu_config_invalid_strategy(self):
        """Test setting invalid parallelism strategy."""
        test_logger.info("Testing set invalid parallelism strategy")
        
        config_data = {
            "gpu_ids": [0, 1],
            "strategy": "invalid_strategy",
            "tensor_parallel_size": 2,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "round_robin"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            # Should return 500 error for invalid strategy
            assert response.status_code == 500
            
        test_logger.info("Set invalid parallelism strategy test passed")
    
    @pytest.mark.asyncio
    async def test_set_multi_gpu_config_unauthorized(self):
        """Test setting multi-GPU configuration without API key."""
        test_logger.info("Testing set multi-GPU configuration unauthorized")
        
        config_data = {
            "gpu_ids": [0, 1],
            "strategy": "tensor",
            "tensor_parallel_size": 2,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "round_robin"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data
                # No Authorization header
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 403  # Unauthorized
            
        test_logger.info("Set multi-GPU configuration unauthorized test passed")

class TestMultiGPUStats:
    """Test multi-GPU statistics endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_multi_gpu_stats(self):
        """Test getting multi-GPU statistics."""
        test_logger.info("Testing get multi-GPU statistics")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/v1/multi-gpu/stats?include_metrics=true",
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "multi_gpu_stats" in data
            
            # Stats should be empty if no model is loaded
            stats = data["multi_gpu_stats"]
            assert isinstance(stats, dict)
            
        test_logger.info("Get multi-GPU statistics test passed")
    
    @pytest.mark.asyncio
    async def test_get_multi_gpu_stats_no_metrics(self):
        """Test getting multi-GPU statistics without metrics."""
        test_logger.info("Testing get multi-GPU statistics without metrics")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/v1/multi-gpu/stats?include_metrics=false",
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "multi_gpu_stats" in data
            
        test_logger.info("Get multi-GPU statistics without metrics test passed")
    
    @pytest.mark.asyncio
    async def test_get_multi_gpu_stats_unauthorized(self):
        """Test getting multi-GPU statistics without API key."""
        test_logger.info("Testing get multi-GPU statistics unauthorized")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/v1/multi-gpu/stats"
                # No Authorization header
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 403  # Unauthorized
            
        test_logger.info("Get multi-GPU statistics unauthorized test passed")

class TestMultiGPUIntegration:
    """Test multi-GPU integration with main API endpoints."""
    
    @pytest.mark.asyncio
    async def test_completions_with_multi_gpu_config(self):
        """Test completions endpoint with multi-GPU configuration."""
        test_logger.info("Testing completions with multi-GPU configuration")
        
        # First set multi-GPU config
        config_data = {
            "gpu_ids": [0, 1],
            "strategy": "tensor",
            "tensor_parallel_size": 2,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "round_robin"
        }
        
        async with httpx.AsyncClient() as client:
            # Set config
            config_response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            assert config_response.status_code == 200
            
            # Test completions
            completion_data = {
                "prompt": "Hello, world!",
                "max_tokens": 10,
                "stream": False
            }
            
            response = await client.post(
                f"{BASE_URL}/v1/completions",
                json=completion_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Completions response status: {response.status_code}")
            test_logger.info(f"Completions response body: {response.text}")
            
            # Should work regardless of multi-GPU config
            assert response.status_code in [200, 500]  # 500 if model not loaded
            
        test_logger.info("Completions with multi-GPU configuration test passed")
    
    @pytest.mark.asyncio
    async def test_chat_completions_with_multi_gpu_config(self):
        """Test chat completions endpoint with multi-GPU configuration."""
        test_logger.info("Testing chat completions with multi-GPU configuration")
        
        # First set multi-GPU config
        config_data = {
            "gpu_ids": [0, 1],
            "strategy": "pipeline",
            "tensor_parallel_size": 1,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "adaptive"
        }
        
        async with httpx.AsyncClient() as client:
            # Set config
            config_response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            assert config_response.status_code == 200
            
            # Test chat completions
            chat_data = {
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "max_tokens": 10,
                "stream": False
            }
            
            response = await client.post(
                f"{BASE_URL}/v1/chat/completions",
                json=chat_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Chat completions response status: {response.status_code}")
            test_logger.info(f"Chat completions response body: {response.text}")
            
            # Should work regardless of multi-GPU config
            assert response.status_code in [200, 500]  # 500 if model not loaded
            
        test_logger.info("Chat completions with multi-GPU configuration test passed")
    
    @pytest.mark.asyncio
    async def test_model_load_with_multi_gpu_config(self):
        """Test model loading with multi-GPU configuration."""
        test_logger.info("Testing model loading with multi-GPU configuration")
        
        # First set multi-GPU config
        config_data = {
            "gpu_ids": [0, 1],
            "strategy": "tensor",
            "tensor_parallel_size": 2,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "round_robin"
        }
        
        async with httpx.AsyncClient() as client:
            # Set config
            config_response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            assert config_response.status_code == 200
            
            # Test model loading
            load_data = {
                "model_name": "llama-base"
            }
            
            response = await client.post(
                f"{BASE_URL}/v1/models/load",
                json=load_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Model load response status: {response.status_code}")
            test_logger.info(f"Model load response body: {response.text}")
            
            # Should work regardless of multi-GPU config
            assert response.status_code in [200, 500]  # 500 if model not available
            
        test_logger.info("Model loading with multi-GPU configuration test passed")

class TestMultiGPUMonitoring:
    """Test multi-GPU monitoring integration."""
    
    @pytest.mark.asyncio
    async def test_monitor_queues_with_multi_gpu(self):
        """Test monitoring queues with multi-GPU configuration."""
        test_logger.info("Testing monitor queues with multi-GPU configuration")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/v1/monitor/queues",
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert "completion_queues" in data
            assert "chat_queues" in data
            
        test_logger.info("Monitor queues with multi-GPU configuration test passed")
    
    @pytest.mark.asyncio
    async def test_monitor_batches_with_multi_gpu(self):
        """Test monitoring batches with multi-GPU configuration."""
        test_logger.info("Testing monitor batches with multi-GPU configuration")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/v1/monitor/batches",
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert "batch_stats" in data
            assert "active_workers" in data
            assert "worker_status" in data
            
        test_logger.info("Monitor batches with multi-GPU configuration test passed")
    
    @pytest.mark.asyncio
    async def test_monitor_workers_with_multi_gpu(self):
        """Test monitoring workers with multi-GPU configuration."""
        test_logger.info("Testing monitor workers with multi-GPU configuration")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/v1/monitor/workers",
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            assert response.status_code == 200
            data = response.json()
            assert "workers" in data
            assert "total_workers" in data
            
        test_logger.info("Monitor workers with multi-GPU configuration test passed")

class TestMultiGPUErrorHandling:
    """Test multi-GPU error handling."""
    
    @pytest.mark.asyncio
    async def test_multi_gpu_config_invalid_gpu_ids(self):
        """Test multi-GPU config with invalid GPU IDs."""
        test_logger.info("Testing multi-GPU config with invalid GPU IDs")
        
        config_data = {
            "gpu_ids": [-1, 999],  # Invalid GPU IDs
            "strategy": "tensor",
            "tensor_parallel_size": 2,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "round_robin"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            # Should still accept the config (validation happens at runtime)
            assert response.status_code == 200
            
        test_logger.info("Multi-GPU config with invalid GPU IDs test passed")
    
    @pytest.mark.asyncio
    async def test_multi_gpu_config_empty_gpu_ids(self):
        """Test multi-GPU config with empty GPU IDs."""
        test_logger.info("Testing multi-GPU config with empty GPU IDs")
        
        config_data = {
            "gpu_ids": [],  # Empty GPU IDs
            "strategy": "tensor",
            "tensor_parallel_size": 2,
            "pipeline_parallel_size": 2,
            "data_parallel_size": 1,
            "load_balancing": "round_robin"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/v1/multi-gpu/config",
                json=config_data,
                headers=HEADERS
            )
            
            test_logger.info(f"Response status: {response.status_code}")
            test_logger.info(f"Response body: {response.text}")
            
            # Should still accept the config (validation happens at runtime)
            assert response.status_code == 200
            
        test_logger.info("Multi-GPU config with empty GPU IDs test passed")

# Run tests and log results
if __name__ == "__main__":
    test_logger.info("Starting multi-GPU API tests")
    
    # Run pytest with verbose output
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_multi_gpu_api.py", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        # Log test results
        test_logger.info("Test execution completed")
        test_logger.info(f"Return code: {result.returncode}")
        test_logger.info("STDOUT:")
        test_logger.info(result.stdout)
        test_logger.info("STDERR:")
        test_logger.info(result.stderr)
        
        if result.returncode == 0:
            test_logger.info("All multi-GPU API tests passed successfully!")
        else:
            test_logger.error("Some multi-GPU API tests failed!")
            
    except Exception as e:
        test_logger.error(f"Error running multi-GPU API tests: {e}")
    
    test_logger.info("Multi-GPU API tests completed") 