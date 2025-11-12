#!/bin/bash
# Project Organization Script
# Moves files to appropriate subdirectories to keep root clean

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🧹 Starting Project Organization..."
echo ""

# Create backup
echo "📦 Creating backup..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo "   ✅ Backup directory: $BACKUP_DIR"
echo ""

# ========================================
# 1. Move Documentation Files
# ========================================
echo "📚 Step 1: Organizing documentation files..."

# Move AI-related docs to docs/ai/
mkdir -p docs/ai
for file in AI_README.md AI_UPGRADE_MANIFEST.md AI_UPGRADE_STATUS.md AI_UPGRADE_TODO.md; do
    if [ -f "$file" ]; then
        echo "   • $file → docs/ai/"
        mv "$file" docs/ai/
    fi
done

# Move desktop app docs to docs/desktop-app/
mkdir -p docs/desktop-app
for file in DESKTOP_APP_CHECKLIST.md DESKTOP_APP_SETUP_COMPLETE.md LAUNCH_APP.md; do
    if [ -f "$file" ]; then
        echo "   • $file → docs/desktop-app/"
        mv "$file" docs/desktop-app/
    fi
done

# Move feature/implementation docs to docs/features/
mkdir -p docs/features
for file in IMPLEMENTATION_COMPLETE.md INTEGRATION_TODO.md NEW_FEATURES.md SUDO_IMPLEMENTATION_COMPLETE.md SUDO_TODO_CHECKLIST.md; do
    if [ -f "$file" ]; then
        echo "   • $file → docs/features/"
        mv "$file" docs/features/
    fi
done

echo "   ✅ Documentation organized"
echo ""

# ========================================
# 2. Move Test Files
# ========================================
echo "🧪 Step 2: Organizing test files..."

mkdir -p tests/manual
for file in test_history.py test_sudo.py; do
    if [ -f "$file" ]; then
        echo "   • $file → tests/manual/"
        mv "$file" tests/manual/
    fi
done

echo "   ✅ Test files organized"
echo ""

# ========================================
# 3. Move Docker Files
# ========================================
echo "🐳 Step 3: Organizing Docker files..."

mkdir -p docker
for file in Dockerfile docker-compose.yml; do
    if [ -f "$file" ]; then
        echo "   • $file → docker/"
        mv "$file" docker/
    fi
done

echo "   ✅ Docker files organized"
echo ""

# ========================================
# 4. Move Desktop Entry Files
# ========================================
echo "🖥️  Step 4: Organizing desktop entry files..."

mkdir -p share/applications
for file in ai-assistant.desktop install-desktop-app.sh; do
    if [ -f "$file" ]; then
        if [ "$file" = "install-desktop-app.sh" ]; then
            # This is a duplicate of scripts/install_desktop_app.sh
            if [ -f "scripts/install_desktop_app.sh" ]; then
                echo "   • Removing duplicate: $file"
                rm "$file"
            else
                echo "   • $file → scripts/"
                mv "$file" scripts/
            fi
        else
            echo "   • $file → share/applications/"
            mv "$file" share/applications/
        fi
    fi
done

echo "   ✅ Desktop files organized"
echo ""

# ========================================
# 5. Organize Config Files (keep in root)
# ========================================
echo "⚙️  Step 5: Verifying config files..."

# These should stay in root
CONFIG_FILES=(.editorconfig .env.example .gitignore .pre-commit-config.yaml .prettierrc)
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file (keeping in root)"
    fi
done

echo "   ✅ Config files verified"
echo ""

# ========================================
# 6. Update Desktop File Path Reference
# ========================================
echo "🔧 Step 6: Updating desktop file references..."

# Update installation script to use new path
if [ -f "scripts/install_desktop_app.sh" ]; then
    sed -i 's|"$PROJECT_ROOT/ai-assistant.desktop"|"$PROJECT_ROOT/share/applications/ai-assistant.desktop"|g' scripts/install_desktop_app.sh
    echo "   ✅ Updated install_desktop_app.sh"
fi

echo ""

# ========================================
# 7. Create README in each major directory
# ========================================
echo "📝 Step 7: Creating directory READMEs..."

# docs/ai/README.md
cat > docs/ai/README.md << 'DOCEND'
# AI Enhancement Documentation

This directory contains documentation related to AI features, upgrades, and improvements.

## Files

- `AI_README.md` - AI feature overview
- `AI_UPGRADE_MANIFEST.md` - Upgrade tracking manifest
- `AI_UPGRADE_STATUS.md` - Current upgrade status
- `AI_UPGRADE_TODO.md` - Remaining AI tasks

## Related Documentation

- Main: [../../README.md](../../README.md)
- Desktop App: [../desktop-app/](../desktop-app/)
- Features: [../features/](../features/)
DOCEND

# docs/desktop-app/README.md
cat > docs/desktop-app/README.md << 'DOCEND'
# Desktop Application Documentation

This directory contains all documentation related to the desktop application installation and usage.

## Files

- `DESKTOP_APP_CHECKLIST.md` - Installation verification checklist
- `DESKTOP_APP_SETUP_COMPLETE.md` - Installation summary
- `LAUNCH_APP.md` - Quick start guide

## Full Guide

See [DESKTOP_APP_INSTALLATION.md](../DESKTOP_APP_INSTALLATION.md) for complete documentation.

## Quick Start

```bash
# Install
./scripts/install_desktop_app.sh

# Launch
Super Key → "Llama GPU" → Click
```
DOCEND

# docs/features/README.md
cat > docs/features/README.md << 'DOCEND'
# Feature Implementation Documentation

This directory contains documentation about implemented features and ongoing development tasks.

## Files

- `IMPLEMENTATION_COMPLETE.md` - Completed implementations
- `INTEGRATION_TODO.md` - Integration tasks
- `NEW_FEATURES.md` - New feature descriptions
- `SUDO_IMPLEMENTATION_COMPLETE.md` - Sudo execution feature
- `SUDO_TODO_CHECKLIST.md` - Sudo feature checklist

## Related

- Main documentation: [../../README.md](../../README.md)
- Development guide: [../DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md)
DOCEND

# tests/manual/README.md
cat > tests/manual/README.md << 'DOCEND'
# Manual Test Scripts

This directory contains manual test scripts for specific features.

## Files

- `test_history.py` - Test conversation history persistence
- `test_sudo.py` - Test sudo command execution

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run a test
python tests/manual/test_history.py
python tests/manual/test_sudo.py
```

## Automated Tests

See [../](../) for automated test suite.
DOCEND

# docker/README.md
cat > docker/README.md << 'DOCEND'
# Docker Configuration

This directory contains Docker-related files for containerized deployment.

## Files

- `Dockerfile` - Container image definition
- `docker-compose.yml` - Multi-container orchestration

## Usage

```bash
# Build image
docker build -t llama-gpu -f docker/Dockerfile .

# Run with docker-compose
docker-compose -f docker/docker-compose.yml up
```

## Requirements

- Docker 20.10+
- Docker Compose 2.0+
- NVIDIA Docker (for GPU support)

## GPU Support

For GPU acceleration in containers:
```bash
docker run --gpus all llama-gpu
```
DOCEND

echo "   ✅ Directory READMEs created"
echo ""

# ========================================
# 8. Update Root README with new structure
# ========================================
echo "📖 Step 8: Updating root README..."

# Create a backup of README
cp README.md "$BACKUP_DIR/README.md.backup"

# Add a note about new organization (we'll just append it)
cat >> README.md << 'READMEEND'

---

## 📁 Project Structure

```
Llama-GPU/
├── bin/                    # Executable scripts and launchers
├── config/                 # Configuration files
├── docs/                   # Documentation
│   ├── ai/                # AI feature documentation
│   ├── desktop-app/       # Desktop app guides
│   └── features/          # Feature implementation docs
├── docker/                 # Docker configuration
├── examples/              # Usage examples
├── scripts/               # Utility scripts
├── share/                 # Shared resources
│   ├── applications/      # Desktop entries
│   └── icons/             # Application icons
├── src/                   # Source code
├── tests/                 # Test suite
│   └── manual/           # Manual test scripts
├── tools/                 # Development tools
│   ├── execution/        # Command execution
│   └── gui/              # GUI applications
└── utils/                # Utility modules

Core files (kept in root):
├── README.md              # Main documentation
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project metadata
└── LICENSE               # License information
```

### Directory Purposes

| Directory | Purpose |
|-----------|---------|
| `bin/` | Executable launchers and entry points |
| `config/` | Configuration files and settings |
| `docs/` | All documentation organized by topic |
| `docker/` | Container images and orchestration |
| `scripts/` | Automation and utility scripts |
| `share/` | Shared resources (icons, desktop files) |
| `src/` | Main source code |
| `tests/` | Automated and manual tests |
| `tools/` | Development and debugging tools |

READMEEND

echo "   ✅ README updated with structure"
echo ""

# ========================================
# 9. Summary
# ========================================
echo "✅ Organization Complete!"
echo ""
echo "📊 Summary:"
echo "   • Documentation moved to docs/ subdirectories"
echo "   • Test files moved to tests/manual/"
echo "   • Docker files moved to docker/"
echo "   • Desktop files organized in share/"
echo "   • Root directory cleaned"
echo "   • Directory READMEs created"
echo "   • Backup created in: $BACKUP_DIR"
echo ""
echo "📂 New Structure:"
echo "   Root files:     $(find . -maxdepth 1 -type f ! -name '.*' | wc -l)"
echo "   Config files:   $(find . -maxdepth 1 -name '.*' -type f | wc -l)"
echo "   Directories:    $(find . -maxdepth 1 -type d ! -name '.*' ! -name '.' | wc -l)"
echo ""
echo "🔍 Root files remaining:"
find . -maxdepth 1 -type f ! -name '.*' -exec basename {} \; | sort
echo ""
echo "✨ Project is now organized!"
