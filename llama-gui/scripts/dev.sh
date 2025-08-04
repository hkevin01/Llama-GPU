#!/bin/bash

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to find an available port
find_available_port() {
    local port=$1
    while check_port $port; do
        port=$((port + 1))
    done
    echo $port
}

# Get available ports for frontend and backend
FRONTEND_PORT=$(find_available_port 3000)
BACKEND_PORT=$(find_available_port 8000)

# Export the ports so they're available to the React app
export PORT=$FRONTEND_PORT
export REACT_APP_API_PORT=$BACKEND_PORT

echo "Starting Llama-GPU development environment..."
echo "Frontend will run on port $FRONTEND_PORT"
echo "Backend will run on port $BACKEND_PORT"

# Update the config file with the correct port
sed -i "s/localhost:[0-9]\+/localhost:$BACKEND_PORT/" src/config/llm-config.js

# Start both servers
echo "Starting mock API server..."
cd ..
python3 -m uvicorn mock_api_server:app --reload --port $BACKEND_PORT --host 0.0.0.0 &
MOCK_SERVER_PID=$!

echo "Starting frontend development server..."
cd llama-gui
npm start &
FRONTEND_PID=$!

# Handle cleanup on script exit
cleanup() {
    echo "Shutting down servers..."
    kill $MOCK_SERVER_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
}

trap cleanup EXIT

# Wait for both processes
wait $MOCK_SERVER_PID $FRONTEND_PID
