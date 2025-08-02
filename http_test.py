#!/usr/bin/env python3
"""Simple HTTP server test."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = json.dumps({"message": "Hello from Python!"})
        self.wfile.write(response.encode())

if __name__ == "__main__":
    try:
        server = HTTPServer(('127.0.0.1', 8008), SimpleHandler)
        print("🚀 Test server running on http://127.0.0.1:8008")
        server.serve_forever()
    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)
