#!/usr/bin/env python3
"""Simple socket test server."""

import socket
import sys


def test_socket_bind(port):
    """Test binding to a specific port."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Set socket options
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Try to bind
        sock.bind(('127.0.0.1', port))
        print(f"✅ Successfully bound to port {port}")

        # Listen for connections
        sock.listen(1)
        print(f"✅ Successfully listening on port {port}")

        return True

    except socket.error as e:
        print(f"❌ Error binding to port {port}: {e}")
        return False

    finally:
        sock.close()

def main():
    """Test binding to common ports."""
    test_ports = [8000, 8080, 3000, 5000]

    print("🔍 Testing network connectivity...")
    print(f"System info: Python {sys.version}")

    for port in test_ports:
        if test_socket_bind(port):
            break

if __name__ == "__main__":
    main()
