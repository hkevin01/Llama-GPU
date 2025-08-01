"""
Llama-GPU: High-performance GPU-accelerated inference library for LLaMA models.

This package provides efficient tools for loading, optimizing, and running
LLaMA models on GPU hardware with advanced features like multi-GPU support,
quantization, and real-time monitoring.
"""

__version__ = "1.0.0"
__author__ = "Kevin"
__email__ = "your.email@example.com"

# Core imports
from .llama_gpu import LlamaGPU
from .model_manager import ModelManager
from .multi_gpu import MultiGPUManager

# API imports
try:
    from .api_server import APIServer
except ImportError:
    # Optional API dependencies
    APIServer = None

# Monitoring imports
try:
    from .monitoring_alerts import MonitoringSystem
except ImportError:
    # Optional monitoring dependencies
    MonitoringSystem = None

__all__ = [
    "LlamaGPU",
    "ModelManager",
    "MultiGPUManager",
]

# Add optional exports if available
if APIServer:
    __all__.append("APIServer")
if MonitoringSystem:
    __all__.append("MonitoringSystem")
