#!/usr/bin/env python3
"""High-port test server."""

import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler."""
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({
            "message": "Hello from test server!",
            "path": self.path
        })
        self.wfile.write(response.encode())


def find_port():
    """Find an available port in the higher range."""
    for port in range(49152, 65535):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    raise RuntimeError("Could not find an available port")


if __name__ == "__main__":
    try:
        port = find_port()
        print(f"🚀 Found free port {port}")

        server = HTTPServer(('127.0.0.1', port), SimpleHandler)
        print(f"📡 Test server running on http://127.0.0.1:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        server.server_close()
    except Exception as e:
        print(f"❌ Error: {e}")
        import sys
        sys.exit(1)
