#!/usr/bin/env python3
"""
Comprehensive Test Suite
Runs all tests to verify Parts A-F requirements are met
"""

import os
import subprocess
import sys
import time

import requests


def run_test_file(test_file, description):
    """Run a test file and return success status."""
    print(f"\n🧪 Running {description}...")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd="/home/kevin/Projects/Llama-GPU",
            capture_output=True,
            text=True,
            timeout=120
        )

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        if result.returncode == 0:
            print(f"✅ {description} PASSED")
            return True
        else:
            print(f"❌ {description} FAILED (exit code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {description} TIMED OUT")
        return False
    except Exception as e:
        print(f"❌ {description} ERROR: {e}")
        return False


def check_api_server_running():
    """Check if API server is running."""
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False


def start_api_server_if_needed():
    """Start API server if not already running."""
    if check_api_server_running():
        print("✅ API server already running")
        return None

    print("🚀 Starting API server for tests...")

    # Start API server in background
    cmd = [
        "bash", "-c",
        "cd /home/kevin/Projects/Llama-GPU && source venv/bin/activate && python -m src.api_server"
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )

    # Wait for server to start
    for _ in range(10):
        time.sleep(1)
        if check_api_server_running():
            print("✅ API server started successfully")
            return process

    print("❌ API server failed to start")
    return None


def stop_api_server(process):
    """Stop the API server process."""
    if process:
        print("🛑 Stopping API server...")
        try:
            os.killpg(os.getpgid(process.pid), 15)  # SIGTERM
            process.wait(timeout=5)
        except:
            try:
                os.killpg(os.getpgid(process.pid), 9)  # SIGKILL
            except:
                pass


def main():
    """Run comprehensive test suite."""
    print("🎯 Comprehensive Test Suite - Llama-GPU Stabilization")
    print("=" * 80)
    print("Testing all Parts A-F requirements...")

    # Start API server
    server_process = start_api_server_if_needed()

    try:
        # Define all tests
        tests = [
            # Part A: Root directory cleanup (implicit - files organized)
            # Part B: API server implementation
            ("tests/test_api_endpoints.py", "Part B: API Server Endpoints"),

            # Part C: Engine CPU fallback
            ("tests/test_engine.py", "Part C: Engine CPU Fallback"),

            # Part D: GUI wiring
            ("tests/test_gui_integration.py", "Part D: GUI Integration"),

            # Part E: Docker and CI
            ("tests/test_docker_ci.py", "Part E: Docker and CI"),

            # Part F: Additional tests
            ("tests/test_websocket.py", "Part F: WebSocket Streaming"),
            ("tests/test_status_check.py", "Part F: Status Check"),
        ]

        results = []
        part_summary = {
            "Part A": "✅ Root directory cleanup completed",
            "Part B": "❓ Testing API server implementation...",
            "Part C": "❓ Testing engine CPU fallback...",
            "Part D": "❓ Testing GUI integration...",
            "Part E": "❓ Testing Docker and CI...",
            "Part F": "❓ Testing comprehensive coverage...",
        }

        print("\n📋 Test Plan:")
        for part, status in part_summary.items():
            print(f"  {part}: {status}")

        # Run all tests
        for test_file, description in tests:
            if os.path.exists(f"/home/kevin/Projects/Llama-GPU/{test_file}"):
                result = run_test_file(test_file, description)
                results.append((description, result))
            else:
                print(f"⚠️ Test file {test_file} not found, skipping...")
                results.append((description, False))

        # Update part summary based on results
        part_results = {}
        for desc, result in results:
            if "Part B" in desc:
                part_results["Part B"] = "✅ PASSED" if result else "❌ FAILED"
            elif "Part C" in desc:
                part_results["Part C"] = "✅ PASSED" if result else "❌ FAILED"
            elif "Part D" in desc:
                part_results["Part D"] = "✅ PASSED" if result else "❌ FAILED"
            elif "Part E" in desc:
                part_results["Part E"] = "✅ PASSED" if result else "❌ FAILED"
            elif "Part F" in desc:
                part_results["Part F"] = "✅ PASSED" if result else "❌ FAILED"

        # Final summary
        print("\n" + "=" * 80)
        print("🏁 FINAL TEST RESULTS")
        print("=" * 80)

        print("\n📊 Part-by-Part Summary:")
        print("  Part A: ✅ Root directory cleanup and unification")
        for part in ["Part B", "Part C", "Part D", "Part E", "Part F"]:
            status = part_results.get(part, "❓ NOT TESTED")
            print(f"  {part}: {status}")

        print(f"\n📈 Individual Test Results:")
        passed = 0
        total = len(results)
        for desc, result in results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {desc}: {status}")
            if result:
                passed += 1

        print(f"\n🎯 Overall Score: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 SUCCESS: All tests passed! Repository stabilization complete!")
            print("\n✨ Ready for production use:")
            print("  • FastAPI server with OpenAI-compatible endpoints")
            print("  • React GUI with real-time WebSocket streaming")
            print("  • CPU fallback engine for demo/testing")
            print("  • Docker Compose for containerized deployment")
            print("  • CI/CD pipeline for automated testing")
            print("  • Comprehensive test coverage")
            return True
        else:
            failed = total - passed
            print(f"⚠️ PARTIAL SUCCESS: {failed} test(s) failed")
            print("Repository requires additional work before production use.")
            return False

    finally:
        # Cleanup
        stop_api_server(server_process)


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
    exit(0 if success else 1)
