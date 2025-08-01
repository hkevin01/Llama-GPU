import os
from utils import logging as log_util

def test_logger_creates_log_file():
    logger = log_util.get_logger('test_logger')
    logger.info('test log entry')
    log_dir = os.path.join(os.path.dirname(__file__), '../logs')
    files = os.listdir(log_dir)
    assert any(f.endswith('.log') for f in files)
