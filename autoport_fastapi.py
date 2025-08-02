#!/usr/bin/env python3
"""Auto-port FastAPI test."""

import socket
from contextlib import closing

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello from FastAPI!"}


def find_free_port():
    """Find an available port."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        return port


if __name__ == "__main__":
    import uvicorn
    import uvicorn.config

    try:
        port = find_free_port()
        print(f"🚀 Found free port {port}")

        # Configure Uvicorn server
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)

        print(f"📡 Starting FastAPI server on http://127.0.0.1:{port}")
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import sys
        sys.exit(1)
