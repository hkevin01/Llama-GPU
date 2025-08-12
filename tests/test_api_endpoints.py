#!/usr/bin/env python3
"""
Test API Server Endpoints
Tests the FastAPI server endpoints to verify Part B requirements
"""

import asyncio
import time

import requests
import websockets


def test_health_endpoint() -> bool:
    """Test the /health endpoint."""
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health endpoint: {data}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False


def test_completions_endpoint() -> bool:
    """Test the /v1/completions endpoint."""
    try:
        payload = {
            "prompt": "Hello, world!",
            "max_tokens": 50,
            "temperature": 0.7
        }
        response = requests.post("http://localhost:8000/v1/completions",
                                 json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Completions endpoint: {data}")
            return True
        else:
            print(f"❌ Completions endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Completions endpoint error: {e}")
        return False


def test_chat_completions_endpoint() -> bool:
    """Test the /v1/chat/completions endpoint."""
    try:
        payload = {
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
        response = requests.post("http://localhost:8000/v1/chat/completions",
                                 json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat completions endpoint: {data}")
            return True
        else:
            print(f"❌ Chat completions endpoint failed: "
                  f"{response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Chat completions endpoint error: {e}")
        return False


async def test_websocket_endpoint() -> bool:
    """Test the /v1/stream WebSocket endpoint."""
    try:
        uri = "ws://localhost:8000/v1/stream"
        async with websockets.connect(uri) as websocket:
            # Send a test prompt (expects text, not JSON)
            test_prompt = "Hello, world!"
            await websocket.send(test_prompt)

            # Receive streaming response
            responses = []
            try:
                while True:
                    response = await asyncio.wait_for(
                        websocket.recv(), timeout=5.0)
                    responses.append(response)
                    if len(responses) >= 3:  # Get a few tokens
                        break
            except asyncio.TimeoutError:
                pass  # Expected when stream ends
            except websockets.exceptions.ConnectionClosed:
                pass  # Expected when stream completes

            if responses:
                print(f"✅ WebSocket endpoint: received {len(responses)} "
                      f"tokens: {responses[:2]}...")
                return True
            else:
                print("❌ WebSocket endpoint: no response received")
                return False
    except Exception as e:
        print(f"❌ WebSocket endpoint error: {e}")
        return False


def main() -> bool:
    """Run all API tests."""
    print("🧪 Testing API Server Endpoints")
    print("=" * 50)

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)

    results = []

    # Test HTTP endpoints
    results.append(test_health_endpoint())
    results.append(test_completions_endpoint())
    results.append(test_chat_completions_endpoint())

    # Test WebSocket endpoint
    try:
        ws_result = asyncio.run(test_websocket_endpoint())
        results.append(ws_result)
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All API endpoints working!")
        return True
    else:
        print("⚠️ Some endpoints failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
    exit(0 if success else 1)
