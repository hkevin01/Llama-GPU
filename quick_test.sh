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

# Start the server in background and capture the port
cd /home/kevin/Projects/Llama-GPU
echo "🚀 Starting test server..."
python mock_api_server.py --host 0.0.0.0 > server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start and extract port
echo "⏳ Waiting for server to start..."
sleep 5

# Extract port from server log
SERVER_PORT=$(grep -o "0.0.0.0:[0-9]*" server.log | head -1 | cut -d: -f2)
if [ -z "$SERVER_PORT" ]; then
    echo "❌ Could not determine server port"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "✅ Server started on port $SERVER_PORT"

# Test the connection with the correct port
echo "🔍 Testing connection..."
python test_connection.py --port $SERVER_PORT

# Cleanup
echo "🧹 Cleaning up..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "✅ Test completed!"
