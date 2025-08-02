#!/usr/bin/env python3
"""AIOHTTP test server."""

from aiohttp import web


async def handle(request):
    """Handle incoming requests."""
    return web.json_response({"message": "Hello from aiohttp!"})

async def init_app():
    """Initialize the app."""
    app = web.Application()
    app.router.add_get('/', handle)
    return app

if __name__ == '__main__':
    try:
        app = init_app()
        print("🚀 Starting aiohttp server...")
        web.run_app(app, host='127.0.0.1', port=0)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        import sys
        sys.exit(1)
