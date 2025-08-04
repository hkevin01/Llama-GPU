"""
ROCm backend for LLaMA model inference
"""

import logging
from typing import Optional

try:
    import torch
    HAS_ROCM = torch.cuda.is_available() and torch.version.hip is not None
except ImportError:
    HAS_ROCM = False

logger = logging.getLogger(__name__)

class ROCmBackend:
    """ROCm backend for GPU acceleration"""

    def __init__(self):
        self.device = None
        self.available = False
        self.init_rocm()

    def init_rocm(self):
        """Initialize ROCm backend"""
        if not HAS_ROCM:
            logger.warning("ROCm not available. Make sure PyTorch is built with ROCm support")
            return

        try:
            self.device = torch.device("cuda")
            self.available = True
            logger.info(f"ROCm initialized successfully on {torch.cuda.get_device_name()}")
        except Exception as e:
            logger.error(f"Failed to initialize ROCm: {str(e)}")
            self.available = False

    def get_device_info(self) -> dict:
        """Get ROCm device information"""
        if not self.available:
            return {
                "available": False,
                "name": "No GPU Available",
                "memory_total": 0,
                "memory_used": 0
            }

        try:
            memory_total = torch.cuda.get_device_properties(0).total_memory
            memory_reserved = torch.cuda.memory_reserved(0)
            memory_allocated = torch.cuda.memory_allocated(0)

            return {
                "available": True,
                "name": torch.cuda.get_device_name(),
                "memory_total": memory_total / (1024**3),  # Convert to GB
                "memory_used": (memory_reserved + memory_allocated) / (1024**3)
            }
        except Exception as e:
            logger.error(f"Error getting device info: {str(e)}")
            return {
                "available": False,
                "name": "Error Reading GPU",
                "memory_total": 0,
                "memory_used": 0
            }

    def to_device(self, tensor: "torch.Tensor") -> "torch.Tensor":
        """Move tensor to ROCm device if available"""
        if self.available:
            return tensor.to(self.device)
        return tensor

rocm_backend = ROCmBackend()
