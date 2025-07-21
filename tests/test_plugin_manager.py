"""
Unit tests for PluginManager
"""
import unittest
from src.plugin_manager import PluginManager

class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.pm = PluginManager()

    def test_load_unload_plugin(self):
        # Dummy plugin path for test
        result = self.pm.load_plugin('example', 'src.plugin_templates.example_plugin')
        self.assertTrue(result is not None)
        self.assertIn('example', self.pm.list_plugins())
        self.assertTrue(self.pm.unload_plugin('example'))
        self.assertNotIn('example', self.pm.list_plugins())

    def test_validate_plugin(self):
        self.pm.load_plugin('example', 'src.plugin_templates.example_plugin')
        self.assertTrue(self.pm.validate_plugin('example'))

    def test_plugin_status(self):
        self.pm.load_plugin('example', 'src.plugin_templates.example_plugin')
        status = self.pm.get_plugin_status('example')
        self.assertIn('loaded', status)

if __name__ == '__main__':
    unittest.main()
