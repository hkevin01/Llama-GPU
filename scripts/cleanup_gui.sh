#!/bin/bash
# Remove redundant gui directory and update references to use llama-gui only

# Remove the redundant gui directory
rm -rf gui/

echo "Removed redundant gui directory. llama-gui is now the canonical GUI directory."
