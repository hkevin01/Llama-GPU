"""
Structured Logging Utility
Provides JSON-formatted logs for all modules.
"""

import logging
import json
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str, log_file: str):
        self.logger = logging.getLogger(name)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, message: str, extra: Dict[str, Any] = None):
        log_entry = {'level': 'INFO', 'message': message}
        if extra:
            log_entry.update(extra)
        self.logger.info(json.dumps(log_entry))

    def error(self, message: str, extra: Dict[str, Any] = None):
        log_entry = {'level': 'ERROR', 'message': message}
        if extra:
            log_entry.update(extra)
        self.logger.error(json.dumps(log_entry))
