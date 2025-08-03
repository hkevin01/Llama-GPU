#!/bin/bash

# Script to start the Llama-GPU Dashboard and API Server
echo "🚀 Starting Llama-GPU System..."

# Navigate to the project root
cd "$(dirname "$0")/.." || exit

# Function to check if a port is available
check_port() {
    local port=$1
    if ! ss -tuln | grep -q ":${port} "; then
        return 0
    else
        return 1
    fi
}

# Function to find the next available port starting from a base port
find_available_port() {
    local base_port=$1
    local max_port=$((base_port + 10))
    local port=$base_port

    while [ $port -lt $max_port ]; do
        if check_port "$port"; then
            echo "$port"
            return 0
        fi
        port=$((port + 1))
    done
    return 1
}

# Function to setup Python virtual environment
setup_python_env() {
    echo "🐍 Setting up Python environment..."

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi

    # Remove old log files if they exist
    rm -f api_server.log gui.log

    # Activate virtual environment
    source venv/bin/activate || { echo "❌ Failed to activate virtual environment"; return 1; }

    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip || { echo "❌ Failed to upgrade pip"; return 1; }
    pip install -r requirements.txt || { echo "❌ Failed to install requirements"; return 1; }
}

# Function to wait for API server to be ready
wait_for_api() {
    local max_attempts=30
    local attempt=1

    echo "⏳ Waiting for API server to start..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            echo "✅ API server is ready!"
            return 0
        fi

        # Check if the process is still running
        if ! kill -0 $API_PID 2>/dev/null; then
            echo "❌ API server process has died"
            if [ -f "api_server.log" ]; then
                echo "📝 API server log:"
                tail -n 20 api_server.log
            fi
            return 1
        fi

        # Show progress
        if [ $((attempt % 2)) -eq 0 ]; then
            echo -n "."
        fi

        sleep 1
        attempt=$((attempt + 1))
    done
    echo

    echo "❌ API server failed to start within 30 seconds"
    if [ -f "api_server.log" ]; then
        echo "📝 API server log:"
        tail -n 20 api_server.log
    fi
    return 1
}

# Start API Server
start_api_server() {
    # Kill any existing processes on port 8000
    if ! check_port 8000; then
        echo "⚠️ Port 8000 is in use, cleaning up old processes..."
        pkill -f "python.*mock_api_server" || true
        sleep 2
    fi

    echo "🔧 Starting API server..."
    setup_python_env || exit 1

    # Start the API server
    API_PORT=8000
    echo "🚀 Starting API on port $API_PORT..."
    PORT=$API_PORT ./venv/bin/python -u mock_api_server.py > api_server.log 2>&1 &
    API_PID=$!

    # Wait for API to be ready
    wait_for_api
    if [ $? -ne 0 ]; then
        echo "❌ Failed to start API server"
        kill $API_PID 2>/dev/null
        exit 1
    fi

    export API_PORT
}

# Start GUI
start_gui() {
    cd llama-gui || exit

    # Check if node_modules exists, if not run npm install
    echo "📦 Installing/updating GUI dependencies..."
    npm install --quiet

    # Try ports in sequence for GUI
    PORTS=(3001 3002 3003 3000)
    PORT_FOUND=0

    for PORT in "${PORTS[@]}"; do
        if check_port "$PORT"; then
            export PORT="$PORT"
            PORT_FOUND=1
            echo "✅ Using port $PORT for GUI"
            break
        fi
    done

    if [ "$PORT_FOUND" -eq 0 ]; then
        echo "⚠️ None of the preferred ports (3001, 3002, 3003, 3000) are available for GUI."
        echo "Please free up a port and try again."
        exit 1
    fi
}

# Cleanup function for graceful shutdown
cleanup() {
    echo
    echo "🛑 Shutting down services..."

    # Kill the specific processes we started
    if [ -n "$API_PID" ]; then
        echo "Stopping API server..."
        kill $API_PID 2>/dev/null || true
    fi

    if [ -n "$NPM_PID" ]; then
        echo "Stopping GUI server..."
        kill $NPM_PID 2>/dev/null || true
    fi

    # Additional cleanup of any stragglers
    pkill -f "python.*mock_api_server.py" 2>/dev/null || true
    pkill -f "node.*react-scripts start" 2>/dev/null || true

    # Wait a moment for processes to stop gracefully
    sleep 1

    # Force kill any remaining processes
    pkill -9 -f "python.*mock_api_server.py" 2>/dev/null || true
    pkill -9 -f "node.*react-scripts start" 2>/dev/null || true

    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate || true
    fi

    echo "✨ Cleanup complete"
    exit 0
}

# Register cleanup function
trap cleanup SIGINT SIGTERM

# Main execution
start_api_server || { cleanup; exit 1; }
start_gui || { cleanup; exit 1; }

    # Start the React development server
    echo "🌟 Starting React development server on port $PORT..."
    REACT_APP_API_PORT=$API_PORT PORT=$PORT npm start  # Monitor both processes
while kill -0 $API_PID 2>/dev/null && kill -0 $NPM_PID 2>/dev/null; do
    sleep 1
done

# If either process died, clean up and exit
echo "❌ One of the services has terminated"
cleanup
