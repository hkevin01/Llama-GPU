#!/bin/bash
# Install Llama GPU Assistant as a Desktop Application
# This script installs the .desktop file and icon to make the app appear in the applications menu

set -e  # Exit on error

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Installing Llama GPU Assistant..."
echo ""

# Step 1: Ensure launcher is executable
echo "📝 Step 1: Making launcher executable..."
chmod +x "$PROJECT_ROOT/bin/llama-assistant"
echo "   ✅ Launcher is executable"
echo ""

# Step 2: Create local applications directory
echo "📁 Step 2: Creating applications directory..."
mkdir -p "$HOME/.local/share/applications"
mkdir -p "$HOME/.local/share/icons"
echo "   ✅ Directories created"
echo ""

# Step 3: Copy icon
echo "🎨 Step 3: Installing icon..."
cp "$PROJECT_ROOT/share/icons/llama-assistant.svg" "$HOME/.local/share/icons/"
echo "   ✅ Icon installed to ~/.local/share/icons/"
echo ""

# Step 4: Install desktop file
echo "🖥️  Step 4: Installing desktop entry..."
cp "$PROJECT_ROOT/ai-assistant.desktop" "$HOME/.local/share/applications/llama-gpu-assistant.desktop"

# Update paths in the installed desktop file to use absolute paths
sed -i "s|/home/kevin/Projects/Llama-GPU|$PROJECT_ROOT|g" "$HOME/.local/share/applications/llama-gpu-assistant.desktop"
sed -i "s|Icon=.*|Icon=$HOME/.local/share/icons/llama-assistant.svg|g" "$HOME/.local/share/applications/llama-gpu-assistant.desktop"
sed -i "s|Exec=.*|Exec=$PROJECT_ROOT/bin/llama-assistant|g" "$HOME/.local/share/applications/llama-gpu-assistant.desktop"

echo "   ✅ Desktop entry installed to ~/.local/share/applications/"
echo ""

# Step 5: Update desktop database
echo "🔄 Step 5: Updating desktop database..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo "   ✅ Desktop database updated"
else
    echo "   ⚠️  update-desktop-database not found (optional)"
fi
echo ""

# Step 6: Update icon cache
echo "🎨 Step 6: Updating icon cache..."
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons" 2>/dev/null || true
    echo "   ✅ Icon cache updated"
else
    echo "   ⚠️  gtk-update-icon-cache not found (optional)"
fi
echo ""

echo "✅ Installation complete!"
echo ""
echo "🎉 Llama GPU Assistant is now installed!"
echo ""
echo "You can now:"
echo "  1. Press Super key (Windows key) and search for 'Llama GPU Assistant'"
echo "  2. Find it in your applications menu under Utilities or Development"
echo "  3. Right-click and add to favorites for quick access"
echo ""
echo "📍 Installed files:"
echo "   • Launcher: $PROJECT_ROOT/bin/llama-assistant"
echo "   • Desktop: ~/.local/share/applications/llama-gpu-assistant.desktop"
echo "   • Icon: ~/.local/share/icons/llama-assistant.svg"
echo ""
echo "To uninstall, run: $PROJECT_ROOT/scripts/uninstall_desktop_app.sh"
echo ""
