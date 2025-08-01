"""
Plugin Discovery Utility
Scans and lists available plugins in the plugin_templates directory.
"""
import os
from typing import List

PLUGIN_DIR = 'src/plugin_templates'

def discover_plugins() -> List[str]:
    """
    Discover available plugin modules in the plugin_templates directory.
    Returns:
        List of plugin module names
    """
    plugins = []
    try:
        if os.path.exists(PLUGIN_DIR):
            for fname in os.listdir(PLUGIN_DIR):
                if fname.endswith('.py') and not fname.startswith('__'):
                    plugins.append(fname[:-3])
    except (OSError, FileNotFoundError):
        pass  # Return empty list if directory doesn't exist
    return plugins

