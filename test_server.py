#!/usr/bin/env python3
"""Simple FastAPI test server."""

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


def find_free_port():
    """Find a free port to bind to."""
    import socket
    from contextlib import closing
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
        return port


if __name__ == "__main__":
    try:
        port = find_free_port()
        print(f"🚀 Starting test server on port {port}...")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        import sys
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
