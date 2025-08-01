"""
Plugin Utilities Module
Provides helper functions for plugin management and validation.
"""
from typing import Any

def has_method(obj: Any, method: str) -> bool:
    """
    Check if an object has a method with the given name.
    Args:
        obj: Object to check
        method: Method name
    Returns:
        True if method exists, False otherwise
    """
    return hasattr(obj, method) and callable(getattr(obj, method, None))

