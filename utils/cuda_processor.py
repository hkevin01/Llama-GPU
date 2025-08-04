"""CUDA-accelerated data processing module for LLaMA-GPU using cuDF."""

import logging
import subprocess
from typing import Any, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_nvidia_gpu():
    """Check if NVIDIA GPU is available in hardware"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True,
                                text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_cuda_driver():
    """Check if CUDA driver is properly installed"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True,
                                text=True, timeout=5)
        if result.returncode == 0:
            # Check if CUDA is listed in nvidia-smi output
            return 'CUDA' in result.stdout or 'Driver Version' in result.stdout
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


# Check hardware and driver availability
HAS_NVIDIA_GPU = check_nvidia_gpu()
HAS_CUDA_DRIVER = check_cuda_driver()

try:
    if not HAS_NVIDIA_GPU:
        logger.info("No NVIDIA GPU detected in hardware - running in CPU mode")
        HAS_CUDA = False
    elif not HAS_CUDA_DRIVER:
        logger.warning("NVIDIA GPU detected but CUDA driver not properly "
                       "installed")
        HAS_CUDA = False
    else:
        import cudf
        import numpy as np
        from numba import cuda
        HAS_CUDA = True
        logger.info("CUDA acceleration enabled with cuDF")
except ImportError as e:
    HAS_CUDA = False
    if HAS_NVIDIA_GPU:
        logger.warning(f"NVIDIA GPU detected but CUDA packages not "
                       f"installed: {e}")
        logger.info("To enable CUDA acceleration, install: "
                    "pip install cudf-cu11 numba")
    else:
        logger.info("CUDA packages not available - running in CPU mode")


class CudaDataProcessor:
    """Handle CUDA-accelerated data processing for chat responses."""

    def __init__(self):
        """Initialize the CUDA data processor"""
        self.has_cuda = HAS_CUDA
        if self.has_cuda:
            # Initialize CUDA context
            try:
                cuda.select_device(0)  # Use first available GPU
                device_name = cuda.get_current_device().name
                logger.info(f"Using CUDA device: {device_name}")
            except Exception as e:
                logger.error(f"Failed to initialize CUDA device: {e}")
                self.has_cuda = False

    def process_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Process performance metrics using CUDA acceleration if available"""
        if not self.has_cuda:
            return metrics

        try:
            # Convert metrics to cuDF DataFrame for efficient processing
            df = cudf.DataFrame([metrics])

            # Calculate moving averages and other statistics
            if 'tokensPerSecond' in metrics:
                # Use CUDA for calculating rolling statistics
                df['tokensPerSecond'] = df['tokensPerSecond'].astype('float32')
                window_mean = df['tokensPerSecond'].rolling(window=5).mean()
                df['smoothed_tps'] = window_mean

            # Update GPU metrics
            if 'gpuUsage' in metrics:
                df['gpuUsage'] = df['gpuUsage'].astype('float32')

            # Convert back to dictionary
            processed = df.iloc[-1].to_dict()
            return processed

        except Exception as e:
            logger.error(f"Error in CUDA metrics processing: {e}")
            return metrics

    def optimize_response(self, text: str, chunk_size: int = 1024) -> str:
        """Optimize text response processing using CUDA"""
        if not self.has_cuda or len(text) < chunk_size:
            return text

        try:
            # Convert text to CUDA array for processing
            text_array = np.array(list(text), dtype='str')
            d_array = cuda.to_device(text_array)

            # Process text in chunks
            @cuda.jit
            def process_text(arr):
                idx = cuda.grid(1)
                if idx < arr.size:
                    # Perform any needed text processing here
                    pass

            # Calculate grid and block sizes
            threads_per_block = 256
            blocks_per_grid = ((text_array.size + threads_per_block - 1)
                               // threads_per_block)

            # Process text
            process_text[blocks_per_grid, threads_per_block](d_array)

            # Return processed text
            return ''.join(d_array.copy_to_host())

        except Exception as e:
            logger.error(f"Error in CUDA text processing: {e}")
            return text

    def get_gpu_status(self) -> Dict[str, Any]:
        """Get detailed GPU status information"""
        if not self.has_cuda:
            return {
                "available": False,
                "name": "No CUDA Device",
                "memoryUsed": 0,
                "memoryTotal": 0
            }

        try:
            device = cuda.get_current_device()
            ctx = device.get_memory_info()
            return {
                "available": True,
                "name": device.name,
                "memoryUsed": (ctx[1] - ctx[0]) / (1024**3),  # Convert to GB
                "memoryTotal": ctx[1] / (1024**3)
            }
        except Exception as e:
            logger.error(f"Error getting GPU status: {e}")
            return {
                "available": False,
                "name": f"Error: {str(e)}",
                "memoryUsed": 0,
                "memoryTotal": 0
            }


cuda_processor = CudaDataProcessor()
