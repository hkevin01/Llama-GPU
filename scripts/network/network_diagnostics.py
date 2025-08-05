#!/usr/bin/env python3
"""Network diagnostics script."""

import logging
import os
import socket
import subprocess
import sys

# Configure verbose logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def check_network_status():
    """Check basic network status."""
    try:
        # Check if loopback interface is up
        result = subprocess.run(
            ['ip', 'addr', 'show', 'lo'],
            capture_output=True,
            text=True,
            check=False
        )
        logger.info("Loopback interface status:\n%s", result.stdout)

        # Check listening ports
        result = subprocess.run(
            ['ss', '-tlnp'],
            capture_output=True,
            text=True,
            check=False
        )
        logger.info("Current listening ports:\n%s", result.stdout)

    except subprocess.SubprocessError as e:
        logger.error("Failed to check network status: %s", e)


def test_socket_binding():
    """Test socket binding capabilities."""
    test_ports = [8000, 8080, 3000, 5000]

    for port in test_ports:
        logger.info("Testing port %d...", port)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Try binding
            sock.bind(('127.0.0.1', port))
            logger.info("Successfully bound to port %d", port)

            # Try listening
            sock.listen(1)
            logger.info("Successfully listening on port %d", port)

            return port

        except socket.error as e:
            logger.error("Failed to bind to port %d: %s", port, e)

        finally:
            sock.close()

    return None


def main():
    """Run network diagnostics."""
    logger.info("Starting network diagnostics...")
    logger.info("Python version: %s", sys.version)
    logger.info("Current user: %s", os.getenv('USER'))
    logger.info("Current working directory: %s", os.getcwd())

    # Check network status
    check_network_status()

    # Test socket binding
    if port := test_socket_binding():
        logger.info("✅ Successfully found working port: %d", port)
    else:
        logger.error("❌ Could not bind to any test ports")


if __name__ == "__main__":
    main()
