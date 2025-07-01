"""Error handling and fallback utilities for Llama-GPU."""

import logging
import traceback
from typing import Optional, Callable, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class LlamaGPUError(Exception):
    """Base exception for Llama-GPU errors."""
    pass

class BackendError(LlamaGPUError):
    """Exception raised when backend operations fail."""
    pass

class ModelLoadError(LlamaGPUError):
    """Exception raised when model loading fails."""
    pass

class InferenceError(LlamaGPUError):
    """Exception raised when inference fails."""
    pass

class GPUUnavailableError(LlamaGPUError):
    """Exception raised when GPU is unavailable."""
    pass

@contextmanager
def fallback_to_cpu_on_error(backend_name: str, fallback_callback: Callable[[], Any]):
    """Context manager that falls back to CPU on GPU errors.
    
    Args:
        backend_name: Name of the backend being used
        fallback_callback: Function to call when falling back to CPU
    """
    try:
        yield
    except (GPUUnavailableError, BackendError) as e:
        logger.warning(f"GPU backend '{backend_name}' failed: {e}")
        logger.info("Falling back to CPU backend")
        try:
            result = fallback_callback()
            yield result
        except Exception as cpu_error:
            logger.error(f"CPU fallback also failed: {cpu_error}")
            raise LlamaGPUError(f"Both GPU and CPU backends failed. GPU error: {e}, CPU error: {cpu_error}")
    except Exception as e:
        logger.error(f"Unexpected error in backend '{backend_name}': {e}")
        raise

def safe_model_load(load_function: Callable, model_path: str, backend_name: str) -> Any:
    """Safely load a model with error handling.
    
    Args:
        load_function: Function to load the model
        model_path: Path to the model
        backend_name: Name of the backend
        
    Returns:
        Loaded model
        
    Raises:
        ModelLoadError: If model loading fails
    """
    try:
        logger.info(f"Loading model '{model_path}' with {backend_name} backend")
        return load_function(model_path)
    except FileNotFoundError:
        error_msg = f"Model not found at path: {model_path}"
        logger.error(error_msg)
        raise ModelLoadError(error_msg)
    except PermissionError:
        error_msg = f"Permission denied accessing model at: {model_path}"
        logger.error(error_msg)
        raise ModelLoadError(error_msg)
    except Exception as e:
        error_msg = f"Failed to load model '{model_path}' with {backend_name} backend: {e}"
        logger.error(error_msg)
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        raise ModelLoadError(error_msg)

def safe_inference(inference_function: Callable, input_data: Any, backend_name: str) -> Any:
    """Safely perform inference with error handling.
    
    Args:
        inference_function: Function to perform inference
        input_data: Input data for inference
        backend_name: Name of the backend
        
    Returns:
        Inference result
        
    Raises:
        InferenceError: If inference fails
    """
    try:
        return inference_function(input_data)
    except RuntimeError as e:
        if "CUDA" in str(e) or "GPU" in str(e):
            error_msg = f"GPU error during inference with {backend_name} backend: {e}"
            logger.error(error_msg)
            raise GPUUnavailableError(error_msg)
        else:
            error_msg = f"Runtime error during inference with {backend_name} backend: {e}"
            logger.error(error_msg)
            raise InferenceError(error_msg)
    except MemoryError:
        error_msg = f"Out of memory during inference with {backend_name} backend"
        logger.error(error_msg)
        raise InferenceError(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error during inference with {backend_name} backend: {e}"
        logger.error(error_msg)
        logger.debug(f"Full traceback: {traceback.format_exc()}")
        raise InferenceError(error_msg)

def validate_backend_availability(backend_class, backend_name: str) -> bool:
    """Validate if a backend is available and working.
    
    Args:
        backend_class: Backend class to validate
        backend_name: Name of the backend
        
    Returns:
        True if backend is available, False otherwise
    """
    try:
        backend = backend_class()
        is_available = backend.is_available()
        if is_available:
            logger.info(f"Backend '{backend_name}' is available")
        else:
            logger.warning(f"Backend '{backend_name}' is not available")
        return is_available
    except Exception as e:
        logger.warning(f"Error checking availability of backend '{backend_name}': {e}")
        return False

def get_system_info() -> dict:
    """Get system information for debugging.
    
    Returns:
        Dictionary with system information
    """
    import torch
    import psutil
    
    info = {
        'cpu_count': psutil.cpu_count(),
        'memory_gb': psutil.virtual_memory().total / (1024**3),
        'python_version': f"{torch.version.python}",
        'torch_version': torch.__version__,
    }
    
    # GPU information
    if torch.cuda.is_available():
        info['cuda_available'] = True
        info['cuda_version'] = torch.version.cuda
        info['gpu_count'] = torch.cuda.device_count()
        info['gpu_names'] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
    else:
        info['cuda_available'] = False
    
    # ROCm information
    try:
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            info['rocm_available'] = True
            info['rocm_version'] = torch.version.hip
        else:
            info['rocm_available'] = False
    except AttributeError:
        info['rocm_available'] = False
    
    return info 