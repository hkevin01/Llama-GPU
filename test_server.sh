#!/bin/bash
echo "Testing API server startup..."
cd /home/kevin/Projects/Llama-GPU
python3 mock_api_server.py --port 8000 --host 0.0.0.0
