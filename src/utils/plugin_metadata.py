"""
Plugin Metadata Utility
Provides functions to extract and validate plugin metadata.
"""
from typing import Any, Dict

def get_metadata(plugin: Any) -> Dict:
    """
    Extract metadata from a plugin module (expects 'metadata' attribute).
    Args:
        plugin: Plugin module
    Returns:
        Metadata dictionary or empty dict
    """
    return getattr(plugin, 'metadata', {})

