#!/usr/bin/env python3
"""
Connection test utility for the Llama-GPU mock server
"""

import asyncio
import json
import sys
import time
from urllib.parse import urlparse

import requests
import websockets


def test_http_health(base_url="http://localhost:8000"):
    """Test HTTP health endpoint"""
    print(f"🔍 Testing HTTP health endpoint: {base_url}/health")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ HTTP Health OK: {data}")
            return True
        else:
            print(f"❌ HTTP Health failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTTP Health error: {e}")
        return False


async def test_websocket_connection(ws_url="ws://localhost:8000/v1/stream"):
    """Test WebSocket connection"""
    print(f"🔍 Testing WebSocket connection: {ws_url}")
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connected successfully")

            # Send a test message
            test_message = {
                "type": "message",
                "content": "Hello, test message",
                "timestamp": time.time()
            }

            await websocket.send(json.dumps(test_message))
            print("📤 Test message sent")

            # Wait for responses
            response_count = 0
            while response_count < 5:  # Get a few responses
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(response)
                    print(f"📥 Response {response_count + 1}: {data.get('type', 'unknown')}")
                    response_count += 1

                    if data.get('type') == 'end':
                        break

                except asyncio.TimeoutError:
                    print("⏰ WebSocket response timeout")
                    break

            print("✅ WebSocket test completed")
            return True

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        return False


def main():
    """Run connection tests"""
    print("🚀 Starting connection tests...")

    # Test different ports
    ports = [8000, 8001, 8002]
    success = False

    for port in ports:
        print(f"\n--- Testing port {port} ---")
        base_url = f"http://localhost:{port}"
        ws_url = f"ws://localhost:{port}/v1/stream"

        if test_http_health(base_url):
            if asyncio.run(test_websocket_connection(ws_url)):
                print(f"🎉 Success! Server is running on port {port}")
                success = True
                break
        else:
            print(f"❌ No server found on port {port}")

    if not success:
        print("\n💥 No working server found on any port!")
        print("Make sure to start the server with:")
        print("python mock_api_server.py --port 8000")
        sys.exit(1)
    else:
        print(f"\n🎉 All tests passed!")


if __name__ == "__main__":
    main()
