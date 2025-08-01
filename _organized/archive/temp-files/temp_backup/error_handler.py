"""
Centralized Error Handler
Provides logging and error reporting utilities.
"""
import logging
from typing import Optional

logging.basicConfig(filename='logs/error_handler.log', level=logging.ERROR)

def log_error(message: str, exc: Optional[Exception] = None) -> None:
    """
    Log an error message with optional exception details.
    Args:
        message: Error message
        exc: Exception object (optional)
    """
    if exc:
        logging.error('%s Exception: %s', message, exc)
    else:
        logging.error('%s', message)

