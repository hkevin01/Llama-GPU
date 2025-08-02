#!/usr/bin/env python3
"""Auto-port HTTP server test."""

import json
import socket
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"message": "Hello from Python!"})
        self.wfile.write(response.encode())


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        return port


if __name__ == "__main__":
    try:
        port = find_free_port()
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
