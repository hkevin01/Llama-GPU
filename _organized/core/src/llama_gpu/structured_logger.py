"""
Structured Logger Utility
Provides structured logging for backend and other modules.
"""

import logging
from typing import Any, Dict

class StructuredLogger:
    def __init__(self, name: str, log_file: str):
        self.logger = logging.getLogger(name)
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, message: str, data: Dict = None):
        self.logger.info(f'{message} | {data}')

    def error(self, message: str, data: Dict = None):
        self.logger.error(f'{message} | {data}')
