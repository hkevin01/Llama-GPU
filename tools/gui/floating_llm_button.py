#!/usr/bin/env python3
"""
Floating LLM Companion Button - Always visible on screen
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import subprocess
import webbrowser

class FloatingLLMButton(Gtk.Window):
    def __init__(self):
        super().__init__(title="LLM")
        
        # Configure window to be a floating button
        self.set_default_size(80, 40)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_decorated(False)  # No title bar
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        
        # Position in top-right corner
        screen = Gdk.Screen.get_default()
        monitor = screen.get_primary_monitor()
        geometry = screen.get_monitor_geometry(monitor)
        self.move(geometry.width - 100, 50)
        
        # Create the button
        self.button = Gtk.Button(label="🤖 AI")
        self.button.connect("clicked", self.show_menu)
        self.add(self.button)
        
        # Make draggable
        self.button.connect("button-press-event", self.on_button_press)
        self.button.connect("motion-notify-event", self.on_mouse_move)
        self.button.set_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.dragging = False
        
        # Set CSS for styling
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b"""
        button {
            background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: 2px solid #4a5568;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            padding: 5px 10px;
        }
        button:hover {
            background: linear-gradient(45deg, #764ba2 0%, #667eea 100%);
            transform: scale(1.05);
        }
        """)
        
        style_context = self.button.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
    def on_button_press(self, widget, event):
        if event.button == 1:  # Left click
            self.drag_start_x = event.x_root - self.get_position()[0]
            self.drag_start_y = event.y_root - self.get_position()[1]
            self.dragging = True
        return False
        
    def on_mouse_move(self, widget, event):
        if self.dragging and event.state & Gdk.ModifierType.BUTTON1_MASK:
            x = event.x_root - self.drag_start_x
            y = event.y_root - self.drag_start_y
            self.move(int(x), int(y))
        return False
        
    def show_menu(self, widget):
        # Create popup menu
        menu = Gtk.Menu()
        
        # Web Interface
        web_item = Gtk.MenuItem(label="🌐 Web Interface")
        web_item.connect("activate", lambda x: webbrowser.open('http://localhost:3000'))
        menu.append(web_item)
        
        # Terminal Chat
        chat_item = Gtk.MenuItem(label="💬 Terminal Chat")
        chat_item.connect("activate", self.open_terminal)
        menu.append(chat_item)
        
        # Status
        status_item = Gtk.MenuItem(label="📊 Status")
        status_item.connect("activate", self.show_status)
        menu.append(status_item)
        
        # Separator
        sep = Gtk.SeparatorMenuItem()
        menu.append(sep)
        
        # Hide button
        hide_item = Gtk.MenuItem(label="👁️ Hide (Alt+Tab to find)")
        hide_item.connect("activate", lambda x: self.iconify())
        menu.append(hide_item)
        
        # Quit
        quit_item = Gtk.MenuItem(label="❌ Quit")
        quit_item.connect("activate", lambda x: Gtk.main_quit())
        menu.append(quit_item)
        
        menu.show_all()
        menu.popup_at_widget(widget, Gdk.Gravity.SOUTH_WEST, Gdk.Gravity.NORTH_WEST, None)
        
    def open_terminal(self, widget):
        subprocess.Popen([
            'gnome-terminal', 
            '--', 
            'bash', 
            '-c', 
            'echo "🤖 AI Assistant Ready!"; ai-chat; read -p "Press Enter to close..."'
        ])
        
    def show_status(self, widget):
        subprocess.Popen([
            'gnome-terminal',
            '--',
            'bash',
            '-c',
            '''
            echo "🤖 LLM COMPANION STATUS"
            echo "======================"
            echo "Ollama: $(systemctl is-active ollama 2>/dev/null || echo 'inactive')"
            echo "WebUI: $(docker ps --format 'table {{.Status}}' | grep webui || echo 'Not running')"
            echo ""
            echo "Available Models:"
            ollama list 2>/dev/null || echo "  No models found"
            echo ""
            echo "Quick Test:"
            timeout 3 curl -s http://localhost:11434/api/tags >/dev/null && echo "  ✅ API responding" || echo "  ❌ API not responding"
            echo ""
            read -p "Press Enter to close..."
            '''
        ])

def main():
    window = FloatingLLMButton()
    window.show_all()
    
    print("🤖 Floating LLM Button started!")
    print("📍 Look for the '🤖 AI' button on your screen")
    print("🖱️  Click it to access LLM features")
    print("🔄 Drag it to move around")
    print("⚡ Press Ctrl+C here to quit")
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\n👋 Floating LLM Button closed")

if __name__ == "__main__":
    main()
