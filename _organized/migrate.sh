#!/bin/bash
# Llama-GPU Project Migration Script
# Replaces the current project structure with the reorganized version

set -e  # Exit on any error

echo "🚀 Llama-GPU Project Reorganization Migration"
echo "============================================="

# Get current timestamp for backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/kevin/Projects/Llama-GPU-backup-${TIMESTAMP}"
ORGANIZED_DIR="/home/kevin/Projects/Llama-GPU/_organized"
TARGET_DIR="/home/kevin/Projects/Llama-GPU"

echo "📋 Pre-migration checks..."

# Check if organized structure exists
if [ ! -d "$ORGANIZED_DIR" ]; then
    echo "❌ Error: Organized structure not found at $ORGANIZED_DIR"
    exit 1
fi

# Check if target directory exists
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ Error: Target directory not found at $TARGET_DIR"
    exit 1
fi

echo "✅ Pre-checks passed"

echo "📦 Creating backup..."
mv "$TARGET_DIR" "$BACKUP_DIR"
echo "✅ Backup created at: $BACKUP_DIR"

echo "🔄 Moving reorganized structure..."
mv "$ORGANIZED_DIR" "$TARGET_DIR"
echo "✅ Structure migration complete"

echo "🔧 Setting up development environment..."
cd "$TARGET_DIR"

# Install Python package in development mode
echo "Installing Python package..."
pip install -e "core/[dev]" --quiet

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend/main-interface/
npm install --silent
cd ../..

echo "✅ Development environment setup complete"

echo "🧪 Running validation tests..."

# Test Python imports
echo "Testing Python package imports..."
cd core/
python -c "import sys; sys.path.insert(0, 'src'); import llama_gpu; print('✅ Core package imports successfully')" || {
    echo "❌ Python import test failed"
    exit 1
}

# Test frontend build
echo "Testing frontend build..."
cd ../frontend/main-interface/
npm run build --silent || {
    echo "❌ Frontend build test failed"
    exit 1
}
cd ../..

echo "🎉 Migration completed successfully!"
echo ""
echo "📁 New project structure:"
echo "  ├── core/                 # Python package"
echo "  ├── frontend/             # GUI applications"
echo "  ├── tools/                # Development tools"
echo "  ├── docs/                 # Documentation"
echo "  └── archive/              # Legacy files"
echo ""
echo "🔗 Quick links:"
echo "  • Main README: $TARGET_DIR/README.md"
echo "  • Python package: $TARGET_DIR/core/"
echo "  • GUI interface: $TARGET_DIR/frontend/main-interface/"
echo "  • Documentation: $TARGET_DIR/docs/"
echo ""
echo "📞 Next steps:"
echo "  1. Review the new structure"
echo "  2. Update your IDE/editor workspace"
echo "  3. Check $TARGET_DIR/POST_REORGANIZATION_ACTIONS.md for details"
echo ""
echo "🔄 Rollback: mv $BACKUP_DIR $TARGET_DIR"
