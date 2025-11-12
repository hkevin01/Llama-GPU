#!/bin/bash
# Uninstall Llama GPU Assistant Desktop Application

echo "🗑️  Uninstalling Llama GPU Assistant..."
echo ""

# Remove desktop entry
if [ -f "$HOME/.local/share/applications/llama-gpu-assistant.desktop" ]; then
    rm "$HOME/.local/share/applications/llama-gpu-assistant.desktop"
    echo "✅ Removed desktop entry"
else
    echo "⚠️  Desktop entry not found (already removed?)"
fi

# Remove icon
if [ -f "$HOME/.local/share/icons/llama-assistant.svg" ]; then
    rm "$HOME/.local/share/icons/llama-assistant.svg"
    echo "✅ Removed icon"
else
    echo "⚠️  Icon not found (already removed?)"
fi

# Update caches
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    echo "✅ Updated desktop database"
fi

if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons" 2>/dev/null || true
    echo "✅ Updated icon cache"
fi

echo ""
echo "✅ Uninstall complete!"
echo ""
echo "Note: Project files remain in their original location."
echo "The application can be reinstalled by running: scripts/install_desktop_app.sh"
echo ""
