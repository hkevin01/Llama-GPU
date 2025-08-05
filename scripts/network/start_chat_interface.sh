#!/bin/bash
# Complete Start Script for LLaMA-GPU Real-Time Chat

echo "🚀 Starting LLaMA-GPU Real-Time Chat Interface"
echo "=============================================="

# Check if we're in the right directory
if [ ! -d "llama-gui" ]; then
    echo "❌ Error: llama-gui directory not found"
    echo "💡 Please run this script from /home/kevin/Projects/Llama-GPU"
    exit 1
fi

echo "📋 Starting components..."

# Start mock API server in background
echo "🖥️  Starting mock API server..."
python3 mock_api_server.py &
API_PID=$!

# Wait for API server to start
sleep 3

# Start React app
echo "⚛️  Starting React application..."
cd llama-gui
npm start &
REACT_PID=$!

echo ""
echo "✅ All services started!"
echo "🌐 Chat Interface: http://localhost:3000/chat"
echo "📡 API Server: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

echo ""
echo "🛑 To stop all services:"
echo "   kill $API_PID $REACT_PID"

# Keep script running
wait
