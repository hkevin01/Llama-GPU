#!/usr/bin/env python3
"""
Test WebSocket Streaming
Tests the WebSocket streaming functionality in detail
"""

import asyncio
import json
import time

import websockets


async def test_websocket_connection():
    """Test basic WebSocket connection."""
    try:
        uri = "ws://localhost:8000/v1/stream"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connection established")
            return True
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return False


async def test_websocket_echo():
    """Test WebSocket echo functionality."""
    try:
        uri = "ws://localhost:8000/v1/stream"
        async with websockets.connect(uri) as websocket:
            # Send a test message
            test_prompt = "Test echo"
            await websocket.send(test_prompt)

            # Receive response
            response = await asyncio.wait_for(websocket.recv(), timeout=10.0)

            if response:
                print(f"✅ WebSocket echo received: {response[:50]}...")
                return True
            else:
                print("❌ WebSocket echo failed: no response")
                return False
    except Exception as e:
        print(f"❌ WebSocket echo failed: {e}")
        return False


async def test_websocket_streaming():
    """Test WebSocket streaming with multiple tokens."""
    try:
        uri = "ws://localhost:8000/v1/stream"
        async with websockets.connect(uri) as websocket:
            # Send a prompt that should generate multiple tokens
            test_prompt = "Tell me a story about"
            await websocket.send(test_prompt)

            # Collect streaming tokens
            tokens = []
            try:
                while len(tokens) < 10:  # Collect up to 10 tokens
                    token = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    tokens.append(token)
            except asyncio.TimeoutError:
                pass  # Expected when stream ends
            except websockets.exceptions.ConnectionClosed:
                pass  # Expected when stream completes

            if len(tokens) > 0:
                print(f"✅ WebSocket streaming received {len(tokens)} tokens")
                print(f"   First few: {tokens[:3]}")
                return True
            else:
                print("❌ WebSocket streaming failed: no tokens received")
                return False
    except Exception as e:
        print(f"❌ WebSocket streaming failed: {e}")
        return False


async def test_websocket_concurrent():
    """Test multiple concurrent WebSocket connections."""
    try:
        uri = "ws://localhost:8000/v1/stream"

        async def single_connection(connection_id):
            async with websockets.connect(uri) as websocket:
                prompt = f"Connection {connection_id} test"
                await websocket.send(prompt)
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                return response is not None

        # Test 3 concurrent connections
        tasks = [single_connection(i) for i in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = sum(1 for r in results if r is True)

        if successful >= 2:  # At least 2 out of 3 should succeed
            print(f"✅ WebSocket concurrent connections: {successful}/3 successful")
            return True
        else:
            print(f"❌ WebSocket concurrent connections failed: {successful}/3 successful")
            return False
    except Exception as e:
        print(f"❌ WebSocket concurrent test failed: {e}")
        return False


async def main():
    """Run all WebSocket tests."""
    print("🔌 Testing WebSocket Streaming Implementation")
    print("=" * 60)

    # Wait a moment to ensure server is ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)

    tests = [
        ("WebSocket Connection", test_websocket_connection),
        ("WebSocket Echo", test_websocket_echo),
        ("WebSocket Streaming", test_websocket_streaming),
        ("WebSocket Concurrent", test_websocket_concurrent),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        result = await test_func()
        results.append(result)

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n📊 Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All WebSocket tests passed!")
        return True
    else:
        print("⚠️ Some WebSocket tests failed")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
    exit(0 if success else 1)
