"""Logging configuration for Llama-GPU."""

import logging
import logging.handlers
import os
from pathlib import Path


def setup_logging(
    log_level=logging.INFO,
    log_dir="logs",
    service_name="llama-gpu"
):
    """Set up logging configuration with rotating file handlers and proper formatting.

    Args:
        log_level: The logging level to use
        log_dir: Directory to store log files
        service_name: Name of the service for log file naming
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    )

    # Set up rotating file handler for detailed logs
    detailed_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, f"{service_name}-detailed.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    detailed_handler.setFormatter(detailed_formatter)
    detailed_handler.setLevel(logging.DEBUG)

    # Set up rotating file handler for errors
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, f"{service_name}-error.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)

    # Set up console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(detailed_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)

    # Create performance logger for metrics
    perf_formatter = logging.Formatter('%(asctime)s | %(message)s')
    perf_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, f"{service_name}-performance.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    perf_handler.setFormatter(perf_formatter)
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.INFO)
    perf_logger.propagate = False  # Don't propagate to root logger

    return root_logger
