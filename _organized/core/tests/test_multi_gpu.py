"""
Tests for multi-GPU functionality.

This module tests tensor parallelism, pipeline parallelism,
load balancing, and GPU management features.
"""

import json
import os
import sys
import time
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
import torch
import torch.nn as nn

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Configure logging for tests
import logging

from multi_gpu import (
    GPUConfig,
    LoadBalancer,
    MultiGPUInference,
    MultiGPUManager,
    ParallelismStrategy,
    ParallelLinear,
    PipelineParallelism,
    TensorParallelism,
)

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Create test log file
test_log_file = f"{LOG_DIR}/multi_gpu_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=test_log_file,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
test_logger = logging.getLogger("multi_gpu_tests")

class TestGPUConfig:
    """Test GPU configuration."""
    
    def test_gpu_config_creation(self):
        """Test GPU configuration creation."""
        test_logger.info("Testing GPU configuration creation")
        
        gpu_ids = [0, 1, 2]
        config = GPUConfig(
            gpu_ids=gpu_ids,
            strategy=ParallelismStrategy.TENSOR,
            tensor_parallel_size=2,
            pipeline_parallel_size=2
        )
        
        assert config.gpu_ids == gpu_ids
        assert config.strategy == ParallelismStrategy.TENSOR
        assert config.tensor_parallel_size == 2
        assert config.pipeline_parallel_size == 2
        assert config.load_balancing == "round_robin"
        
        test_logger.info("GPU configuration creation test passed")

class TestMultiGPUManager:
    """Test multi-GPU manager functionality."""
    
    @pytest.fixture
    def mock_gpu_config(self):
        """Create mock GPU configuration."""
        return GPUConfig(
            gpu_ids=[0, 1],
            strategy=ParallelismStrategy.TENSOR,
            tensor_parallel_size=2
        )
    
    @pytest.fixture
    def gpu_manager(self, mock_gpu_config):
        """Create GPU manager instance."""
        return MultiGPUManager(mock_gpu_config)
    
    def test_gpu_manager_initialization(self, gpu_manager, mock_gpu_config):
        """Test GPU manager initialization."""
        test_logger.info("Testing GPU manager initialization")
        
        assert gpu_manager.config == mock_gpu_config
        assert gpu_manager.gpu_ids == [0, 1]
        assert gpu_manager.num_gpus == 2
        assert len(gpu_manager.devices) == 2
        assert len(gpu_manager.gpu_loads) == 2
        assert len(gpu_manager.gpu_memory) == 2
        assert len(gpu_manager.request_queues) == 2
        
        test_logger.info("GPU manager initialization test passed")
    
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.device_count')
    def test_get_available_gpus(self, mock_device_count, mock_is_available, gpu_manager):
        """Test getting available GPUs."""
        test_logger.info("Testing get available GPUs")
        
        # Mock CUDA availability
        mock_is_available.return_value = True
        mock_device_count.return_value = 4
        
        available = gpu_manager.get_available_gpus()
        assert available == [0, 1]
        
        # Test with fewer available devices
        mock_device_count.return_value = 1
        available = gpu_manager.get_available_gpus()
        assert available == [0]
        
        test_logger.info("Get available GPUs test passed")
    
    def test_gpu_load_management(self, gpu_manager):
        """Test GPU load management."""
        test_logger.info("Testing GPU load management")
        
        # Test initial load
        assert gpu_manager.get_gpu_load(0) == 0.0
        assert gpu_manager.get_gpu_load(1) == 0.0
        
        # Test setting load
        gpu_manager.gpu_loads[0] = 0.5
        assert gpu_manager.get_gpu_load(0) == 0.5
        
        # Test error handling
        assert gpu_manager.get_gpu_load(999) == 0.0
        
        test_logger.info("GPU load management test passed")
    
    @patch('torch.cuda.is_available')
    @patch('torch.cuda.memory_allocated')
    @patch('torch.cuda.get_device_properties')
    def test_gpu_memory_usage(self, mock_properties, mock_allocated, mock_is_available, gpu_manager):
        """Test GPU memory usage calculation."""
        test_logger.info("Testing GPU memory usage")
        
        # Mock CUDA availability
        mock_is_available.return_value = True
        
        # Mock device properties
        mock_prop = Mock()
        mock_prop.total_memory = 1000000000  # 1GB
        mock_properties.return_value = mock_prop
        
        # Mock allocated memory
        mock_allocated.return_value = 500000000  # 500MB
        
        memory_usage = gpu_manager.get_gpu_memory_usage(0)
        assert memory_usage == 0.5
        
        test_logger.info("GPU memory usage test passed")
    
    def test_gpu_selection_strategies(self, gpu_manager):
        """Test different GPU selection strategies."""
        test_logger.info("Testing GPU selection strategies")
        
        # Test round robin
        gpu1 = gpu_manager.select_gpu("round_robin")
        gpu2 = gpu_manager.select_gpu("round_robin")
        assert gpu1 != gpu2 or gpu_manager.num_gpus == 1
        
        # Test least loaded
        gpu_manager.gpu_loads[0] = 0.8
        gpu_manager.gpu_loads[1] = 0.2
        selected = gpu_manager.select_gpu("least_loaded")
        assert selected == 1
        
        # Test adaptive
        gpu_manager.gpu_memory[0] = 0.3
        gpu_manager.gpu_memory[1] = 0.7
        selected = gpu_manager.select_gpu("adaptive")
        # Should prefer GPU with lower combined score
        
        test_logger.info("GPU selection strategies test passed")

class TestTensorParallelism:
    """Test tensor parallelism functionality."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model for testing."""
        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )
        return model
    
    @pytest.fixture
    def mock_gpu_config(self):
        """Create mock GPU configuration."""
        return GPUConfig(
            gpu_ids=[0, 1],
            strategy=ParallelismStrategy.TENSOR,
            tensor_parallel_size=2
        )
    
    def test_tensor_parallelism_initialization(self, mock_model, mock_gpu_config):
        """Test tensor parallelism initialization."""
        test_logger.info("Testing tensor parallelism initialization")
        
        tensor_parallel = TensorParallelism(mock_model, mock_gpu_config)
        
        assert tensor_parallel.model == mock_model
        assert tensor_parallel.config == mock_gpu_config
        assert tensor_parallel.tensor_parallel_size == 2
        assert len(tensor_parallel.devices) == 2
        
        test_logger.info("Tensor parallelism initialization test passed")
    
    def test_tensor_splitting(self, mock_model, mock_gpu_config):
        """Test tensor splitting functionality."""
        test_logger.info("Testing tensor splitting")
        
        tensor_parallel = TensorParallelism(mock_model, mock_gpu_config)
        
        # Test splitting a tensor
        tensor = torch.randn(10, 5)
        splits = tensor_parallel._split_tensor(tensor, 2)
        
        assert len(splits) == 2
        assert splits[0].size(0) == 5
        assert splits[1].size(0) == 5
        assert splits[0].size(1) == 5
        assert splits[1].size(1) == 5
        
        # Test splitting with remainder
        tensor = torch.randn(7, 3)
        splits = tensor_parallel._split_tensor(tensor, 2)
        
        assert len(splits) == 2
        assert splits[0].size(0) == 3
        assert splits[1].size(0) == 4
        
        test_logger.info("Tensor splitting test passed")
    
    def test_parallel_linear_layer(self):
        """Test parallel linear layer."""
        test_logger.info("Testing parallel linear layer")
        
        # Create mock linear layers
        layer1 = nn.Linear(5, 3)
        layer2 = nn.Linear(5, 3)
        
        devices = [torch.device('cpu'), torch.device('cpu')]  # Use CPU for testing
        parallel_layer = ParallelLinear([layer1, layer2], devices)
        
        # Test forward pass
        input_tensor = torch.randn(2, 5)
        output = parallel_layer(input_tensor)
        
        assert output.size(0) == 2
        assert output.size(1) == 6  # 3 + 3 from both layers
        
        test_logger.info("Parallel linear layer test passed")

class TestPipelineParallelism:
    """Test pipeline parallelism functionality."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model for testing."""
        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 15),
            nn.ReLU(),
            nn.Linear(15, 5)
        )
        return model
    
    @pytest.fixture
    def mock_gpu_config(self):
        """Create mock GPU configuration."""
        return GPUConfig(
            gpu_ids=[0, 1],
            strategy=ParallelismStrategy.PIPELINE,
            pipeline_parallel_size=2
        )
    
    def test_pipeline_parallelism_initialization(self, mock_model, mock_gpu_config):
        """Test pipeline parallelism initialization."""
        test_logger.info("Testing pipeline parallelism initialization")
        
        pipeline_parallel = PipelineParallelism(mock_model, mock_gpu_config)
        
        assert pipeline_parallel.model == mock_model
        assert pipeline_parallel.config == mock_gpu_config
        assert len(pipeline_parallel.pipeline_stages) == 2
        
        test_logger.info("Pipeline parallelism initialization test passed")
    
    def test_pipeline_stage_creation(self, mock_model, mock_gpu_config):
        """Test pipeline stage creation."""
        test_logger.info("Testing pipeline stage creation")
        
        pipeline_parallel = PipelineParallelism(mock_model, mock_gpu_config)
        
        # Check that stages were created
        assert len(pipeline_parallel.pipeline_stages) == 2
        
        # Check that stages are Sequential modules
        for stage in pipeline_parallel.pipeline_stages:
            assert isinstance(stage, nn.Sequential)
        
        test_logger.info("Pipeline stage creation test passed")

class TestLoadBalancer:
    """Test load balancer functionality."""
    
    @pytest.fixture
    def mock_gpu_manager(self):
        """Create mock GPU manager."""
        config = GPUConfig(gpu_ids=[0, 1])
        return MultiGPUManager(config)
    
    @pytest.fixture
    def load_balancer(self, mock_gpu_manager):
        """Create load balancer instance."""
        return LoadBalancer(mock_gpu_manager)
    
    def test_load_balancer_initialization(self, load_balancer, mock_gpu_manager):
        """Test load balancer initialization."""
        test_logger.info("Testing load balancer initialization")
        
        assert load_balancer.gpu_manager == mock_gpu_manager
        assert load_balancer.balancing_stats["total_requests"] == 0
        assert len(load_balancer.balancing_stats["gpu_assignments"]) == 2
        
        test_logger.info("Load balancer initialization test passed")
    
    def test_request_assignment(self, load_balancer):
        """Test request assignment."""
        test_logger.info("Testing request assignment")
        
        request_data = {"prompt": "test", "max_tokens": 10}
        
        # Assign request
        gpu_id = load_balancer.assign_request(request_data)
        
        assert gpu_id in [0, 1]
        assert load_balancer.balancing_stats["total_requests"] == 1
        assert load_balancer.balancing_stats["gpu_assignments"][gpu_id] == 1
        
        # Check that request was added to queue
        queue = load_balancer.gpu_manager.request_queues[gpu_id]
        assert not queue.empty()
        
        test_logger.info("Request assignment test passed")
    
    def test_balancing_statistics(self, load_balancer):
        """Test balancing statistics."""
        test_logger.info("Testing balancing statistics")
        
        # Add some requests
        for i in range(5):
            request_data = {"prompt": f"test{i}", "max_tokens": 10}
            load_balancer.assign_request(request_data)
        
        stats = load_balancer.get_balancing_stats()
        
        assert stats["total_requests"] == 5
        assert "gpu_loads" in stats
        assert "gpu_memory" in stats
        
        test_logger.info("Balancing statistics test passed")

class TestMultiGPUInference:
    """Test multi-GPU inference interface."""
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock model."""
        return nn.Sequential(nn.Linear(10, 5))
    
    @pytest.fixture
    def mock_gpu_config(self):
        """Create mock GPU configuration."""
        return GPUConfig(
            gpu_ids=[0, 1],
            strategy=ParallelismStrategy.TENSOR,
            tensor_parallel_size=2
        )
    
    @pytest.fixture
    def multi_gpu_inference(self, mock_model, mock_gpu_config):
        """Create multi-GPU inference instance."""
        return MultiGPUInference(mock_model, mock_gpu_config)
    
    def test_multi_gpu_inference_initialization(self, multi_gpu_inference, mock_model, mock_gpu_config):
        """Test multi-GPU inference initialization."""
        test_logger.info("Testing multi-GPU inference initialization")
        
        assert multi_gpu_inference.model == mock_model
        assert multi_gpu_inference.config == mock_gpu_config
        assert multi_gpu_inference.gpu_manager is not None
        assert multi_gpu_inference.load_balancer is not None
        assert multi_gpu_inference.parallel_engine is not None
        
        test_logger.info("Multi-GPU inference initialization test passed")
    
    def test_generate_method(self, multi_gpu_inference):
        """Test generate method."""
        test_logger.info("Testing generate method")
        
        prompt = "Hello, world!"
        result = multi_gpu_inference.generate(prompt, max_tokens=50)
        
        assert isinstance(result, str)
        assert "Hello, world!" in result
        assert "max_tokens: 50" in result
        
        test_logger.info("Generate method test passed")
    
    def test_stats_retrieval(self, multi_gpu_inference):
        """Test statistics retrieval."""
        test_logger.info("Testing statistics retrieval")
        
        stats = multi_gpu_inference.get_stats()
        
        assert "gpu_config" in stats
        assert "load_balancing" in stats
        assert "gpu_metrics" in stats
        
        # Check GPU config
        assert stats["gpu_config"]["gpu_ids"] == [0, 1]
        assert stats["gpu_config"]["strategy"] == "tensor"
        
        test_logger.info("Statistics retrieval test passed")
    
    def test_optimization(self, multi_gpu_inference):
        """Test optimization method."""
        test_logger.info("Testing optimization method")
        
        # Add some requests to create load
        for i in range(10):
            multi_gpu_inference.generate(f"test{i}", max_tokens=10)
        
        # Run optimization
        multi_gpu_inference.optimize()
        
        # Should not raise any exceptions
        assert True
        
        test_logger.info("Optimization test passed")

class TestIntegration:
    """Integration tests for multi-GPU functionality."""
    
    def test_end_to_end_workflow(self):
        """Test end-to-end multi-GPU workflow."""
        test_logger.info("Testing end-to-end workflow")
        
        # Create configuration
        config = GPUConfig(
            gpu_ids=[0, 1],
            strategy=ParallelismStrategy.TENSOR,
            tensor_parallel_size=2,
            load_balancing="round_robin"
        )
        
        # Create mock model
        model = nn.Sequential(
            nn.Linear(10, 20),
            nn.ReLU(),
            nn.Linear(20, 5)
        )
        
        # Create multi-GPU inference
        inference = MultiGPUInference(model, config)
        
        # Generate multiple requests
        results = []
        for i in range(5):
            result = inference.generate(f"Request {i}", max_tokens=20)
            results.append(result)
        
        # Check results
        assert len(results) == 5
        for result in results:
            assert isinstance(result, str)
            assert len(result) > 0
        
        # Check statistics
        stats = inference.get_stats()
        assert stats["load_balancing"]["total_requests"] == 5
        
        test_logger.info("End-to-end workflow test passed")
    
    def test_different_strategies(self):
        """Test different parallelism strategies."""
        test_logger.info("Testing different strategies")
        
        model = nn.Sequential(nn.Linear(10, 5))
        
        # Test tensor parallelism
        tensor_config = GPUConfig(
            gpu_ids=[0, 1],
            strategy=ParallelismStrategy.TENSOR
        )
        tensor_inference = MultiGPUInference(model, tensor_config)
        
        # Test pipeline parallelism
        pipeline_config = GPUConfig(
            gpu_ids=[0, 1],
            strategy=ParallelismStrategy.PIPELINE
        )
        pipeline_inference = MultiGPUInference(model, pipeline_config)
        
        # Both should work
        tensor_result = tensor_inference.generate("test", max_tokens=10)
        pipeline_result = pipeline_inference.generate("test", max_tokens=10)
        
        assert isinstance(tensor_result, str)
        assert isinstance(pipeline_result, str)
        
        test_logger.info("Different strategies test passed")

# Run tests and log results
if __name__ == "__main__":
    test_logger.info("Starting multi-GPU tests")
    
    # Run pytest with verbose output
    import subprocess
    import sys
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_multi_gpu.py", 
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
            test_logger.info("All tests passed successfully!")
        else:
            test_logger.error("Some tests failed!")
            
    except Exception as e:
        test_logger.error(f"Error running tests: {e}")
    
    test_logger.info("Multi-GPU tests completed") 