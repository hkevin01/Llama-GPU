#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to find available port
find_available_port() {
    local port=$1
    while ss -tulpn | grep -q ":$port "; do
        ((port++))
    done
    echo $port
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    if [ ! -z "$API_PID" ]; then
        echo "Stopping API server..."
        kill $API_PID 2>/dev/null
        wait $API_PID 2>/dev/null
    fi
    echo -e "${GREEN}✨ Cleanup complete${NC}"
    exit 0
}

# Set up cleanup trap
trap cleanup EXIT INT TERM

# Find available ports
API_PORT=$(find_available_port 8000)
GUI_PORT=$(find_available_port 3001)

echo -e "${BLUE}🚀 Starting Llama-GPU Development Environment${NC}"
echo -e "${GREEN}✅ Using port $API_PORT for API server${NC}"
echo -e "${GREEN}✅ Using port $GUI_PORT for GUI${NC}"

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies if needed
if [ ! -f "venv/.dependencies_installed" ]; then
    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
    pip install fastapi uvicorn websockets python-multipart requests
    touch venv/.dependencies_installed
fi

# Start API server in background
echo -e "${YELLOW}🌟 Starting API server on port $API_PORT...${NC}"
cd "$(dirname "$0")/.."
python mock_api_server.py --port $API_PORT --host 0.0.0.0 &
API_PID=$!

# Wait a moment for server to start
sleep 3

# Check if API server started successfully
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start API server${NC}"
    exit 1
fi

# Test API server connection
echo -e "${YELLOW}🔍 Testing API server connection...${NC}"
if python test_connection.py 2>/dev/null; then
    echo -e "${GREEN}✅ API server is responding correctly${NC}"
else
    echo -e "${YELLOW}⚠️  API connection test failed, but continuing...${NC}"
fi

# Update GUI configuration with the correct API port
CONFIG_FILE="llama-gui/src/config/llm-config.js"
if [ -f "$CONFIG_FILE" ]; then
    # Create backup
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup"
    # Update the port in the configuration
    sed -i "s/localhost:[0-9]*/localhost:$API_PORT/g" "$CONFIG_FILE"
    echo -e "${GREEN}✅ Updated frontend configuration${NC}"
fi

echo -e "${GREEN}✅ API server started successfully${NC}"
echo -e "${BLUE}🌐 API server: http://localhost:$API_PORT${NC}"
echo -e "${BLUE}📊 GUI will be available at: http://localhost:$GUI_PORT${NC}"
echo -e "${BLUE}🔌 WebSocket endpoint: ws://localhost:$API_PORT/v1/stream${NC}"

# Start GUI
echo -e "${YELLOW}🌟 Starting React development server on port $GUI_PORT...${NC}"
cd llama-gui
PORT=$GUI_PORT npm run start:react

# If we reach here, the GUI has stopped
echo -e "${YELLOW}⏹️  GUI server stopped${NC}"
