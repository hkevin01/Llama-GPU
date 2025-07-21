"""
Plugin Version Utility
Provides version and compatibility checks for plugins.
"""
from typing import Dict

def check_version(metadata: Dict, required_version: str) -> bool:
    """
    Check if plugin version matches required version.
    Args:
        metadata: Plugin metadata dict
        required_version: Required version string
    Returns:
        True if compatible, False otherwise
    """
    return metadata.get('version', '') == required_version

