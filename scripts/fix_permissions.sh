#!/bin/bash
# Fix permissions script - moved from root directory
# This script was previously in the root directory

echo "Fix permissions script - moved to scripts directory"
echo "Usage: Run from project root directory"

# Make scripts executable
chmod +x scripts/*.sh
chmod +x scripts/*.py

echo "Permissions fixed for scripts directory"
