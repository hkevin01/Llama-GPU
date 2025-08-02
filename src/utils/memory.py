"""Memory management utilities for LLaMA GPU inference."""

import psutil
import torch


def get_gpu_memory_usage() -> dict:
    """
    Get current GPU memory usage for both NVIDIA (CUDA) and AMD (ROCm) GPUs.

    Returns:
        Dictionary with total, used, and free memory in MB for each GPU.
    """
    mem_info = {}

    # Check if running on ROCm (AMD)
    try:
        if torch.version.hip is not None:
            device_type = "rocm"
            for i in range(torch.cuda.device_count()):
                stats = torch.cuda.memory_stats(i)
                props = torch.cuda.get_device_properties(i)
                total_mb = props.total_memory // 1024 ** 2
                allocated_mb = stats['allocated_bytes.all'] // 1024 ** 2
                reserved_mb = stats.get('reserved_bytes.all', 0) // 1024 ** 2
                free_mb = total_mb - allocated_mb
                mem_info[f'{device_type}:{i}'] = {
                    'allocated_mb': allocated_mb,
                    'reserved_mb': reserved_mb,
                    'free_mb': free_mb,
                    'total_mb': total_mb,
                    'gpu_type': 'AMD'
                }
            return mem_info
    except AttributeError:
        pass

    # Check if running on CUDA (NVIDIA)
    if torch.cuda.is_available():
        device_type = "cuda"
        for i in range(torch.cuda.device_count()):
            stats = torch.cuda.memory_stats(i)
            props = torch.cuda.get_device_properties(i)
            total_mb = props.total_memory // 1024 ** 2
            allocated_mb = stats['allocated_bytes.all'] // 1024 ** 2
            reserved_mb = stats['reserved_bytes.all'] // 1024 ** 2
            free_mb = total_mb - allocated_mb
            mem_info[f'{device_type}:{i}'] = {
                'allocated_mb': allocated_mb,
                'reserved_mb': reserved_mb,
                'free_mb': free_mb,
                'total_mb': total_mb,
                'gpu_type': 'NVIDIA'
            }
        return mem_info

    return {}


def get_cpu_memory_usage() -> dict:
    """
    Get current CPU memory usage.

    Returns:
        Dictionary with total, used, and available memory in MB.
    """
    vm = psutil.virtual_memory()
    return {
        'total_mb': vm.total // 1024 ** 2,
        'used_mb': vm.used // 1024 ** 2,
        'available_mb': vm.available // 1024 ** 2
    }

