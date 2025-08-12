#!/bin/bash
# Show structure script - moved from root directory
# This script was previously in the root directory

echo "Show structure script - moved to scripts directory"
echo "Usage: Run from project root directory"

# Display project structure
tree -I 'venv|__pycache__|*.pyc|.git|node_modules' .
