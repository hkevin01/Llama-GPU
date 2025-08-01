#!/bin/bash

# Llama-GPU Interface Startup Script
# This script starts the GUI application in development mode

echo "🚀 Starting Llama-GPU Interface..."
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or later."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Navigate to the GUI directory
cd llama-gui

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        exit 1
    fi
fi

echo "🌐 Starting React development server..."
echo "📱 The application will open at: http://localhost:3000"
echo "🔄 Hot reload is enabled for development"
echo ""
echo "💡 To run as desktop app instead, use: npm run electron-dev"
echo "⚡ To build for production, use: npm run build"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Start the development server
npm start
