import psutil
import time
import logging
from utils.logging import get_logger

logger = get_logger("resource_monitor")

def log_resources(interval=5):
    while True:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        logger.info(f"CPU: {cpu}% | Memory: {mem}%")
        time.sleep(interval)

if __name__ == "__main__":
    log_resources()
