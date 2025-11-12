#!/bin/bash
# Install AI Assistant as Ubuntu Desktop Application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_NAME="AI Assistant"
DESKTOP_FILE="ai-assistant.desktop"

echo "🤖 Installing $APP_NAME"
echo "================================"

# Check for required dependencies
echo "📦 Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

# Check GTK
if ! python3 -c "import gi; gi.require_version('Gtk', '3.0')" 2>/dev/null; then
    echo "❌ GTK3 not available. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
fi

# Check AppIndicator
if ! python3 -c "import gi; gi.require_version('AppIndicator3', '0.1')" 2>/dev/null; then
    echo "❌ AppIndicator3 not available. Installing..."
    sudo apt-get install -y gir1.2-appindicator3-0.1
fi

# Check Notify
if ! python3 -c "import gi; gi.require_version('Notify', '0.7')" 2>/dev/null; then
    echo "❌ Notify not available. Installing..."
    sudo apt-get install -y gir1.2-notify-0.7
fi

echo "✅ All dependencies satisfied"

# Install desktop file
echo "📋 Installing desktop entry..."
mkdir -p ~/.local/share/applications
cp "$SCRIPT_DIR/$DESKTOP_FILE" ~/.local/share/applications/
chmod +x ~/.local/share/applications/$DESKTOP_FILE

echo "✅ Desktop entry installed"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications
    echo "✅ Desktop database updated"
fi

# Optional: Add to autostart
read -p "🚀 Add to startup applications? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    mkdir -p ~/.config/autostart
    cp "$SCRIPT_DIR/$DESKTOP_FILE" ~/.config/autostart/
    echo "✅ Added to startup applications"
fi

echo ""
echo "================================"
echo "✅ Installation complete!"
echo ""
echo "You can now:"
echo "  1. Find '$APP_NAME' in your applications menu"
echo "  2. Launch from command line: $SCRIPT_DIR/tools/gui/ai_assistant_app.py"
echo "  3. Look for the system tray icon when running"
echo ""
echo "To start:"
echo "  - Press Super key and type 'AI Assistant'"
echo "  - Or run: python3 $SCRIPT_DIR/tools/gui/ai_assistant_app.py"
echo ""
