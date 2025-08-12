#!/bin/bash
# Setup script - moved from root directory
# This script was previously in the root directory

echo "Setup script - moved to scripts directory"
echo "Usage: Run from project root directory"

# Setup virtual environment and dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
