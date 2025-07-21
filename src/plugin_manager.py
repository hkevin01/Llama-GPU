"""
Plugin Architecture Module
Allows dynamic loading and management of custom modules/integrations.
"""

import importlib
import logging

logging.basicConfig(filename='logs/plugin_manager.log', level=logging.INFO)

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugin(self, name, path):
        try:
            module = importlib.import_module(path)
            self.plugins[name] = module
            logging.info(f'Plugin loaded: {name} from {path}')
            return module
        except Exception as e:
            logging.error(f'Failed to load plugin {name}: {e}')
            return None

    def get_plugin(self, name):
        return self.plugins.get(name)
