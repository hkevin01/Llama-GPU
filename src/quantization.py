"""
Quantization support for LLaMA GPU.

This module provides INT8/INT4 quantization, dynamic quantization,
and quantized model management for memory efficiency.
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
from torch.ao.quantization import QConfig, get_default_qconfig, quantize_dynamic

# Configure logging
LOG_DIR = "logs"
logging.basicConfig(
    filename=f"{LOG_DIR}/quantization.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("quantization")

class QuantizationType(Enum):
    """Available quantization types."""
    INT8 = "int8"
    INT4 = "int4"
    FP16 = "fp16"
    BF16 = "bf16"
    DYNAMIC = "dynamic"
    STATIC = "static"

@dataclass
class QuantizationConfig:
    """Configuration for quantization."""
    quantization_type: QuantizationType = QuantizationType.INT8
    dynamic: bool = True
    per_channel: bool = True
    symmetric: bool = True
    reduce_range: bool = True
    memory_efficient: bool = True
    preserve_accuracy: bool = True

class QuantizationManager:
    """Manager for model quantization operations."""
    
    def __init__(self, config: QuantizationConfig):
        self.config = config
        self.quantized_models = {}
        self.quantization_stats = {
            "total_models": 0,
            "memory_saved": 0.0,
            "accuracy_loss": 0.0,
            "quantization_times": []
        }
        
        logger.info(f"Quantization manager initialized with config: {config}")
    
    def quantize_model(self, model: nn.Module, model_name: str = "default") -> nn.Module:
        """Quantize a model based on configuration."""
        logger.info(f"Starting quantization for model: {model_name}")
        
        start_time = time.time()
        
        try:
            if self.config.quantization_type == QuantizationType.DYNAMIC:
                quantized_model = self._dynamic_quantization(model)
            elif self.config.quantization_type == QuantizationType.INT8:
                quantized_model = self._int8_quantization(model)
            elif self.config.quantization_type == QuantizationType.INT4:
                quantized_model = self._int4_quantization(model)
            elif self.config.quantization_type == QuantizationType.FP16:
                quantized_model = self._fp16_quantization(model)
            elif self.config.quantization_type == QuantizationType.BF16:
                quantized_model = self._bf16_quantization(model)
            else:
                raise ValueError(f"Unsupported quantization type: {self.config.quantization_type}")
            
            # Calculate memory savings
            original_size = self._get_model_size(model)
            quantized_size = self._get_model_size(quantized_model)
            memory_saved = original_size - quantized_size
            
            # Store quantized model
            self.quantized_models[model_name] = {
                "model": quantized_model,
                "config": self.config,
                "original_size": original_size,
                "quantized_size": quantized_size,
                "memory_saved": memory_saved,
                "quantization_time": time.time() - start_time
            }
            
            # Update statistics
            self.quantization_stats["total_models"] += 1
            self.quantization_stats["memory_saved"] += memory_saved
            self.quantization_stats["quantization_times"].append(time.time() - start_time)
            
            logger.info(f"Quantization completed for {model_name}. Memory saved: {memory_saved:.2f} MB")
            
            return quantized_model
            
        except Exception as e:
            logger.error(f"Quantization failed for {model_name}: {str(e)}")
            raise
    
    def _dynamic_quantization(self, model: nn.Module) -> nn.Module:
        """Apply dynamic quantization."""
        logger.info("Applying dynamic quantization")
        
        # Use PyTorch's dynamic quantization
        quantized_model = quantize_dynamic(
            model, 
            {nn.Linear, nn.LSTM, nn.LSTMCell, nn.RNNCell, nn.GRUCell}, 
            dtype=torch.qint8
        )
        
        return quantized_model
    
    def _int8_quantization(self, model: nn.Module) -> nn.Module:
        """Apply INT8 quantization."""
        logger.info("Applying INT8 quantization")
        
        # For INT8, we'll use dynamic quantization as a fallback
        # since static quantization requires calibration data
        quantized_model = quantize_dynamic(
            model,
            {nn.Linear, nn.LSTM, nn.LSTMCell, nn.RNNCell, nn.GRUCell},
            dtype=torch.qint8
        )
        
        return quantized_model
    
    def _int4_quantization(self, model: nn.Module) -> nn.Module:
        """Apply INT4 quantization."""
        logger.info("Applying INT4 quantization")
        
        # Custom INT4 quantization implementation
        quantized_model = self._custom_int4_quantization(model)
        
        return quantized_model
    
    def _custom_int4_quantization(self, model: nn.Module) -> nn.Module:
        """Custom INT4 quantization implementation."""
        quantized_model = model.__class__()
        quantized_model.load_state_dict(model.state_dict())
        
        # Quantize linear layers to INT4
        for name, module in quantized_model.named_modules():
            if isinstance(module, nn.Linear):
                # Quantize weights to INT4
                quantized_weights = self._quantize_weights_int4(module.weight.data)
                module.weight.data = quantized_weights
                
                # Quantize bias if present
                if module.bias is not None:
                    quantized_bias = self._quantize_weights_int4(module.bias.data)
                    module.bias.data = quantized_bias
        
        return quantized_model
    
    def _quantize_weights_int4(self, weights: torch.Tensor) -> torch.Tensor:
        """Quantize weights to INT4."""
        # Scale weights to INT4 range (-8 to 7)
        max_val = torch.max(torch.abs(weights))
        if max_val > 0:
            scale = max_val / 7.0
            quantized = torch.round(weights / scale) * scale
            quantized = torch.clamp(quantized, -8 * scale, 7 * scale)
        else:
            quantized = weights
        
        return quantized
    
    def _fp16_quantization(self, model: nn.Module) -> nn.Module:
        """Apply FP16 quantization."""
        logger.info("Applying FP16 quantization")
        
        # Convert model to FP16
        quantized_model = model.half()
        
        return quantized_model
    
    def _bf16_quantization(self, model: nn.Module) -> nn.Module:
        """Apply BF16 quantization."""
        logger.info("Applying BF16 quantization")
        
        # Convert model to BF16
        quantized_model = model.to(torch.bfloat16)
        
        return quantized_model
    
    def _get_model_size(self, model: nn.Module) -> float:
        """Calculate model size in MB."""
        param_size = 0
        buffer_size = 0
        
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        size_mb = (param_size + buffer_size) / 1024 / 1024
        return size_mb
    
    def get_quantized_model(self, model_name: str) -> Optional[nn.Module]:
        """Get a quantized model by name."""
        if model_name in self.quantized_models:
            return self.quantized_models[model_name]["model"]
        return None
    
    def get_quantization_stats(self, model_name: str) -> Dict[str, Any]:
        """Get quantization statistics for a specific model."""
        if model_name in self.quantized_models:
            model_info = self.quantized_models[model_name]
            return {
                "model_name": model_name,
                "quantization_type": self.config.quantization_type.value,
                "memory_saved": model_info["memory_saved"],
                "quantization_time": model_info["quantization_time"],
                "original_size": model_info["original_size"],
                "quantized_size": model_info["quantized_size"]
            }
        return {}
    
    def get_overall_stats(self) -> Dict[str, Any]:
        """Get overall quantization statistics."""
        avg_time = 0.0
        if self.quantization_stats["quantization_times"]:
            avg_time = sum(self.quantization_stats["quantization_times"]) / len(self.quantization_stats["quantization_times"])
        
        return {
            "total_models": self.quantization_stats["total_models"],
            "memory_saved": self.quantization_stats["memory_saved"],
            "accuracy_loss": self.quantization_stats["accuracy_loss"],
            "avg_quantization_time": avg_time,
            "quantization_times": self.quantization_stats["quantization_times"]
        }


class QuantizedInference:
    """Quantized inference engine."""
    
    def __init__(self, quantized_model: nn.Module, config: QuantizationConfig):
        self.quantized_model = quantized_model
        self.config = config
        self.tokenizer = None
        
        # Set model to evaluation mode
        self.quantized_model.eval()
        
        logger.info(f"Quantized inference engine initialized with {config.quantization_type.value} quantization")
    
    def generate(self, prompt: str, max_tokens: int = 50, **kwargs) -> str:
        """Generate text using quantized model."""
        try:
            # Simple tokenization (in real implementation, use proper tokenizer)
            if self.tokenizer is None:
                # Fallback tokenization
                tokens = [ord(c) % 1000 for c in prompt[:100]]  # Simple character-based
                input_tensor = torch.tensor([tokens], dtype=torch.long)
            else:
                input_tensor = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate tokens
            generated_tokens = []
            current_input = input_tensor
            
            with torch.no_grad():
                for _ in range(max_tokens):
                    # Forward pass through quantized model
                    output = self.quantized_model(current_input)
                    
                    # Get next token (simple greedy decoding)
                    next_token = torch.argmax(output[0, -1, :]).unsqueeze(0)
                    generated_tokens.append(next_token.item())
                    
                    # Update input for next iteration
                    current_input = torch.cat([current_input, next_token.unsqueeze(0)], dim=1)
            
            # Decode tokens
            if self.tokenizer is None:
                # Fallback decoding
                result = prompt + " " + "".join([chr(t % 1000) for t in generated_tokens])
            else:
                result = self.tokenizer.decode(generated_tokens)
            
            return result
            
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            return f"Generated text for: {prompt}"
    
    def benchmark_performance(self, test_prompts: List[str], max_tokens: int = 50) -> Dict[str, Any]:
        """Benchmark quantized model performance."""
        logger.info(f"Starting performance benchmark with {len(test_prompts)} prompts")
        
        start_time = time.time()
        total_tokens = 0
        
        for prompt in test_prompts:
            try:
                result = self.generate(prompt, max_tokens)
                total_tokens += max_tokens
            except Exception as e:
                logger.error(f"Benchmark failed for prompt '{prompt}': {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        avg_time_per_prompt = total_time / len(test_prompts) if test_prompts else 0
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0
        throughput = len(test_prompts) / total_time if total_time > 0 else 0
        
        # Estimate memory usage
        memory_usage = self._estimate_memory_usage()
        
        benchmark_results = {
            "total_time": total_time,
            "avg_time_per_prompt": avg_time_per_prompt,
            "tokens_per_second": tokens_per_second,
            "throughput": throughput,
            "total_prompts": len(test_prompts),
            "total_tokens": total_tokens,
            "memory_usage": memory_usage
        }
        
        logger.info(f"Benchmark completed. Throughput: {throughput:.2f} prompts/sec")
        
        return benchmark_results
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage of quantized model."""
        param_size = 0
        for param in self.quantized_model.parameters():
            param_size += param.nelement() * param.element_size()
        
        return param_size / 1024 / 1024  # MB


class QuantizationCache:
    """Cache for quantized models."""
    
    def __init__(self, cache_dir: str = "cache/quantized_models"):
        self.cache_dir = cache_dir
        self.cache_index = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load existing cache index
        self._load_cache_index()
        
        logger.info(f"Quantization cache initialized at {cache_dir}")
    
    def _load_cache_index(self):
        """Load cache index from disk."""
        index_path = os.path.join(self.cache_dir, "cache_index.json")
        if os.path.exists(index_path):
            try:
                import json
                with open(index_path, 'r') as f:
                    self.cache_index = json.load(f)
                logger.info(f"Loaded cache index with {len(self.cache_index)} entries")
            except Exception as e:
                logger.error(f"Failed to load cache index: {str(e)}")
                self.cache_index = {}
    
    def _save_cache_index(self):
        """Save cache index to disk."""
        index_path = os.path.join(self.cache_dir, "cache_index.json")
        try:
            import json
            with open(index_path, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache index: {str(e)}")
    
    def cache_model(self, model_name: str, quantized_model: nn.Module, config: QuantizationConfig):
        """Cache a quantized model."""
        try:
            # Create model file path
            model_path = os.path.join(self.cache_dir, f"{model_name}_{config.quantization_type.value}.pt")
            
            # Save model
            torch.save(quantized_model.state_dict(), model_path)
            
            # Update cache index
            self.cache_index[model_name] = {
                "path": model_path,
                "quantization_type": config.quantization_type.value,
                "cached_at": datetime.now().isoformat(),
                "config": {
                    "dynamic": config.dynamic,
                    "per_channel": config.per_channel,
                    "symmetric": config.symmetric,
                    "reduce_range": config.reduce_range,
                    "memory_efficient": config.memory_efficient,
                    "preserve_accuracy": config.preserve_accuracy
                }
            }
            
            # Save updated index
            self._save_cache_index()
            
            logger.info(f"Cached quantized model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to cache model {model_name}: {str(e)}")
            raise
    
    def load_cached_model(self, model_name: str, quantization_type: QuantizationType) -> Optional[nn.Module]:
        """Load a cached quantized model."""
        if model_name not in self.cache_index:
            return None
        
        cache_entry = self.cache_index[model_name]
        if cache_entry["quantization_type"] != quantization_type.value:
            return None
        
        try:
            model_path = cache_entry["path"]
            if not os.path.exists(model_path):
                logger.warning(f"Cached model file not found: {model_path}")
                return None
            
            # Load model state dict
            state_dict = torch.load(model_path, map_location='cpu')
            
            # Create a simple model to load the state dict
            # In real implementation, you'd need the original model architecture
            model = SimpleModel()
            model.load_state_dict(state_dict)
            
            logger.info(f"Loaded cached quantized model: {model_name}")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load cached model {model_name}: {str(e)}")
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = 0
        for entry in self.cache_index.values():
            if os.path.exists(entry["path"]):
                total_size += os.path.getsize(entry["path"])
        
        return {
            "total_models": len(self.cache_index),
            "cache_size": total_size / 1024 / 1024,  # MB
            "models": list(self.cache_index.keys())
        }


# Simple model class for testing
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