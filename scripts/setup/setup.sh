#!/bin/bash
# One-line installer for Llama-GPU setup

echo "🚀 Setting up Llama-GPU environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q fastapi uvicorn websockets python-multipart requests

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd llama-gui
npm install --silent

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  npm start"
echo ""
echo "To test the connection:"
echo "  cd .. && ./quick_test.sh"
