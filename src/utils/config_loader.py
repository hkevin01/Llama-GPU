"""
Config Loader Utility
Loads configuration from YAML or JSON files.
"""
import yaml
import json
from typing import Any

def load_config(path: str) -> Any:
    """
    Load configuration from a YAML or JSON file.
    Args:
        path: Path to config file
    Returns:
        Parsed config object
    """
    if path.endswith('.yaml') or path.endswith('.yml'):
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    elif path.endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        raise ValueError('Unsupported config file format')

