#!/usr/bin/env python3
"""
GUI Dashboard Test Runner for LLaMA GPU
Starts the Flask dashboard with proper configuration
"""

import logging
import os
import sys
import importlib.metadata

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def get_package_version(package_name):
    """Get package version using importlib.metadata for compatibility."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"

def test_imports():
    """Test all required imports."""
    print("🧪 Testing imports...")

    try:
        import flask
        version = get_package_version("flask")
        print(f"✅ Flask {version}")
    except ImportError as e:
        print(f"❌ Flask import error: {e}")
        return False

    try:
        import flask_socketio
        version = get_package_version("flask-socketio")
        print(f"✅ Flask-SocketIO {version}")
    except ImportError as e:
        print(f"❌ Flask-SocketIO import error: {e}")
        print("💡 Install with: pip install flask-socketio")
        return False

    try:
        from src.dashboard import app, socketio
        print("✅ Dashboard app imports successfully")
    except ImportError as e:
        print(f"❌ Dashboard import error: {e}")
        print("💡 Make sure src/dashboard.py exists and is properly configured")
        return False

    try:
        from src.plugin_manager import PluginManager
        pm = PluginManager()
        print("✅ Plugin Manager imports successfully")
    except ImportError as e:
        print(f"❌ Plugin Manager import error: {e}")
        print("💡 Plugin Manager is optional, continuing...")

    return True

def check_directories():
    """Check required directories exist."""
    print("\n📁 Checking directories...")

    dirs_to_check = [
        'src/templates',
        'src/templates/dashboard',
        'src/static',
        'src/static/css',
        'src/static/js',
        'logs'
    ]

    all_exist = True
    for dir_path in dirs_to_check:
        if os.path.exists(dir_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} (missing)")
            all_exist = False

    return all_exist

def test_templates():
    """Test template rendering."""
    print("\n🎨 Testing templates...")

    try:
        from src.dashboard import app
        with app.test_client() as client:
            # Test main dashboard
            response = client.get('/')
            if response.status_code == 200:
                print("✅ Dashboard index renders successfully")
            else:
                print(f"❌ Dashboard index failed: {response.status_code}")
                return False

            # Test plugins API
            response = client.get('/plugins')
            if response.status_code == 200:
                print("✅ Plugins API responds successfully")
            else:
                print(f"❌ Plugins API failed: {response.status_code}")
                return False

    except Exception as e:
        print(f"❌ Template test error: {e}")
        return False

    return True

def run_dashboard():
    """Run the dashboard server."""
    print("\n🚀 Starting LLaMA GPU Dashboard...")
    print("📍 URL: http://localhost:5000")
    print("🔄 Real-time updates enabled")
    print("⚠️  Press Ctrl+C to stop\n")

    try:
        from src.dashboard import app, socketio
        socketio.run(app,
                    debug=True,
                    host='0.0.0.0',
                    port=5000,
                    allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")
        return False

    return True

def main():
    """Main test runner."""
    print("🎯 LLaMA GPU Dashboard - GUI Test Runner")
    print("=" * 50)

    # Run tests
    if not test_imports():
        print("\n❌ Import tests failed. Cannot continue.")
        return 1

    if not check_directories():
        print("\n❌ Directory check failed. Some files may be missing.")
        return 1

    if not test_templates():
        print("\n❌ Template tests failed. Check Flask configuration.")
        return 1

    print("\n✅ All tests passed! Starting dashboard...")

    # Run dashboard
    if not run_dashboard():
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
