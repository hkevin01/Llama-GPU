#!/usr/bin/env python3
"""Socket test server."""

import socket


def create_server():
    """Create a simple TCP server."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))  # Let OS choose port
            port = s.getsockname()[1]
            print(f"🚀 Bound to port {port}")

            s.listen(1)
            print(f"📡 Listening on http://127.0.0.1:{port}")

            while True:
                conn, addr = s.accept()
                print(f"🔌 Connection from {addr}")
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        break
                    response = (
                        b'HTTP/1.1 200 OK\r\n'
                        b'Content-Type: application/json\r\n'
                        b'\r\n'
                        b'{"message": "Hello from socket server!"}'
                    )
                    conn.sendall(response)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    create_server()
