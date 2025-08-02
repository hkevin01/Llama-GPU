#!/usr/bin/env python3
"""
LLaMA GPU Dashboard Launcher
Starts both Flask API backend and React frontend dashboard
"""

import importlib.metadata
import logging
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def get_package_version(package_name):
    """Get package version using importlib.metadata for compatibility."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def test_python_dependencies():
    """Test Python backend dependencies."""
    print("🐍 Testing Python dependencies...")

    required_packages = [
        ("flask", "Flask"),
        ("flask-socketio", "Flask-SocketIO"),
    ]

    missing_packages = []

    for package_name, display_name in required_packages:
        try:
            __import__(package_name.replace("-", "_"))
            version = get_package_version(package_name)
            print(f"✅ {display_name} {version}")
        except ImportError:
            print(f"❌ {display_name} not found")
            missing_packages.append(package_name)

    if missing_packages:
        print(f"\n💡 Install missing packages: pip install {' '.join(missing_packages)}")
        return False

    return True


def test_node_dependencies():
    """Test Node.js and React dependencies."""
    print("\n📦 Testing Node.js dependencies...")

    # Check if Node.js is available
    try:
        result = subprocess.run(['node', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not responding properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Node.js not found")
        print("💡 Install Node.js from https://nodejs.org/")
        return False

    # Check React GUI directory
    gui_dir = project_root / "llama-gui"
    if not gui_dir.exists():
        print("❌ React GUI directory not found")
        return False

    # Check package.json
    package_json = gui_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found in llama-gui/")
        return False

    print("✅ React GUI structure found")

    # Check if node_modules exists
    node_modules = gui_dir / "node_modules"
    if not node_modules.exists():
        print("⚠️  Node modules not installed")
        print("💡 Run 'npm install' in llama-gui/ directory")
        return False

    print("✅ Node modules installed")
    return True


def test_backend_imports():
    """Test backend imports."""
    print("\n🔧 Testing backend imports...")

    try:
        from src.dashboard import app, socketio
        print("✅ Dashboard app imports successfully")
    except ImportError as e:
        print(f"❌ Dashboard import error: {e}")
        return False

    try:
        from src.api_server import app as api_app
        print("✅ API server imports successfully")
    except ImportError as e:
        print(f"⚠️  API server import warning: {e}")
        print("💡 API server is optional for basic dashboard")

    return True


def start_flask_backend():
    """Start Flask backend server."""
    print("🚀 Starting Flask backend...")

    try:
        from src.dashboard import app, socketio

        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Start SocketIO server
        socketio.run(app,
                    debug=False,
                    host='0.0.0.0',
                    port=5000,
                    allow_unsafe_werkzeug=True)

    except Exception as e:
        print(f"❌ Flask backend error: {e}")
        return False


def start_react_frontend():
    """Start React frontend development server."""
    print("⚛️  Starting React frontend...")

    gui_dir = project_root / "llama-gui"

    try:
        # Change to GUI directory and start React dev server
        os.chdir(gui_dir)
        result = subprocess.run(['npm', 'start'],
                              env={**os.environ, 'BROWSER': 'none'})
        return result.returncode == 0

    except Exception as e:
        print(f"❌ React frontend error: {e}")
        return False


def start_full_stack():
    """Start both backend and frontend in separate threads."""
    print("\n🎯 Starting Full Stack Dashboard...")
    print("=" * 50)

    # Start Flask backend in a thread
    backend_thread = threading.Thread(target=start_flask_backend, daemon=True)
    backend_thread.start()

    # Give backend time to start
    print("⏳ Waiting for backend to start...")
    time.sleep(3)

    print("📍 Backend API: http://localhost:5000")
    print("📍 Frontend Dashboard: http://localhost:3000")
    print("🔄 Real-time updates enabled")
    print("⚠️  Press Ctrl+C to stop both servers\n")

    try:
        # Start React frontend (this will block)
        start_react_frontend()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main dashboard launcher."""
    print("🎯 LLaMA GPU Dashboard Launcher")
    print("=" * 50)

    # Test dependencies
    if not test_python_dependencies():
        print("\n❌ Python dependency check failed.")
        return 1

    if not test_node_dependencies():
        print("\n❌ Node.js dependency check failed.")
        print("💡 You can still run Flask-only mode")

        choice = input("\nRun Flask-only dashboard? (y/n): ").lower()
        if choice == 'y':
            print("\n🚀 Starting Flask-only dashboard...")
            print("📍 URL: http://localhost:5000")
            start_flask_backend()
            return 0
        else:
            return 1

    if not test_backend_imports():
        print("\n❌ Backend import check failed.")
        return 1

    print("\n✅ All checks passed!")

    # Ask user preference
    print("\nChoose dashboard mode:")
    print("1. Full Stack (Flask + React) - Recommended")
    print("2. Flask Only (Simple dashboard)")
    print("3. React Only (Frontend development)")

    try:
        choice = input("\nEnter choice (1-3) [1]: ").strip() or "1"

        if choice == "1":
            start_full_stack()
        elif choice == "2":
            print("\n🚀 Starting Flask dashboard...")
            print("📍 URL: http://localhost:5000")
            start_flask_backend()
        elif choice == "3":
            print("\n⚛️  Starting React dashboard...")
            print("📍 URL: http://localhost:3000")
            start_react_frontend()
        else:
            print("❌ Invalid choice")
            return 1

    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
