#!/bin/bash
# Simple LLM Companion Launcher

echo "🤖 LLM COMPANION LAUNCHER"
echo "========================"

# Check if services are running
echo "🔍 Checking services..."

# Check Ollama
if pgrep ollama > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "⚠️  Starting Ollama..."
    sudo systemctl start ollama
    sleep 2
fi

# Check Open WebUI
if docker ps | grep -q open-webui; then
    echo "✅ Open WebUI is running"
else
    echo "⚠️  Starting Open WebUI..."
    docker start $(docker ps -a | grep open-webui | awk '{print $1}') 2>/dev/null || \
    docker run -d --name open-webui -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --restart always ghcr.io/open-webui/open-webui:main
    sleep 3
fi

# Start system tray if not running
if ! pgrep -f "python3.*AppIndicator3" > /dev/null; then
    echo "🚀 Starting system tray..."
    nohup python3 -c "
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
import subprocess, webbrowser, warnings
warnings.filterwarnings('ignore')

class LLMTray:
    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new('llm-companion', 'applications-development', AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_title('🤖 LLM')
        
        menu = Gtk.Menu()
        
        web_item = Gtk.MenuItem(label='🌐 Web Interface')
        web_item.connect('activate', lambda x: webbrowser.open('http://localhost:3000'))
        menu.append(web_item)
        
        chat_item = Gtk.MenuItem(label='💬 Terminal Chat')
        chat_item.connect('activate', lambda x: subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'ai-chat; read']))
        menu.append(chat_item)
        
        status_item = Gtk.MenuItem(label='📊 Status')
        status_item.connect('activate', lambda x: subprocess.Popen(['gnome-terminal', '--', 'bash', '-c', 'echo \"🤖 LLM Status:\"; ollama list; docker ps | grep webui; read']))
        menu.append(status_item)
        
        quit_item = Gtk.MenuItem(label='❌ Quit')
        quit_item.connect('activate', lambda x: Gtk.main_quit())
        menu.append(quit_item)
        
        menu.show_all()
        self.indicator.set_menu(menu)

LLMTray()
Gtk.main()
" > /dev/null 2>&1 &
    echo "✅ System tray started"
else
    echo "✅ System tray already running"
fi

echo ""
echo "🎉 LLM Companion is ready!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 Look for the 🤖 icon in your system tray"
echo "🌐 Web Interface: http://localhost:3000"
echo "💬 Terminal: Run 'ai-chat' command"
echo ""
echo "Right-click the tray icon for quick access!"
