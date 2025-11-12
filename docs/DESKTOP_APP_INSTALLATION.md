# Desktop Application Installation Guide

This guide explains how to install Llama GPU Assistant as a native desktop application that appears in your applications menu.

## Quick Start

```bash
# From the project root directory
./scripts/install_desktop_app.sh
```

That's it! The app will now appear in your applications menu.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Uninstallation](#uninstallation)
- [Troubleshooting](#troubleshooting)
- [Technical Details](#technical-details)

---

## Overview

### What Gets Installed

The installation script creates three key components:

1. **Launcher Script** (`bin/llama-assistant`)
   - Bash script that handles environment setup
   - Activates virtual environment if available
   - Sets proper Python paths
   - Launches the GUI application

2. **Desktop Entry** (`~/.local/share/applications/llama-gpu-assistant.desktop`)
   - Standard FreeDesktop.org desktop file
   - Makes the app appear in your applications menu
   - Defines app name, icon, categories, and launch command

3. **Application Icon** (`~/.local/share/icons/llama-assistant.svg`)
   - Custom SVG icon showing GPU chip with AI brain
   - Used in application menu and window decorations

### Where to Find the App

After installation, you can find the app in:

- **GNOME**: Press `Super` (Windows key), type "Llama GPU"
- **Application Menu**: Under "Utilities" or "Development" categories
- **Favorites**: Right-click the app and "Add to Favorites" for quick access

---

## Installation

### Prerequisites

Before installing, ensure you have:

1. **Python 3.8+** installed
2. **GTK 3** and dependencies:
   ```bash
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
                    gir1.2-appindicator3-0.1 gir1.2-notify-0.7
   ```

3. **Ollama** installed and running:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama serve  # Start in background
   ollama pull phi4:3.8b  # Download the model
   ```

4. **Project Dependencies**:
   ```bash
   # Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install requirements
   pip install -r requirements.txt
   ```

### Step-by-Step Installation

1. **Navigate to Project Root**:
   ```bash
   cd /path/to/Llama-GPU
   ```

2. **Run Installation Script**:
   ```bash
   ./scripts/install_desktop_app.sh
   ```

3. **Verify Installation**:
   ```bash
   # Check desktop file
   cat ~/.local/share/applications/llama-gpu-assistant.desktop
   
   # Check icon
   ls -l ~/.local/share/icons/llama-assistant.svg
   
   # Test launcher directly
   ./bin/llama-assistant
   ```

### What Happens During Installation

```
🚀 Installing Llama GPU Assistant...

📝 Step 1: Making launcher executable...
   ✅ Launcher is executable

📁 Step 2: Creating applications directory...
   ✅ Directories created

🎨 Step 3: Installing icon...
   ✅ Icon installed to ~/.local/share/icons/

🖥️  Step 4: Installing desktop entry...
   ✅ Desktop entry installed to ~/.local/share/applications/

🔄 Step 5: Updating desktop database...
   ✅ Desktop database updated

🎨 Step 6: Updating icon cache...
   ✅ Icon cache updated

✅ Installation complete!
```

---

## Usage

### Launching the Application

**Method 1: Application Menu**
1. Press `Super` key (Windows key)
2. Type "Llama GPU Assistant"
3. Click the application icon

**Method 2: Command Line**
```bash
# Using the launcher
./bin/llama-assistant

# Or directly with Python
python3 tools/gui/ai_assistant_app.py
```

**Method 3: Desktop File**
```bash
# Execute the desktop file
gtk-launch llama-gpu-assistant
```

### First Run

On first launch, the application will:

1. **Check Ollama Connection**
   - Verifies Ollama is running on `http://localhost:11434`
   - Shows connection status in the UI

2. **Load Model**
   - Uses `phi4:3.8b` by default
   - You can change models in the settings

3. **Display System Tray Icon**
   - Look for the icon in your system tray
   - Click to show/hide the chat window

### Application Features

**Chat Window**
- AI-powered conversations with Phi4-Mini
- Command execution suggestions
- Real-time streaming responses
- Message history

**System Tray Integration**
- Persistent background presence
- Quick access from tray icon
- Minimize to tray on close

**Command Execution**
- Safe command validator
- Sudo command support (with password prompt)
- Real-time command output
- Confirmation prompts for dangerous operations

**Beast Mode**
- Toggle autonomous operation
- Executes commands without confirmation
- Use with caution!

---

## Uninstallation

### Remove Desktop App

```bash
./scripts/uninstall_desktop_app.sh
```

This will:
- Remove desktop entry from applications menu
- Remove application icon
- Update desktop database and icon cache
- Keep project files intact

### Complete Removal

To completely remove the project:

```bash
# Uninstall desktop app first
./scripts/uninstall_desktop_app.sh

# Then remove project directory
cd ..
rm -rf Llama-GPU
```

---

## Troubleshooting

### App Doesn't Appear in Menu

**Solution 1: Update Desktop Database**
```bash
update-desktop-database ~/.local/share/applications
```

**Solution 2: Log Out and Back In**
Some desktop environments cache the applications list. Logging out and back in refreshes the cache.

**Solution 3: Check Desktop File**
```bash
# Verify desktop file exists and is valid
desktop-file-validate ~/.local/share/applications/llama-gpu-assistant.desktop
```

### Icon Not Showing

**Solution 1: Update Icon Cache**
```bash
gtk-update-icon-cache -f -t ~/.local/share/icons
```

**Solution 2: Use Full Path**
Edit the desktop file to use absolute path:
```bash
nano ~/.local/share/applications/llama-gpu-assistant.desktop
# Change Icon line to full path:
Icon=/home/yourusername/.local/share/icons/llama-assistant.svg
```

### App Won't Launch

**Solution 1: Check Permissions**
```bash
chmod +x ./bin/llama-assistant
chmod +x ./tools/gui/ai_assistant_app.py
```

**Solution 2: Test Launcher Manually**
```bash
./bin/llama-assistant
# Check for error messages
```

**Solution 3: Check Dependencies**
```bash
# Activate virtual environment
source venv/bin/activate

# Test imports
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk"
```

### Ollama Connection Failed

**Solution 1: Start Ollama**
```bash
ollama serve
```

**Solution 2: Check Ollama Status**
```bash
curl http://localhost:11434/api/tags
```

**Solution 3: Verify Model**
```bash
ollama list
# If phi4:3.8b not listed:
ollama pull phi4:3.8b
```

### Command Execution Not Working

**Solution 1: Check Sudo Configuration**
```bash
# Test sudo works
sudo -v
```

**Solution 2: Verify pexpect**
```bash
source venv/bin/activate
pip install pexpect
```

**Solution 3: Check Logs**
Look for error messages in the terminal if launched from command line.

---

## Technical Details

### Directory Structure

```
Llama-GPU/
├── bin/
│   └── llama-assistant              # Launcher script
├── share/
│   └── icons/
│       └── llama-assistant.svg      # Application icon (128x128)
├── scripts/
│   ├── install_desktop_app.sh       # Installation script
│   └── uninstall_desktop_app.sh     # Uninstallation script
├── tools/
│   └── gui/
│       └── ai_assistant_app.py      # Main GUI application
└── ai-assistant.desktop             # Desktop entry template
```

### Desktop Entry Specification

The `.desktop` file follows the [FreeDesktop.org Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html):

```ini
[Desktop Entry]
Version=1.0                          # Desktop entry spec version
Type=Application                     # Entry type
Name=Llama GPU Assistant             # Application name (shown in menu)
GenericName=AI Assistant             # Generic category name
Comment=GPU-Accelerated AI...        # Description (tooltip)
Exec=/path/to/bin/llama-assistant    # Command to execute
Icon=/path/to/icon.svg               # Icon path
Terminal=false                       # Don't open terminal
Categories=Utility;Development;      # Menu categories
Keywords=ai;assistant;...            # Search keywords
StartupNotify=true                   # Show startup notification
StartupWMClass=ai_assistant_app      # Window class for matching
```

### Icon Design

The application icon (`llama-assistant.svg`) features:

- **128x128 pixels** SVG format (scales to any size)
- **Purple gradient background** (#667eea) - Represents AI/neural networks
- **GPU chip design** - Black chip with circuit lines
- **AI brain symbol** - Pink wavy lines representing neural activity
- **Green center core** - Active processing indicator
- **Lightning bolts** - GPU acceleration/speed

Design rationale:
- GPU chip symbolizes hardware acceleration
- Brain/neural patterns represent AI intelligence
- Lightning bolts convey speed and power
- Colors match the project's brand (purple, pink, green)

### Launcher Script

The `bin/llama-assistant` launcher handles:

1. **Path Resolution**
   ```bash
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
   ```

2. **Virtual Environment Activation**
   ```bash
   if [ -d "$PROJECT_ROOT/venv" ]; then
       source "$PROJECT_ROOT/venv/bin/activate"
   fi
   ```

3. **Python Path Setup**
   ```bash
   export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
   ```

4. **Application Launch**
   ```bash
   exec python3 "$PROJECT_ROOT/tools/gui/ai_assistant_app.py" "$@"
   ```

### Installation Locations

**User-Level Installation** (default):
- Desktop file: `~/.local/share/applications/`
- Icon: `~/.local/share/icons/`
- No root privileges required
- Only visible to current user

**System-Wide Installation** (optional):
- Desktop file: `/usr/share/applications/`
- Icon: `/usr/share/icons/hicolor/scalable/apps/`
- Requires root privileges
- Visible to all users

### Platform Compatibility

**Tested Desktop Environments:**
- ✅ GNOME (Ubuntu 22.04+)
- ✅ Unity (Ubuntu 20.04)
- ✅ KDE Plasma
- ✅ XFCE
- ✅ Cinnamon

**Requirements:**
- GTK 3.0+
- AppIndicator 3
- FreeDesktop.org standards compliance

---

## Advanced Configuration

### Custom Launch Options

Edit the desktop file to add command-line options:

```bash
nano ~/.local/share/applications/llama-gpu-assistant.desktop

# Add options to Exec line:
Exec=/path/to/bin/llama-assistant --beast-mode
Exec=/path/to/bin/llama-assistant --model llama2:7b
```

### Multiple Desktop Entries

Create variations for different use cases:

```bash
# Copy desktop file
cp ~/.local/share/applications/llama-gpu-assistant.desktop \
   ~/.local/share/applications/llama-gpu-assistant-beast.desktop

# Edit for Beast Mode
nano ~/.local/share/applications/llama-gpu-assistant-beast.desktop
# Change Name and Exec:
Name=Llama GPU Assistant (Beast Mode)
Exec=/path/to/bin/llama-assistant --beast-mode
Icon=...
```

### Custom Icons

Replace the default icon:

```bash
# Use your own icon (PNG or SVG)
cp /path/to/your-icon.svg ~/.local/share/icons/llama-assistant.svg

# Update icon cache
gtk-update-icon-cache -f -t ~/.local/share/icons
```

### Keyboard Shortcuts

Add a global keyboard shortcut:

**GNOME:**
1. Settings → Keyboard → Custom Shortcuts
2. Add New Shortcut:
   - Name: "Llama GPU Assistant"
   - Command: `/path/to/bin/llama-assistant`
   - Shortcut: `Ctrl+Alt+L` (or your preference)

**KDE Plasma:**
1. System Settings → Shortcuts → Custom Shortcuts
2. Right-click → New → Global Shortcut → Command/URL
3. Set trigger key and command

---

## Contributing

### Improving the Desktop Integration

Contributions welcome! Areas for improvement:

1. **Icon Themes**
   - Create themed variants (light/dark)
   - Add different icon sizes
   - Support icon themes

2. **Desktop Actions**
   - Add quick actions to desktop entry
   - Right-click menu items
   - Example: "New Chat", "Beast Mode", "Settings"

3. **DBus Integration**
   - Single instance control
   - IPC for external control
   - System notifications

4. **Autostart**
   - Option to launch on login
   - System tray startup

### Desktop Entry Actions

Add context menu actions:

```ini
[Desktop Entry]
...
Actions=NewChat;BeastMode;Settings;

[Desktop Action NewChat]
Name=New Chat
Exec=/path/to/bin/llama-assistant --new-chat

[Desktop Action BeastMode]
Name=Beast Mode
Exec=/path/to/bin/llama-assistant --beast-mode

[Desktop Action Settings]
Name=Settings
Exec=/path/to/bin/llama-assistant --settings
```

---

## See Also

- [README.md](../README.md) - Main project documentation
- [GUI_SETUP_GUIDE.md](GUI-SETUP-COMPLETE.md) - GUI development details
- [INSTALLATION_GUIDE.md](installation_guide.md) - Installation prerequisites
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines

---

## License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

## Support

**Issues?** Open an issue on GitHub: [hkevin01/Llama-GPU](https://github.com/hkevin01/Llama-GPU/issues)

**Questions?** Start a discussion: [GitHub Discussions](https://github.com/hkevin01/Llama-GPU/discussions)

---

**Last Updated**: November 12, 2025
**Version**: 1.0.0
