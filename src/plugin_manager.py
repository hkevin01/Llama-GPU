"""
Plugin Architecture Module
Allows dynamic loading and management of custom modules/integrations.
"""

import importlib
import logging
from typing import Dict, Optional, Any

logging.basicConfig(filename='logs/plugin_manager.log', level=logging.INFO)

class PluginManager:
    """
    Manages dynamic loading and retrieval of plugins.
    """
    def __init__(self) -> None:
        self.plugins: Dict[str, Any] = {}

    def load_plugin(self, name: str, path: str) -> Optional[Any]:
        """
        Loads a plugin module by name and path.
        """
        try:
            module = importlib.import_module(path)
            self.plugins[name] = module
            logging.info('Plugin loaded: %s from %s', name, path)
            return module
        except ImportError as e:
            logging.error('Failed to load plugin %s: %s', name, e)
            return None

    def get_plugin(self, name: str) -> Optional[Any]:
        """
        Retrieves a loaded plugin by name.
        """
        return self.plugins.get(name)
