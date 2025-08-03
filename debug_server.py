#!/usr/bin/env python3
"""Debug server to identify networking issues."""

import logging
import socket
import sys
from contextlib import closing

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_port_availability(host, port):
    """Check if a port is available."""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        try:
            sock.bind((host, port))
            return True
        except socket.error:
            return False


def find_free_port(start_port=8000, max_port=8020):
    """Find a free port in range."""
    for port in range(start_port, max_port + 1):
        if check_port_availability('127.0.0.1', port):
            return port
    return None


def create_app():
    """Create FastAPI app with detailed logging."""
    logger.info("Creating FastAPI application...")
    app = FastAPI()

    logger.info("Configuring CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """Test endpoint."""
        logger.info("Root endpoint called")
        return {"status": "ok", "message": "Debug server running"}

    return app


if __name__ == "__main__":
    import uvicorn

    # Try to find an available port
    port = find_free_port()
    if not port:
        logger.error("No available ports found in range 8000-8020")
        sys.exit(1)

    logger.info(f"Found available port: {port}")

    try:
        # Create and configure the app
        app = create_app()

        # Start with detailed logging and localhost only
        logger.info(f"Starting server on port {port}...")
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=port,
            log_level="debug",
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        logger.debug("Exception details:", exc_info=True)
        sys.exit(1)
