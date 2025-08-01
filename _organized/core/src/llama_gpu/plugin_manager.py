"""
Plugin Architecture Module
Allows dynamic loading, management, and validation of custom modules/integrations.

Features:
- Dynamic plugin loading/unloading
- Plugin listing and retrieval
- Plugin validation
- Comprehensive logging and error handling
"""

import importlib
import logging
from typing import Dict, Optional, Any, List
from src.utils.plugin_utils import has_method
from src.utils.error_handling import log_error
from src.utils.plugin_metadata import get_metadata
from src.utils.plugin_discovery import discover_plugins
from src.utils.plugin_dependency import check_dependencies
from src.utils.plugin_events import PluginEventManager
from src.utils.plugin_version import check_version

logging.basicConfig(filename='logs/plugin_manager.log', level=logging.INFO)


class PluginManager:
    """
    Manages dynamic loading, unloading, validation, and retrieval of plugins.
    """

    def __init__(self) -> None:
        self.plugins: Dict[str, Any] = {}
        self.events = PluginEventManager()

    def load_plugin(self, name: str, path: str) -> Optional[Any]:
        """
        Loads a plugin module by name and path.

        Args:
            name: Name to register the plugin under
            path: Python import path to the plugin module

        Returns:
            The loaded plugin module, or None if failed
        """
        self.events.dispatch('pre_load', name=name, path=path)
        try:
            module = importlib.import_module(path)
            self.plugins[name] = module
            logging.info('Plugin loaded: %s from %s', name, path)
            self.events.dispatch('post_load', name=name, path=path, module=module)
            return module
        except ImportError as e:
            log_error(f'Failed to load plugin {name}', e)
            return None

    def get_plugin(self, name: str) -> Optional[Any]:
        """
        Retrieves a loaded plugin by name.

        Args:
            name: Name of the plugin

        Returns:
            The plugin module, or None if not found
        """
        return self.plugins.get(name)

    def unload_plugin(self, name: str) -> bool:
        """
        Unloads a plugin by name.

        Args:
            name: Name of the plugin to unload

        Returns:
            True if plugin was unloaded, False if not found
        """
        self.events.dispatch('pre_unload', name=name)
        if name in self.plugins:
            del self.plugins[name]
            logging.info('Plugin unloaded: %s', name)
            self.events.dispatch('post_unload', name=name)
            return True
        logging.warning('Attempted to unload non-existent plugin: %s', name)
        return False

    def reload_plugin(self, name: str) -> bool:
        """
        Reload a loaded plugin module.

        Args:
            name: Name of the plugin to reload

        Returns:
            True if reloaded, False otherwise
        """
        self.events.dispatch('pre_reload', name=name)
        if name in self.plugins:
            try:
                importlib.reload(self.plugins[name])
                logging.info('Plugin reloaded: %s', name)
                self.events.dispatch('post_reload', name=name)
                return True
            except Exception as e:
                log_error(f'Failed to reload plugin {name}', e)
        return False

    def list_plugins(self) -> List[str]:
        """
        Lists all loaded plugin names.

        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())

    def get_plugin_metadata(self, name: str) -> Dict:
        """
        Get metadata for a loaded plugin.

        Args:
            name: Name of the plugin

        Returns:
            Metadata dictionary or empty dict
        """
        plugin = self.plugins.get(name)
        if plugin:
            return get_metadata(plugin)
        return {}

    def validate_plugin(self, name: str) -> bool:
        """
        Validates that a plugin implements required interface and has metadata.

        Args:
            name: Name of the plugin to validate

        Returns:
            True if valid, False otherwise
        """
        plugin = self.plugins.get(name)
        valid = plugin and has_method(plugin, 'initialize') and bool(get_metadata(plugin))
        if valid:
            logging.info('Plugin %s validated successfully.', name)
            return True
        log_error(f'Plugin {name} failed validation.')
        return False

    def get_plugin_status(self, name: str) -> str:
        """
        Get status of a loaded plugin (loaded, valid, dependencies).

        Args:
            name: Name of the plugin

        Returns:
            Status string
        """
        plugin = self.plugins.get(name)
        if not plugin:
            return 'not loaded'
        valid = self.validate_plugin(name)
        metadata = get_metadata(plugin)
        deps = metadata.get('dependencies', [])
        deps_ok = check_dependencies(deps) if deps else True
        status = (
            f"loaded | valid: {valid} | dependencies: {'ok' if deps_ok else 'missing'}"
        )
        return status

    def scan_available_plugins(self) -> List[str]:
        """
        Scan and list available plugin modules in the plugin_templates directory.

        Returns:
            List of available plugin names
        """
        return discover_plugins()

    def is_plugin_compatible(self, name: str, required_version: str) -> bool:
        """
        Check if a loaded plugin matches the required version.

        Args:
            name: Name of the plugin
            required_version: Required version string

        Returns:
            True if compatible, False otherwise
        """
        metadata = self.get_plugin_metadata(name)
        return check_version(metadata, required_version)
