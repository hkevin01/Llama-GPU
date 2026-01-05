#!/bin/bash
# Setup Knowledge Base for Llama-GPU
# Initializes RAG system and populates with software engineering knowledge

set -e

echo "========================================="
echo "Llama-GPU Knowledge Base Setup"
echo "========================================="
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Initializing Knowledge Base"
echo "========================================="
echo ""

# Run knowledge base setup
cd src/knowledge_base

echo "Populating knowledge base with software engineering knowledge..."
echo "This will create a local vector database with:"
echo "  - Python programming knowledge"
echo "  - AI/ML concepts and frameworks"
echo "  - Computer Science fundamentals"
echo "  - SDLC and DevOps practices"
echo "  - Ubuntu/Linux system administration"
echo ""

python3 knowledge_populator.py

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "The knowledge base has been initialized at:"
echo "  ~/.llama-gpu/vectordb/"
echo ""
echo "You can now use the RAG-enhanced LLM:"
echo "  python3 src/knowledge_base/rag_llm_interface.py"
echo ""
echo "Or use the AI agent with knowledge enhancement:"
echo "  python3 tools/ai_agent.py"
echo ""
