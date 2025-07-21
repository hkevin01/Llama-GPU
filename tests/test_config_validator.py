"""
Unit tests for ConfigValidator
"""
import unittest
from src.utils.config_validator import validate_config

class TestConfigValidator(unittest.TestCase):
    def test_validate_config(self):
        config = {'name': 'plugin', 'version': '1.0.0'}
        required = ['name', 'version']
        self.assertTrue(validate_config(config, required))
        self.assertFalse(validate_config({'name': 'plugin'}, required))

if __name__ == '__main__':
    unittest.main()
