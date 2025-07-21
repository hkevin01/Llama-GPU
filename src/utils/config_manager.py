"""
Configuration Management Utility
Loads and validates YAML/JSON config files for modules.
"""

import yaml
import json
import logging
from typing import Any, Dict

class ConfigManager:
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger('ConfigManager')

    def load_yaml(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            if self.logger:
                self.logger.info(f'Loaded YAML config: {path}')
            return config
        except Exception as e:
            if self.logger:
                self.logger.error(f'Failed to load YAML config {path}: {e}')
            return {}

    def load_json(self, path: str) -> Dict[str, Any]:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            if self.logger:
                self.logger.info(f'Loaded JSON config: {path}')
            return config
        except Exception as e:
            if self.logger:
                self.logger.error(f'Failed to load JSON config {path}: {e}')
            return {}
