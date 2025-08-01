#!/bin/bash

# Llama-GPU Interface Validation Script
# This script checks if the GUI application is properly set up

echo "🔍 Validating Llama-GPU Interface Setup..."
echo "=========================================="

# Check Node.js version
echo "📋 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js is installed: $NODE_VERSION"

    # Check if version is 16 or higher
    MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1 | cut -d'v' -f2)
    if [ "$MAJOR_VERSION" -ge 16 ]; then
        echo "✅ Node.js version is compatible (16+)"
    else
        echo "⚠️  Node.js version is $MAJOR_VERSION. Recommended: 16+"
    fi
else
    echo "❌ Node.js is not installed"
fi

# Check npm
echo ""
echo "📋 Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm is installed: $NPM_VERSION"
else
    echo "❌ npm is not installed"
fi

# Check GUI directory
echo ""
echo "📋 Checking project structure..."
if [ -d "llama-gui" ]; then
    echo "✅ GUI directory exists"

    # Check package.json
    if [ -f "llama-gui/package.json" ]; then
        echo "✅ package.json found"
    else
        echo "❌ package.json not found"
    fi

    # Check source files
    if [ -f "llama-gui/src/App.js" ]; then
        echo "✅ App.js found"
    else
        echo "❌ App.js not found"
    fi

    if [ -f "llama-gui/src/context/AppContext.js" ]; then
        echo "✅ AppContext.js found"
    else
        echo "❌ AppContext.js not found"
    fi

    # Check dependencies
    if [ -d "llama-gui/node_modules" ]; then
        echo "✅ Dependencies are installed"
    else
        echo "⚠️  Dependencies not installed (run: npm install)"
    fi

else
    echo "❌ GUI directory not found"
fi

# Check for Python backend (optional)
echo ""
echo "📋 Checking backend integration..."
if [ -f "src/api_server.py" ]; then
    echo "✅ Python backend found"
else
    echo "ℹ️  Python backend not found (optional for GUI development)"
fi

# Check for GPU support (optional)
echo ""
echo "📋 Checking GPU support..."
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU tools available"
    GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
    echo "🎮 GPUs detected: $GPU_COUNT"
else
    echo "ℹ️  NVIDIA GPU tools not found (optional for full functionality)"
fi

echo ""
echo "=========================================="
echo "🎯 Setup Summary:"
echo ""

# Overall status
ERRORS=0
WARNINGS=0

if ! command -v node &> /dev/null; then
    echo "❌ Install Node.js (https://nodejs.org/)"
    ERRORS=$((ERRORS+1))
fi

if ! command -v npm &> /dev/null; then
    echo "❌ Install npm (comes with Node.js)"
    ERRORS=$((ERRORS+1))
fi

if [ ! -d "llama-gui" ]; then
    echo "❌ GUI directory missing"
    ERRORS=$((ERRORS+1))
fi

if [ ! -d "llama-gui/node_modules" ] && [ -d "llama-gui" ]; then
    echo "⚠️  Run: cd llama-gui && npm install"
    WARNINGS=$((WARNINGS+1))
fi

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "🎉 Everything looks good! Ready to start the GUI."
    echo ""
    echo "🚀 To start the application:"
    echo "   ./start-gui.sh"
    echo ""
    echo "🖥️  To run as desktop app:"
    echo "   cd llama-gui && npm run electron-dev"
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  Setup is mostly complete, but there are warnings above."
    echo "🚀 You can try starting the application with: ./start-gui.sh"
else
    echo "❌ Please fix the errors above before starting the application."
fi

echo "=========================================="
