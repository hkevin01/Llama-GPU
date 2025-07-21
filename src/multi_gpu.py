"""
Multi-GPU support for LLaMA GPU.

This module provides tensor parallelism, pipeline parallelism,
and load balancing for scaling inference across multiple GPUs.
"""

import logging
import os
import queue
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.distributed as dist
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP

# Configure logging
LOG_DIR = "logs"
logging.basicConfig(
    filename=f"{LOG_DIR}/multi_gpu.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("multi_gpu")

class ParallelismStrategy(Enum):
    """Available parallelism strategies for multi-GPU inference."""
    TENSOR = "tensor"
    PIPELINE = "pipeline"
    DATA = "data"
    HYBRID = "hybrid"

@dataclass
class GPUConfig:
    """Configuration for GPU setup and parallelism."""
    gpu_ids: List[int]
    strategy: ParallelismStrategy = ParallelismStrategy.TENSOR
    tensor_parallel_size: int = 2
    pipeline_parallel_size: int = 2
    data_parallel_size: int = 1
    memory_fraction: float = 0.9
    load_balancing: str = "round_robin"  # round_robin, least_loaded, adaptive

class MultiGPUManager:
    """Manager for multi-GPU inference with various parallelism strategies."""
    
    def __init__(self, gpu_config: GPUConfig):
        self.config = gpu_config
        self.gpu_ids = gpu_config.gpu_ids
        self.num_gpus = len(gpu_config.gpu_ids)
        self.devices = [torch.device(f"cuda:{gpu_id}") for gpu_id in gpu_config.gpu_ids]
        
        # Initialize GPU monitoring
        self.gpu_loads = {gpu_id: 0.0 for gpu_id in gpu_config.gpu_ids}
        self.gpu_memory = {gpu_id: 0.0 for gpu_id in gpu_config.gpu_ids}
        self.request_queues = {gpu_id: queue.Queue() for gpu_id in gpu_config.gpu_ids}
        
        # Load balancing state
        self.current_gpu_index = 0
        self.load_balancing_lock = threading.Lock()
        
        logger.info(f"MultiGPU manager initialized with {self.num_gpus} GPUs: {self.gpu_ids}")
        logger.info(f"Strategy: {gpu_config.strategy.value}")
    
    def get_available_gpus(self) -> List[int]:
        """Get list of available GPU IDs."""
        available = []
        for gpu_id in self.gpu_ids:
            if torch.cuda.is_available() and gpu_id < torch.cuda.device_count():
                available.append(gpu_id)
        return available
    
    def get_gpu_load(self, gpu_id: int) -> float:
        """Get current load on specified GPU."""
        try:
            if gpu_id in self.gpu_loads:
                return self.gpu_loads[gpu_id]
            return 0.0
        except Exception as e:
            logger.error(f"Error getting GPU load for {gpu_id}: {e}")
            return 0.0
    
    def get_gpu_memory_usage(self, gpu_id: int) -> float:
        """Get memory usage percentage for specified GPU."""
        try:
            if torch.cuda.is_available() and gpu_id < torch.cuda.device_count():
                memory_allocated = torch.cuda.memory_allocated(gpu_id)
                memory_total = torch.cuda.get_device_properties(gpu_id).total_memory
                return memory_allocated / memory_total
            return 0.0
        except Exception as e:
            logger.error(f"Error getting GPU memory for {gpu_id}: {e}")
            return 0.0
    
    def update_gpu_metrics(self):
        """Update GPU load and memory metrics."""
        for gpu_id in self.gpu_ids:
            try:
                # Update memory usage
                self.gpu_memory[gpu_id] = self.get_gpu_memory_usage(gpu_id)
                
                # Update load (simplified - queue size based)
                queue_size = self.request_queues[gpu_id].qsize()
                self.gpu_loads[gpu_id] = min(1.0, queue_size / 10.0)  # Normalize to 0-1
                
            except Exception as e:
                logger.error(f"Error updating metrics for GPU {gpu_id}: {e}")
    
    def select_gpu(self, strategy: str = None) -> int:
        """Select GPU based on load balancing strategy."""
        if strategy is None:
            strategy = self.config.load_balancing
        
        with self.load_balancing_lock:
            if strategy == "round_robin":
                gpu_id = self.gpu_ids[self.current_gpu_index]
                self.current_gpu_index = (self.current_gpu_index + 1) % self.num_gpus
                return gpu_id
            
            elif strategy == "least_loaded":
                # Find GPU with lowest load
                min_load = float('inf')
                selected_gpu = self.gpu_ids[0]
                
                for gpu_id in self.gpu_ids:
                    load = self.get_gpu_load(gpu_id)
                    if load < min_load:
                        min_load = load
                        selected_gpu = gpu_id
                
                return selected_gpu
            
            elif strategy == "adaptive":
                # Consider both load and memory
                best_score = float('inf')
                selected_gpu = self.gpu_ids[0]
                
                for gpu_id in self.gpu_ids:
                    load = self.get_gpu_load(gpu_id)
                    memory = self.get_gpu_memory_usage(gpu_id)
                    score = load * 0.7 + memory * 0.3  # Weighted score
                    
                    if score < best_score:
                        best_score = score
                        selected_gpu = gpu_id
                
                return selected_gpu
            
            else:
                # Default to round robin
                return self.select_gpu("round_robin")

class TensorParallelism:
    """Tensor parallelism for splitting model layers across GPUs."""
    
    def __init__(self, model: nn.Module, gpu_config: GPUConfig):
        self.model = model
        self.config = gpu_config
        self.devices = [torch.device(f"cuda:{gpu_id}") for gpu_id in gpu_config.gpu_ids]
        self.tensor_parallel_size = min(gpu_config.tensor_parallel_size, len(gpu_config.gpu_ids))
        
        logger.info(f"Tensor parallelism initialized with size {self.tensor_parallel_size}")
    
    def split_linear_layers(self, module: nn.Module) -> nn.Module:
        """Split linear layers across GPUs for tensor parallelism."""
        for name, child in module.named_children():
            if isinstance(child, nn.Linear):
                # Split the weight matrix across GPUs
                split_weight = self._split_tensor(child.weight, self.tensor_parallel_size)
                split_bias = self._split_tensor(child.bias, self.tensor_parallel_size) if child.bias is not None else None
                
                # Create parallel linear layers
                parallel_layers = []
                for i in range(self.tensor_parallel_size):
                    layer = nn.Linear(
                        split_weight[i].size(1),
                        split_weight[i].size(0),
                        bias=split_bias is not None
                    )
                    layer.weight.data = split_weight[i]
                    if split_bias is not None:
                        layer.bias.data = split_bias[i]
                    layer = layer.to(self.devices[i])
                    parallel_layers.append(layer)
                
                # Replace original layer with parallel version
                setattr(module, name, ParallelLinear(parallel_layers, self.devices))
            
            else:
                # Recursively process child modules
                self.split_linear_layers(child)
        
        return module
    
    def _split_tensor(self, tensor: torch.Tensor, num_splits: int) -> List[torch.Tensor]:
        """Split tensor into specified number of parts."""
        if tensor is None:
            return [None] * num_splits
        
        # Split along the output dimension
        split_size = tensor.size(0) // num_splits
        splits = []
        
        for i in range(num_splits):
            start_idx = i * split_size
            end_idx = start_idx + split_size if i < num_splits - 1 else tensor.size(0)
            splits.append(tensor[start_idx:end_idx])
        
        return splits
    
    def forward_parallel(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """Forward pass with tensor parallelism."""
        # Split input across GPUs
        input_splits = self._split_tensor(input_tensor, self.tensor_parallel_size)
        
        # Process on each GPU
        outputs = []
        for i, device in enumerate(self.devices[:self.tensor_parallel_size]):
            with torch.cuda.device(device):
                input_split = input_splits[i].to(device)
                output = self.model(input_split)
                outputs.append(output)
        
        # Gather outputs
        gathered_output = torch.cat(outputs, dim=-1)
        return gathered_output

class ParallelLinear(nn.Module):
    """Parallel linear layer for tensor parallelism."""
    
    def __init__(self, layers: List[nn.Linear], devices: List[torch.device]):
        super().__init__()
        self.layers = nn.ModuleList(layers)
        self.devices = devices
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        outputs = []
        for i, (layer, device) in enumerate(zip(self.layers, self.devices)):
            with torch.cuda.device(device):
                x_split = x.to(device)
                output = layer(x_split)
                outputs.append(output)
        
        # Concatenate outputs along feature dimension
        return torch.cat(outputs, dim=-1)

class PipelineParallelism:
    """Pipeline parallelism for splitting model stages across GPUs."""
    
    def __init__(self, model: nn.Module, gpu_config: GPUConfig):
        self.model = model
        self.config = gpu_config
        self.devices = [torch.device(f"cuda:{gpu_id}") for gpu_id in gpu_config.gpu_ids]
        self.pipeline_stages = self._create_pipeline_stages()
        
        logger.info(f"Pipeline parallelism initialized with {len(self.pipeline_stages)} stages")
    
    def _create_pipeline_stages(self) -> List[nn.Module]:
        """Create pipeline stages by splitting the model."""
        stages = []
        total_layers = len(list(self.model.children()))
        layers_per_stage = total_layers // self.config.pipeline_parallel_size
        
        current_stage = []
        layer_count = 0
        
        for name, module in self.model.named_children():
            current_stage.append(module)
            layer_count += 1
            
            if layer_count >= layers_per_stage and len(stages) < self.config.pipeline_parallel_size - 1:
                stage_module = nn.Sequential(*current_stage)
                stages.append(stage_module)
                current_stage = []
                layer_count = 0
        
        # Add remaining layers to the last stage
        if current_stage:
            stage_module = nn.Sequential(*current_stage)
            stages.append(stage_module)
        
        # Move stages to respective GPUs
        for i, stage in enumerate(stages):
            if i < len(self.devices):
                stage = stage.to(self.devices[i])
        
        return stages
    
    def forward_pipeline(self, input_tensor: torch.Tensor, batch_size: int = 1) -> torch.Tensor:
        """Forward pass with pipeline parallelism."""
        # Split batch into micro-batches for pipeline
        micro_batch_size = max(1, batch_size // 4)  # Use 4 micro-batches
        micro_batches = torch.chunk(input_tensor, micro_batch_size, dim=0)
        
        # Pipeline execution
        outputs = []
        for micro_batch in micro_batches:
            output = self._forward_micro_batch(micro_batch)
            outputs.append(output)
        
        # Combine outputs
        return torch.cat(outputs, dim=0)
    
    def _forward_micro_batch(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """Forward pass for a single micro-batch through pipeline stages."""
        current_input = input_tensor
        
        for i, stage in enumerate(self.pipeline_stages):
            device = self.devices[i] if i < len(self.devices) else self.devices[0]
            
            with torch.cuda.device(device):
                current_input = current_input.to(device)
                current_input = stage(current_input)
        
        return current_input

class LoadBalancer:
    """Load balancer for distributing requests across multiple GPUs."""
    
    def __init__(self, gpu_manager: MultiGPUManager):
        self.gpu_manager = gpu_manager
        self.request_history = []
        self.balancing_stats = {
            "total_requests": 0,
            "gpu_assignments": {gpu_id: 0 for gpu_id in gpu_manager.gpu_ids}
        }
        
        logger.info("Load balancer initialized")
    
    def assign_request(self, request_data: Dict[str, Any]) -> int:
        """Assign request to appropriate GPU based on load balancing strategy."""
        # Update GPU metrics
        self.gpu_manager.update_gpu_metrics()
        
        # Select GPU based on strategy
        selected_gpu = self.gpu_manager.select_gpu()
        
        # Add to queue
        self.gpu_manager.request_queues[selected_gpu].put(request_data)
        
        # Update statistics
        self.balancing_stats["total_requests"] += 1
        self.balancing_stats["gpu_assignments"][selected_gpu] += 1
        
        # Log assignment
        logger.info(f"Request assigned to GPU {selected_gpu}")
        
        return selected_gpu
    
    def get_balancing_stats(self) -> Dict[str, Any]:
        """Get load balancing statistics."""
        stats = self.balancing_stats.copy()
        stats["gpu_loads"] = self.gpu_manager.gpu_loads
        stats["gpu_memory"] = self.gpu_manager.gpu_memory
        return stats
    
    def optimize_balancing(self):
        """Optimize load balancing based on current statistics."""
        # Analyze current distribution
        total_requests = self.balancing_stats["total_requests"]
        if total_requests == 0:
            return
        
        # Calculate ideal distribution
        num_gpus = len(self.gpu_manager.gpu_ids)
        ideal_per_gpu = total_requests / num_gpus
        
        # Check for imbalance
        imbalances = {}
        for gpu_id in self.gpu_manager.gpu_ids:
            actual = self.balancing_stats["gpu_assignments"][gpu_id]
            imbalance = abs(actual - ideal_per_gpu) / ideal_per_gpu
            imbalances[gpu_id] = imbalance
        
        # Log optimization suggestions
        max_imbalance = max(imbalances.values())
        if max_imbalance > 0.2:  # More than 20% imbalance
            logger.warning(f"Load imbalance detected: {imbalances}")
            logger.info("Consider adjusting load balancing strategy")

class MultiGPUInference:
    """Main interface for multi-GPU inference."""
    
    def __init__(self, model: nn.Module, gpu_config: GPUConfig):
        self.model = model
        self.config = gpu_config
        self.gpu_manager = MultiGPUManager(gpu_config)
        self.load_balancer = LoadBalancer(self.gpu_manager)
        
        # Initialize parallelism based on strategy
        if gpu_config.strategy == ParallelismStrategy.TENSOR:
            self.parallel_engine = TensorParallelism(model, gpu_config)
        elif gpu_config.strategy == ParallelismStrategy.PIPELINE:
            self.parallel_engine = PipelineParallelism(model, gpu_config)
        else:
            self.parallel_engine = None
        
        logger.info(f"MultiGPU inference initialized with strategy: {gpu_config.strategy.value}")
    
    def generate(self, prompt: str, max_tokens: int = 100, **kwargs) -> str:
        """Generate text using multi-GPU inference."""
        # Create request data
        request_data = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "kwargs": kwargs,
            "timestamp": time.time()
        }
        
        # Assign to GPU
        gpu_id = self.load_balancer.assign_request(request_data)
        
        # Process request
        if self.parallel_engine:
            # Use parallel engine
            if isinstance(self.parallel_engine, TensorParallelism):
                result = self._generate_tensor_parallel(prompt, max_tokens, **kwargs)
            elif isinstance(self.parallel_engine, PipelineParallelism):
                result = self._generate_pipeline_parallel(prompt, max_tokens, **kwargs)
            else:
                result = self._generate_single_gpu(prompt, max_tokens, gpu_id, **kwargs)
        else:
            # Use single GPU
            result = self._generate_single_gpu(prompt, max_tokens, gpu_id, **kwargs)
        
        return result
    
    def _generate_tensor_parallel(self, prompt: str, max_tokens: int, **kwargs) -> str:
        """Generate using tensor parallelism."""
        # This would integrate with the actual model and tokenizer
        # For now, return a placeholder
        return f"Tensor parallel generation: {prompt[:20]}... (max_tokens: {max_tokens})"
    
    def _generate_pipeline_parallel(self, prompt: str, max_tokens: int, **kwargs) -> str:
        """Generate using pipeline parallelism."""
        # This would integrate with the actual model and tokenizer
        # For now, return a placeholder
        return f"Pipeline parallel generation: {prompt[:20]}... (max_tokens: {max_tokens})"
    
    def _generate_single_gpu(self, prompt: str, max_tokens: int, gpu_id: int, **kwargs) -> str:
        """Generate using single GPU."""
        # This would integrate with the actual model and tokenizer
        # For now, return a placeholder
        return f"Single GPU generation (GPU {gpu_id}): {prompt[:20]}... (max_tokens: {max_tokens})"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get multi-GPU statistics."""
        stats = {
            "gpu_config": {
                "gpu_ids": self.config.gpu_ids,
                "strategy": self.config.strategy.value,
                "tensor_parallel_size": self.config.tensor_parallel_size,
                "pipeline_parallel_size": self.config.pipeline_parallel_size
            },
            "load_balancing": self.load_balancer.get_balancing_stats(),
            "gpu_metrics": {
                "loads": self.gpu_manager.gpu_loads,
                "memory": self.gpu_manager.gpu_memory
            }
        }
        return stats
    
    def optimize(self):
        """Optimize multi-GPU configuration."""
        self.load_balancer.optimize_balancing()
        logger.info("Multi-GPU optimization completed") 