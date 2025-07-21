"""
Config Validator Utility
Validates plugin and core config files for required fields and types.
"""
from typing import Dict, List

def validate_config(config: Dict, required_fields: List[str]) -> bool:
    """
    Validate config dict for required fields.
    Args:
        config: Config dictionary
        required_fields: List of required field names
    Returns:
        True if all required fields are present, False otherwise
    """
    return all(field in config for field in required_fields)
