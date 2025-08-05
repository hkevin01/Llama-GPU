#!/bin/bash

# Add execution permission to the mock API server
chmod +x mock_api_server.py

# Install dependencies if not already installed
pip install fastapi uvicorn python-multipart

# Start the mock API server
uvicorn mock_api_server:app --reload --port 8000
