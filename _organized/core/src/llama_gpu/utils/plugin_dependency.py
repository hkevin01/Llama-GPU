"""
Plugin Dependency Utility
Manages plugin dependencies and checks for required modules.
"""
import importlib
from typing import List

def check_dependencies(dependencies: List[str]) -> bool:
    """
    Check if all dependencies are importable.
    Args:
        dependencies: List of module names
    Returns:
        True if all dependencies are importable, False otherwise
    """
    for dep in dependencies:
        try:
            importlib.import_module(dep)
        except ImportError:
            return False
    return True

