# AI Assistant Desktop App Guide 🖥️

## Overview

Native Ubuntu desktop application with system tray integration, chat window, and command execution.

## Features

- 🔔 System tray icon (always accessible)
- 💬 GTK3 chat interface
- ⚡ Quick actions menu
- 🔥 Beast Mode (autonomous)
- 🔧 Real command execution
- 🚀 Startup support
- 🎨 Beautiful UI with syntax highlighting

## Installation

```bash
cd /home/kevin/Projects/Llama-GPU
./install-desktop-app.sh
```

Or manually:
```bash
sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 gir1.2-notify-0.7
cp ai-assistant.desktop ~/.local/share/applications/
```

## Usage

### Launch
- Press `Super` key → type "AI Assistant"
- Or: `python3 tools/gui/ai_assistant_app.py`

### System Tray Menu
- 💬 Open Chat - Main window
- ⚡ Quick Actions - Predefined tasks
- ℹ️ About - App info
- ❌ Quit - Exit app

### Chat Window
1. Select model (phi4-mini or deepseek-r1)
2. Toggle Beast Mode for autonomous execution
3. Type message and press Enter
4. AI responds and executes commands

### Quick Actions
- System Info
- Disk Usage  
- Memory Status

## Command Execution

AI automatically finds and runs commands:

```
You: show disk space
AI: I'll check: $ df -h
[Output shown]
```

**Safe commands** run automatically.
**Risky commands** need confirmation (unless Beast Mode).

## Beast Mode 🔥

Toggle in top-right of chat window.

**OFF (default):**
- Asks before executing
- Safe mode

**ON (Beast Mode):**
- Autonomous execution
- Works until complete
- No confirmations

Use for: automation, batch tasks, multi-step workflows

## Models

### phi4-mini:3.8b (Default)
- Speed: ⚡⚡⚡
- Quality: ⭐⭐⭐
- Use: Quick tasks, fast responses

### deepseek-r1:7b
- Speed: ⚡⚡
- Quality: ⭐⭐⭐⭐
- Use: Complex reasoning

Switch in dropdown menu.

## Keyboard Shortcuts

- `Enter` - Send message
- `Ctrl+W` - Close window (hides to tray)
- `Ctrl+Q` - Quit app

## Startup

Add to startup applications:

```bash
cp ai-assistant.desktop ~/.config/autostart/
```

Or use GUI:
1. Open "Startup Applications"
2. Click "Add"
3. Browse to ai-assistant.desktop

## Troubleshooting

### App won't start
```bash
# Check Ollama
ollama serve

# Test dependencies
python3 -c "import gi; gi.require_version('Gtk', '3.0'); print('OK')"
```

### No system tray icon
```bash
# Install AppIndicator
sudo apt-get install gir1.2-appindicator3-0.1

# Check if running
ps aux | grep ai_assistant_app
```

### Commands not executing
- Check if Beast Mode is enabled
- Look for confirmation prompts in chat
- Verify SafeCommandExecutor is working

### Model not found
```bash
ollama list
ollama pull phi4-mini:3.8b
```

## Uninstall

```bash
rm ~/.local/share/applications/ai-assistant.desktop
rm ~/.config/autostart/ai-assistant.desktop  # if in startup
update-desktop-database ~/.local/share/applications
```

## Advanced

### Custom Icon
Replace in ai-assistant.desktop:
```
Icon=/path/to/your/icon.png
```

### Custom Quick Actions
Edit `create_menu()` in `ai_assistant_app.py`:
```python
action4 = Gtk.MenuItem(label="Custom Action")
action4.connect("activate", lambda x: self.quick_action("your command"))
quick_menu.append(action4)
```

### Keyboard Shortcuts
Add to `ChatWindow.__init__()`:
```python
self.connect("key-press-event", self.on_key_press)

def on_key_press(self, widget, event):
    if event.keyval == Gdk.KEY_Escape:
        self.hide()
```

## Related Docs

- [AI Agent Guide](./AI_AGENT_GUIDE.md) - CLI version
- [AI Agent Quickstart](./AI_AGENT_QUICKSTART.md) - Quick reference
- [Ollama Integration](./OLLAMA_INTEGRATION.md) - Backend details

## Support

Issues? Check:
1. Ollama is running: `ollama serve`
2. Dependencies installed: `./install-desktop-app.sh`
3. Desktop file exists: `ls ~/.local/share/applications/ai-assistant.desktop`
4. Logs: Run from terminal to see errors

---

**Tip**: Keep the app in system tray for instant AI access!
