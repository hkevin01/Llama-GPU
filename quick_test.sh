#!/bin/bash
echo "🧪 Testing the fixed WebSocket connection..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required dependencies
echo "📦 Installing required dependencies..."
pip install fastapi uvicorn websockets python-multipart requests > /dev/null 2>&1

# Start the server in background
cd /home/kevin/Projects/Llama-GPU
echo "🚀 Starting test server..."
python mock_api_server.py --port 8000 --host 0.0.0.0 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Test the connection
echo "🔍 Testing connection..."
python test_connection.py

# Cleanup
echo "🧹 Cleaning up..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "✅ Test completed!"
