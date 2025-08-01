"""Memory management utilities for LLaMA GPU inference."""

import torch
import psutil


def get_gpu_memory_usage() -> dict:
    """
    Get current GPU memory usage (CUDA only).

    Returns:
        Dictionary with total, used, and free memory in MB for each GPU.
    """
    if not torch.cuda.is_available():
        return {}
    mem_info = {}
    for i in range(torch.cuda.device_count()):
        stats = torch.cuda.memory_stats(i)
        total_mb = torch.cuda.get_device_properties(i).total_memory // 1024 ** 2
        allocated_mb = stats['allocated_bytes.all'] // 1024 ** 2
        reserved_mb = stats['reserved_bytes.all'] // 1024 ** 2
        free_mb = total_mb - allocated_mb
        mem_info[f'cuda:{i}'] = {
            'allocated_mb': allocated_mb,
            'reserved_mb': reserved_mb,
            'free_mb': free_mb
        }
    return mem_info


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

