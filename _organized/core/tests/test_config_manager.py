import unittest
from src.utils.config_manager import ConfigManager
import os

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.manager = ConfigManager()
        self.yaml_path = 'config/plugin_marketplace_config.yaml'
        self.json_path = 'config/test_config.json'
        # Create a test JSON config file
        with open(self.json_path, 'w', encoding='utf-8') as f:
            f.write('{"test": "value"}')

    def tearDown(self):
        if os.path.exists(self.json_path):
            os.remove(self.json_path)

    def test_load_yaml(self):
        config = self.manager.load_yaml(self.yaml_path)
        self.assertIn('ui', config)

    def test_load_json(self):
        config = self.manager.load_json(self.json_path)
        self.assertEqual(config['test'], 'value')

if __name__ == '__main__':
    unittest.main()
