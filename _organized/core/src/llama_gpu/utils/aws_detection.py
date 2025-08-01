"""AWS GPU instance detection utilities."""

import requests
import json
import os
from typing import Optional, Dict, Any

def get_aws_instance_metadata() -> Optional[Dict[str, Any]]:
    """Get AWS instance metadata.
    
    Returns:
        Dictionary containing instance metadata or None if not on AWS
    """
    try:
        # AWS metadata service endpoint
        metadata_url = "http://169.254.169.254/latest/meta-data/"
        response = requests.get(metadata_url, timeout=2)
        if response.status_code == 200:
            return {"available": True}
    except requests.RequestException:
        pass
    return None

def get_aws_instance_type() -> Optional[str]:
    """Get the AWS instance type.
    
    Returns:
        Instance type string (e.g., 'p3.2xlarge') or None if not on AWS
    """
    try:
        response = requests.get("http://169.254.169.254/latest/meta-data/instance-type", timeout=2)
        if response.status_code == 200:
            return response.text
    except requests.RequestException:
        pass
    return None

def is_aws_gpu_instance() -> bool:
    """Check if current instance is an AWS GPU instance.
    
    Returns:
        True if running on AWS GPU instance, False otherwise
    """
    instance_type = get_aws_instance_type()
    if not instance_type:
        return False
    
    # AWS GPU instance types
    gpu_instance_prefixes = [
        'p3.', 'p3dn.', 'p4.', 'p4d.', 'p4de.', 'p5.',
        'g3.', 'g3s.', 'g4.', 'g4dn.', 'g4ad.', 'g5.', 'g5g.',
        'inf1.', 'trn1.', 'trn1n.'
    ]
    
    return any(instance_type.startswith(prefix) for prefix in gpu_instance_prefixes)

def get_aws_gpu_info() -> Optional[Dict[str, Any]]:
    """Get detailed GPU information for AWS instance.
    
    Returns:
        Dictionary with GPU information or None if not available
    """
    if not is_aws_gpu_instance():
        return None
    
    instance_type = get_aws_instance_type()
    if not instance_type:
        return None
    
    # AWS GPU instance specifications
    gpu_specs = {
        'p3.2xlarge': {'gpu_count': 1, 'gpu_type': 'Tesla V100', 'memory_gb': 16},
        'p3.8xlarge': {'gpu_count': 4, 'gpu_type': 'Tesla V100', 'memory_gb': 64},
        'p3.16xlarge': {'gpu_count': 8, 'gpu_type': 'Tesla V100', 'memory_gb': 128},
        'p3dn.24xlarge': {'gpu_count': 8, 'gpu_type': 'Tesla V100', 'memory_gb': 256},
        'p4d.24xlarge': {'gpu_count': 8, 'gpu_type': 'Tesla A100', 'memory_gb': 400},
        'p4de.24xlarge': {'gpu_count': 8, 'gpu_type': 'Tesla A100', 'memory_gb': 640},
        'g4dn.xlarge': {'gpu_count': 1, 'gpu_type': 'Tesla T4', 'memory_gb': 16},
        'g4dn.2xlarge': {'gpu_count': 1, 'gpu_type': 'Tesla T4', 'memory_gb': 32},
        'g4dn.4xlarge': {'gpu_count': 1, 'gpu_type': 'Tesla T4', 'memory_gb': 64},
        'g4dn.8xlarge': {'gpu_count': 1, 'gpu_type': 'Tesla T4', 'memory_gb': 128},
        'g4dn.12xlarge': {'gpu_count': 4, 'gpu_type': 'Tesla T4', 'memory_gb': 192},
        'g4dn.16xlarge': {'gpu_count': 1, 'gpu_type': 'Tesla T4', 'memory_gb': 256},
        'g5.xlarge': {'gpu_count': 1, 'gpu_type': 'A10G', 'memory_gb': 24},
        'g5.2xlarge': {'gpu_count': 1, 'gpu_type': 'A10G', 'memory_gb': 24},
        'g5.4xlarge': {'gpu_count': 1, 'gpu_type': 'A10G', 'memory_gb': 24},
        'g5.8xlarge': {'gpu_count': 1, 'gpu_type': 'A10G', 'memory_gb': 24},
        'g5.12xlarge': {'gpu_count': 4, 'gpu_type': 'A10G', 'memory_gb': 96},
        'g5.16xlarge': {'gpu_count': 1, 'gpu_type': 'A10G', 'memory_gb': 24},
        'g5.24xlarge': {'gpu_count': 4, 'gpu_type': 'A10G', 'memory_gb': 96},
        'g5.48xlarge': {'gpu_count': 8, 'gpu_type': 'A10G', 'memory_gb': 192},
    }
    
    return gpu_specs.get(instance_type, {
        'gpu_count': 1,
        'gpu_type': 'Unknown',
        'memory_gb': 16
    })

def get_optimal_aws_backend() -> str:
    """Get the optimal backend for the current AWS instance.
    
    Returns:
        Backend name ('cuda', 'rocm', or 'cpu')
    """
    if not is_aws_gpu_instance():
        return 'cpu'
    
    gpu_info = get_aws_gpu_info()
    if not gpu_info:
        return 'cpu'
    
    gpu_type = gpu_info.get('gpu_type', '').lower()
    
    # NVIDIA GPUs
    if any(nvidia_gpu in gpu_type for nvidia_gpu in ['tesla', 'a10g', 'a100', 'v100']):
        return 'cuda'
    
    # AMD GPUs (if any AWS instances use them)
    if any(amd_gpu in gpu_type for amd_gpu in ['radeon', 'mi']):
        return 'rocm'
    
    return 'cpu' 