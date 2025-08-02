#!/bin/bash

# Script to start the Llama-GPU Dashboard
echo "🚀 Starting Llama-GPU Dashboard..."

# Navigate to the GUI directory
cd "$(dirname "$0")/../llama-gui" || exit

# Check if node_modules exists, if not run npm install
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Function to check if a port is available
check_port() {
    if ! lsof -Pi :"$1" -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Try ports in sequence
PORTS=(3001 3002 3003 3000)
PORT_FOUND=0

for PORT in "${PORTS[@]}"; do
    if check_port "$PORT"; then
        export PORT="$PORT"
        PORT_FOUND=1
        echo "✅ Using port $PORT"
        break
    fi
done

if [ "$PORT_FOUND" -eq 0 ]; then
    echo "⚠️ None of the preferred ports (3001, 3002, 3003, 3000) are available. Please free up a port and try again."
    exit 1
fi

# Start the React development server
echo "🌟 Starting React development server on port $PORT..."
export PORT="$PORT"
npm start
