# Desktop App Troubleshooting 🔧

## Common Issues and Solutions

### 1. ValueError: unknown text tag

**Error:**
```
ValueError: unknown text tag: you
```

**Cause:** Tag name mismatch in GTK TextBuffer

**Solution:** Fixed in latest version. Update with:
```bash
cd /home/kevin/Projects/Llama-GPU
git pull  # or just use latest ai_assistant_app.py
```

### 2. App Won't Start

**Error:** Nothing happens when launching

**Check:**
```bash
# Test dependencies
python3 -c "import gi; gi.require_version('Gtk', '3.0'); print('GTK OK')"
python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); print('Indicator OK')"
python3 -c "import gi; gi.require_version('Notify', '0.7'); print('Notify OK')"
```

**Install missing:**
```bash
sudo apt-get install python3-gi gir1.2-gtk-3.0 gir1.2-appindicator3-0.1 gir1.2-notify-0.7
```

### 3. No System Tray Icon

**Issue:** App runs but no icon visible

**Solutions:**
- Check if system tray is enabled in your desktop environment
- For GNOME: Install TopIcons Plus extension
- For Ubuntu: Tray should work by default
- Check if app is running: `ps aux | grep ai_assistant_app`

**Alternative:** Use floating button version:
```bash
python3 tools/gui/floating_llm_button.py
```

### 4. Ollama Not Available

**Error:** "Ollama service not available"

**Solution:**
```bash
# Start Ollama
ollama serve

# Or check if running
ps aux | grep ollama

# Verify connection
curl http://localhost:11434
```

### 5. Model Not Found

**Error:** Model errors in chat

**Solution:**
```bash
# List installed models
ollama list

# Install phi4-mini
ollama pull phi4-mini:3.8b

# Install deepseek-r1
ollama pull deepseek-r1:7b
```

### 6. Commands Not Executing

**Issue:** AI responds but doesn't run commands

**Check:**
1. Beast Mode is enabled? (checkbox in top-right)
2. Commands are formatted correctly? (with `$` prefix)
3. SafeCommandExecutor is available?

**Test:**
```bash
python3 -c "from tools.execution.command_executor import SafeCommandExecutor; print('OK')"
```

### 7. Chat Window Freezes

**Issue:** UI becomes unresponsive

**Cause:** Long-running command or AI response

**Solution:**
- Wait for completion (there's a timeout)
- Close window (hides to tray) and reopen
- Kill and restart: `pkill -f ai_assistant_app`

### 8. GTK Warnings

**Warning:**
```
Gtk-WARNING **: Unknown key enable-thumbnails in settings.ini
```

**Impact:** Cosmetic only, app works fine

**Fix (optional):**
```bash
# Remove invalid key from GTK settings
sed -i '/enable-thumbnails/d' ~/.config/gtk-3.0/settings.ini
```

### 9. Desktop Entry Not Showing

**Issue:** Can't find "AI Assistant" in app menu

**Solution:**
```bash
# Install properly
./install-desktop-app.sh

# Or manually
cp ai-assistant.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/ai-assistant.desktop
update-desktop-database ~/.local/share/applications

# Refresh GNOME shell (if using GNOME)
# Press Alt+F2, type 'r', press Enter
```

### 10. Permission Denied

**Error:** Can't execute files

**Solution:**
```bash
# Make executables
chmod +x tools/gui/ai_assistant_app.py
chmod +x tools/ai_agent.py
chmod +x install-desktop-app.sh
```

## Debug Mode

Run with debug output:
```bash
cd /home/kevin/Projects/Llama-GPU
python3 tools/gui/ai_assistant_app.py 2>&1 | tee ai_app_debug.log
```

Check logs:
```bash
tail -f ai_app_debug.log
```

## Testing Checklist

```bash
# 1. Python version
python3 --version  # Should be 3.8+

# 2. GTK3
python3 -c "import gi; gi.require_version('Gtk', '3.0'); print('OK')"

# 3. AppIndicator
python3 -c "import gi; gi.require_version('AppIndicator3', '0.1'); print('OK')"

# 4. Ollama
curl http://localhost:11434

# 5. Models
ollama list

# 6. Command executor
python3 -c "from tools.execution.command_executor import SafeCommandExecutor; print('OK')"

# 7. Ollama client
python3 -c "from src.backends.ollama import OllamaClient; print('OK')"

# 8. Syntax
python3 -m py_compile tools/gui/ai_assistant_app.py
```

## Common GTK3 Issues

### Theme Issues
```bash
# Reset GTK theme
gsettings reset org.gnome.desktop.interface gtk-theme

# Or set explicitly
gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita'
```

### Icon Issues
```bash
# Update icon cache
sudo gtk-update-icon-cache /usr/share/icons/hicolor/
```

### Font Issues
```bash
# Check font rendering
gsettings get org.gnome.desktop.interface font-name
```

## Performance Issues

### High CPU Usage
- Switch to smaller model (phi4-mini)
- Close unused browser tabs
- Check for runaway processes: `top`

### High Memory Usage
```bash
# Check memory
free -h

# If low, close other apps or use smaller model
```

### Slow Responses
- Use phi4-mini (faster than deepseek-r1)
- Check network: `ping google.com`
- Restart Ollama: `pkill ollama && ollama serve`

## Getting Help

1. **Check logs:** Run app from terminal
2. **Test components:** Use testing checklist above
3. **Read docs:** See DESKTOP_APP_GUIDE.md
4. **Try CLI:** Use `tools/ai` as fallback
5. **Reinstall:** Run `./install-desktop-app.sh` again

## Quick Fixes

### Full Reset
```bash
# Stop app
pkill -f ai_assistant_app

# Remove desktop file
rm ~/.local/share/applications/ai-assistant.desktop

# Reinstall
./install-desktop-app.sh

# Restart
python3 tools/gui/ai_assistant_app.py
```

### Clean Start
```bash
# Clear any caches
rm -rf ~/.cache/ai-assistant/

# Reset Ollama (careful!)
# ollama rm phi4-mini:3.8b
# ollama pull phi4-mini:3.8b
```

## Known Limitations

1. **Requires Ollama running** - App won't work without it
2. **GTK3 only** - No GTK4 support yet
3. **Linux only** - Ubuntu/Debian tested
4. **System tray** - May not work on all desktop environments
5. **Memory** - Needs ~4GB RAM for models

## Alternatives

If desktop app doesn't work:

### 1. Use CLI
```bash
tools/ai "your task"
```

### 2. Use Floating Button
```bash
python3 tools/gui/floating_llm_button.py
```

### 3. Use Terminal Only
```bash
tools/llm_cli.py -i
```

### 4. Use Open WebUI
```bash
# If installed
xdg-open http://localhost:8080
```

## Report Issues

If none of these solutions work:

1. Gather information:
   ```bash
   python3 --version
   uname -a
   echo $DESKTOP_SESSION
   ollama --version
   ```

2. Run debug:
   ```bash
   python3 tools/gui/ai_assistant_app.py 2>&1 | tee issue.log
   ```

3. Include in report:
   - Error messages
   - Debug log
   - System info
   - Steps to reproduce

---

**Quick test:** `python3 tools/gui/ai_assistant_app.py`
**Working alternative:** `tools/ai -i`
