#!/bin/bash

# Comprehensive startup script for Llama-GPU Chat Interface
# This script starts both the backend server and frontend application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is available
    fi
}

# Function to find an available port
find_available_port() {
    local start_port=$1
    local port=$start_port

    while ! check_port $port; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 100)) ]; then
            print_error "Could not find available port after checking $start_port to $port"
            exit 1
        fi
    done

    echo $port
}

# Function to cleanup background processes
cleanup() {
    print_status "Cleaning up processes..."

    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi

    # Kill any processes on our ports
    if [ ! -z "$BACKEND_PORT" ]; then
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PORT" ]; then
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi

    print_success "Cleanup completed"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Check if we're in the right directory
if [ ! -f "mock_api_server.py" ]; then
    print_error "mock_api_server.py not found. Please run this script from the Llama-GPU root directory."
    exit 1
fi

if [ ! -d "llama-gui" ]; then
    print_error "llama-gui directory not found. Please run this script from the Llama-GPU root directory."
    exit 1
fi

print_status "Starting Llama-GPU Chat Interface..."

# Check for Python virtual environment
if [ ! -d "venv" ]; then
    print_warning "Python virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt 2>/dev/null || print_warning "requirements.txt not found, installing basic dependencies..."
    pip install fastapi uvicorn websockets
else
    source venv/bin/activate
fi

# Find available ports
BACKEND_PORT=$(find_available_port 8000)
FRONTEND_PORT=$(find_available_port 3000)

print_status "Using backend port: $BACKEND_PORT"
print_status "Using frontend port: $FRONTEND_PORT"

# Start the backend server
print_status "Starting backend server on port $BACKEND_PORT..."
python mock_api_server.py --port $BACKEND_PORT --host 0.0.0.0 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend is running
if ! check_port $BACKEND_PORT; then
    print_success "Backend server started successfully on port $BACKEND_PORT"
else
    print_error "Failed to start backend server"
    exit 1
fi

# Update frontend configuration
print_status "Updating frontend configuration..."
cd llama-gui

# Create a temporary config file with the correct port
cat > src/config/llm-config.js << EOF
// LLM Backend Configuration - Auto-generated
export const LLM_CONFIG = {
  provider: 'mock',
  providers: {
    mock: {
      baseUrl: 'http://localhost:$BACKEND_PORT',
      endpoint: '/v1/chat/completions',
      wsEndpoint: '/ws',
      model: 'llama-base',
      headers: {
        'Content-Type': 'application/json'
      }
    }
  }
};

export const getCurrentConfig = () => {
  return LLM_CONFIG.providers[LLM_CONFIG.provider];
};
EOF

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing frontend dependencies..."
    npm install
fi

# Start the frontend
print_status "Starting frontend server on port $FRONTEND_PORT..."
export PORT=$FRONTEND_PORT
npm start &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

print_success "🚀 Application started successfully!"
print_success "Frontend: http://localhost:$FRONTEND_PORT"
print_success "Backend: http://localhost:$BACKEND_PORT"
print_status "Press Ctrl+C to stop both servers"

# Keep the script running
wait
