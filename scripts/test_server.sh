#!/bin/bash
# Test server script - moved from root directory
# This script was previously in the root directory

echo "Test server script - moved to scripts directory"
echo "Usage: Run from project root directory"

# Test the API server
echo "Testing API server..."
curl -X GET http://localhost:8000/health
