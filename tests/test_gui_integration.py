#!/usr/bin/env python3
"""
Test GUI Integration
Tests the React GUI integration with the API server to verify Part D requirements
"""

import json
import os
import signal
import subprocess
import time

import requests


def start_api_server():
    """Start the API server in background."""
    print("🚀 Starting API server...")

    # Change to project directory
    project_dir = "/home/kevin/Projects/Llama-GPU"

    # Start API server
    cmd = [
        "bash", "-c",
        f"cd {project_dir} && source venv/bin/activate && python -m src.api_server"
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait for server to start
    time.sleep(3)

    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        if response.status_code == 200:
            print("✅ API server started successfully")
            return process
        else:
            print(f"❌ API server health check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ API server failed to start: {e}")
        return None


def test_gui_dependencies():
    """Test GUI dependencies are installed."""
    print("📦 Testing GUI dependencies...")

    gui_dir = "/home/kevin/Projects/Llama-GPU/llama-gui"

    try:
        # Check if node_modules exists
        if os.path.exists(f"{gui_dir}/node_modules"):
            print("✅ Node modules installed")
        else:
            print("❌ Node modules not found")
            return False

        # Check package.json
        if os.path.exists(f"{gui_dir}/package.json"):
            print("✅ Package.json found")
        else:
            print("❌ Package.json not found")
            return False

        return True
    except Exception as e:
        print(f"❌ GUI dependency check failed: {e}")
        return False


def test_environment_variables():
    """Test GUI environment variables are configured."""
    print("🔧 Testing GUI environment variables...")

    gui_dir = "/home/kevin/Projects/Llama-GPU/llama-gui"
    env_file = f"{gui_dir}/.env.development"

    try:
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                content = f.read()

            if "REACT_APP_API_BASE=http://localhost:8000" in content:
                print("✅ API base URL configured correctly")
            else:
                print("❌ API base URL not configured correctly")
                return False

            if "REACT_APP_WS_URL=ws://localhost:8000/v1/stream" in content:
                print("✅ WebSocket URL configured correctly")
            else:
                print("❌ WebSocket URL not configured correctly")
                return False

            return True
        else:
            print("❌ .env.development file not found")
            return False
    except Exception as e:
        print(f"❌ Environment variable check failed: {e}")
        return False


def test_api_services():
    """Test the API services file configuration."""
    print("🔗 Testing API services configuration...")

    api_file = "/home/kevin/Projects/Llama-GPU/llama-gui/src/services/api.js"

    try:
        if os.path.exists(api_file):
            with open(api_file, 'r') as f:
                content = f.read()

            checks = [
                ("API_BASE environment variable", "process.env.REACT_APP_API_BASE"),
                ("postCompletion function", "postCompletion"),
                ("postChatCompletion function", "postChatCompletion"),
                ("openStream function", "openStream"),
                ("/v1/completions endpoint", "/v1/completions"),
                ("/v1/chat/completions endpoint", "/v1/chat/completions"),
                ("WebSocket URL", "REACT_APP_WS_URL"),
            ]

            all_good = True
            for check_name, search_term in checks:
                if search_term in content:
                    print(f"✅ {check_name} found")
                else:
                    print(f"❌ {check_name} not found")
                    all_good = False

            return all_good
        else:
            print("❌ API services file not found")
            return False
    except Exception as e:
        print(f"❌ API services check failed: {e}")
        return False


def test_gui_build():
    """Test if GUI can be built successfully."""
    print("🔨 Testing GUI build...")

    gui_dir = "/home/kevin/Projects/Llama-GPU/llama-gui"

    try:
        # Try to build the React app
        cmd = ["npm", "run", "build"]

        process = subprocess.run(
            cmd,
            cwd=gui_dir,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if process.returncode == 0:
            print("✅ GUI builds successfully")
            return True
        else:
            print(f"❌ GUI build failed: {process.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ GUI build timed out")
        return False
    except Exception as e:
        print(f"❌ GUI build error: {e}")
        return False


def test_gui_api_integration():
    """Test GUI can communicate with API server."""
    print("🔄 Testing GUI-API integration...")

    # The API services should work with our running server
    try:
        # Test if API endpoints are accessible from GUI perspective
        api_base = "http://localhost:8000"

        # Test completions endpoint
        payload = {
            "prompt": "Hello from GUI test",
            "max_tokens": 20,
            "temperature": 0.7,
            "model": "llama-base"
        }

        response = requests.post(f"{api_base}/v1/completions",
                               json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ GUI can call completions endpoint")
        else:
            print(f"❌ GUI completions endpoint failed: {response.status_code}")
            return False

        # Test chat completions endpoint
        chat_payload = {
            "messages": [{"role": "user", "content": "Hello from GUI test"}],
            "max_tokens": 20,
            "temperature": 0.7,
            "model": "llama-base"
        }

        response = requests.post(f"{api_base}/v1/chat/completions",
                               json=chat_payload, timeout=10)
        if response.status_code == 200:
            print("✅ GUI can call chat completions endpoint")
        else:
            print(f"❌ GUI chat completions endpoint failed: {response.status_code}")
            return False

        return True
    except Exception as e:
        print(f"❌ GUI-API integration test failed: {e}")
        return False


def main():
    """Run all GUI integration tests."""
    print("🎨 Testing GUI Wiring and Integration")
    print("=" * 60)

    # Start API server
    server_process = start_api_server()
    if not server_process:
        print("❌ Cannot proceed without API server")
        return False

    try:
        tests = [
            ("GUI Dependencies", test_gui_dependencies),
            ("Environment Variables", test_environment_variables),
            ("API Services Configuration", test_api_services),
            ("GUI-API Integration", test_gui_api_integration),
            ("GUI Build", test_gui_build),
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            result = test_func()
            results.append(result)

        # Summary
        passed = sum(results)
        total = len(results)
        print(f"\n📊 Test Results: {passed}/{total} passed")

        if passed == total:
            print("🎉 All GUI integration tests passed!")
            return True
        else:
            print("⚠️ Some GUI integration tests failed")
            return False

    finally:
        # Clean up - stop API server
        if server_process:
            print("\n🛑 Stopping API server...")
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
            server_process.wait()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
    exit(0 if success else 1)
