"""
ROCm backend for LLaMA model inference
"""

import logging
import subprocess

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

logger = logging.getLogger(__name__)


def check_amd_gpu():
    """Check if AMD GPU is available in hardware"""
    try:
        # Check via lspci first
        result = subprocess.run(['lspci'], capture_output=True,
                                text=True, timeout=5)
        if result.returncode == 0:
            amd_found = any('amd' in line.lower() or 'radeon' in line.lower()
                            for line in result.stdout.split('\n'))
            if amd_found:
                return True

        # Fallback to rocm-smi
        result = subprocess.run(['rocm-smi'], capture_output=True,
                                text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_rocm_installation():
    """Check if ROCm is properly installed"""
    try:
        # Check for ROCm installation
        result = subprocess.run(['rocm-smi'], capture_output=True,
                                text=True, timeout=5)
        if result.returncode == 0:
            return True

        # Alternative check for HIP
        result = subprocess.run(['hip-config', '--version'],
                                capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Check hardware and ROCm availability
HAS_AMD_GPU = check_amd_gpu()
HAS_ROCM_INSTALL = check_rocm_installation()

# Determine ROCm availability with improved AMD system detection
if HAS_TORCH:
    if torch.cuda.is_available():
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            HAS_ROCM = True
            hip_version = torch.version.hip
            logger.info(f"✅ ROCm detected - PyTorch with HIP {hip_version}")
        else:
            HAS_ROCM = False
            if HAS_AMD_GPU:
                logger.warning("🔧 AMD GPU detected but PyTorch lacks "
                               "ROCm support")
                logger.info("To enable ROCm acceleration:")
                logger.info("  1. Uninstall current PyTorch: "
                            "pip uninstall torch")
                logger.info("  2. Install ROCm PyTorch: pip install torch "
                            "--index-url "
                            "https://download.pytorch.org/whl/rocm5.4.2")
                logger.info("  3. Verify with: python -c 'import torch; "
                            "print(torch.version.hip)'")
            else:
                logger.info("ℹ️  No AMD GPU detected in system")
    else:
        HAS_ROCM = False
        if HAS_AMD_GPU:
            logger.warning("🔧 AMD GPU found but PyTorch can't access it")
            if HAS_ROCM_INSTALL:
                logger.info("ROCm appears installed but PyTorch can't use it")
                logger.info("Try: export HIP_VISIBLE_DEVICES=0")
            else:
                logger.info("Install ROCm first, then ROCm-enabled PyTorch")
        else:
            logger.info("ℹ️  No GPU acceleration available")
else:
    HAS_ROCM = False
    if HAS_AMD_GPU:
        logger.warning("🔧 AMD GPU detected but PyTorch not installed")
        logger.info("For ROCm acceleration, install:")
        logger.info("pip install torch --index-url "
                    "https://download.pytorch.org/whl/rocm5.4.2")
    else:
        logger.info("ℹ️  No AMD GPU detected in hardware")


class ROCmBackend:
    """ROCm backend for GPU acceleration"""

    def __init__(self):
        self.device = None
        self.available = False
        self.init_rocm()

    def init_rocm(self):
        """Initialize ROCm backend"""
        if not HAS_ROCM:
            logger.warning("ROCm not available. Make sure PyTorch is built "
                           "with ROCm support")
            return

        try:
            self.device = torch.device("cuda")
            self.available = True
            device_name = torch.cuda.get_device_name()
            logger.info(f"ROCm initialized successfully on {device_name}")
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
            props = torch.cuda.get_device_properties(0)
            memory_total = props.total_memory
            memory_reserved = torch.cuda.memory_reserved(0)
            memory_allocated = torch.cuda.memory_allocated(0)

            return {
                "available": True,
                "name": torch.cuda.get_device_name(),
                "memory_total": memory_total / (1024**3),  # Convert to GB
                "memory_used": ((memory_reserved + memory_allocated)
                                / (1024**3))
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
