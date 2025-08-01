#!/usr/bin/env python3
"""
LLaMA GPU Dashboard Startup Script
Simple script to start the GUI dashboard
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Start the dashboard."""
    print("🚀 Starting LLaMA GPU Dashboard...")
    print("📍 URL: http://localhost:5000")
    print("⚠️  Press Ctrl+C to stop\n")

    try:
        from src.dashboard import app, socketio
        socketio.run(app,
                    debug=False,  # Set to False for production
                    host='0.0.0.0',
                    port=5000)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure you're in the virtual environment and dependencies are installed:")
        print("  ./venv/bin/pip install flask flask-socketio")
        return 1
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
