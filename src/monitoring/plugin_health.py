"""
Plugin Health Monitoring
Provides health/status checks for loaded plugins.
"""
from src.plugin_manager import PluginManager
from typing import Dict

def get_plugin_health(plugin_manager: PluginManager) -> Dict[str, str]:
    """
    Get health/status for all loaded plugins.
    Args:
        plugin_manager: Instance of PluginManager
    Returns:
        Dict mapping plugin names to health status
    """
    health = {}
    for name in plugin_manager.list_plugins():
        health[name] = plugin_manager.get_plugin_status(name)
    return health
