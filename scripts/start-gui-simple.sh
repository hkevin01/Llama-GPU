#!/bin/bash

# Simple React Dashboard Starter
# Alternative launcher that handles dependencies properly

echo "🚀 LLaMA GPU React Dashboard Starter"
echo "====================================="

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
GUI_DIR="$PROJECT_ROOT/llama-gui"

echo "📁 Project Root: $PROJECT_ROOT"
echo "📁 GUI Directory: $GUI_DIR"

# Check if GUI directory exists
if [ ! -d "$GUI_DIR" ]; then
    echo "❌ GUI directory not found: $GUI_DIR"
    exit 1
fi

cd "$GUI_DIR"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Install from: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm."
    exit 1
fi

echo "✅ npm version: $(npm --version)"

# Check package.json
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found in GUI directory"
    exit 1
fi

echo "✅ package.json found"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing React dependencies..."
    echo "⏳ This may take a few minutes..."

    # Install with legacy peer deps to handle conflicts
    npm install --legacy-peer-deps

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        echo "💡 Try running: npm install --force"
        exit 1
    fi

    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Check if react-scripts is available
if ! npm list react-scripts &> /dev/null; then
    echo "⚠️  react-scripts not found, installing..."
    npm install react-scripts --save-dev
fi

echo ""
echo "🌐 Starting React development server..."
echo "📱 Dashboard URL: http://localhost:3000"
echo "🔄 Hot reload enabled"
echo "🔧 Backend should run on: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop"
echo "====================================="

# Set environment variable to prevent browser auto-open
export BROWSER=none

# Start React development server
npm start
