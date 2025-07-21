"""
Unit tests for PluginHealth
"""
import unittest
from src.plugin_manager import PluginManager
from monitoring.plugin_health import get_plugin_health

class TestPluginHealth(unittest.TestCase):
    def setUp(self):
        self.pm = PluginManager()
        self.pm.load_plugin('example', 'src.plugin_templates.example_plugin')

    def test_get_plugin_health(self):
        health = get_plugin_health(self.pm)
        self.assertIn('example', health)
        self.assertIn('loaded', health['example'])

if __name__ == '__main__':
    unittest.main()
