#!/usr/bin/env python3
"""
LLM Companion GUI Launcher for GNOME
Creates a floating window that can be pinned to screen
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
import subprocess
import webbrowser
import threading
import time

class LLMCompanionWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="�� LLM Companion")
        
        # Set window properties
        self.set_default_size(200, 150)
        self.set_resizable(False)
        self.set_keep_above(True)  # Always on top
        self.set_decorated(True)   # Keep window decorations for now
        
        # Position window in bottom-right corner
        screen = Gdk.Screen.get_default()
        width = screen.get_width()
        height = screen.get_height()
        self.move(width - 220, height - 200)
        
        # Create main container
        vbox = Gtk.VBox(spacing=6)
        self.add(vbox)
        
        # Title label
        title_label = Gtk.Label()
        title_label.set_markup("<b>🤖 LLM Companion</b>")
        vbox.pack_start(title_label, False, False, 0)
        
        # Web Interface button
        web_button = Gtk.Button(label="🌐 Web Interface")
        web_button.connect("clicked", self.open_web_interface)
        vbox.pack_start(web_button, False, False, 0)
        
        # Terminal Chat button
        chat_button = Gtk.Button(label="💬 Terminal Chat")
        chat_button.connect("clicked", self.open_terminal_chat)
        vbox.pack_start(chat_button, False, False, 0)
        
        # Status button
        status_button = Gtk.Button(label="📊 Status")
        status_button.connect("clicked", self.show_status)
        vbox.pack_start(status_button, False, False, 0)
        
        # Minimize/Hide button
        hide_button = Gtk.Button(label="➖ Minimize")
        hide_button.connect("clicked", self.toggle_visibility)
        vbox.pack_start(hide_button, False, False, 0)
        
        # Connect window close event
        self.connect("delete-event", self.on_window_close)
        
        self.hidden = False
        
    def open_web_interface(self, widget):
        webbrowser.open('http://localhost:3000')
        
    def open_terminal_chat(self, widget):
        subprocess.Popen([
            'gnome-terminal', 
            '--', 
            'bash', 
            '-c', 
            'echo "🤖 AI Terminal Assistant - Type your question:"; ai-chat; read -p "Press Enter to close..."'
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
            echo "Models:"
            ollama list 2>/dev/null || echo "  No models available"
            echo ""
            read -p "Press Enter to close..."
            '''
        ])
        
    def toggle_visibility(self, widget):
        if self.hidden:
            self.show_all()
            self.hidden = False
            widget.set_label("➖ Minimize")
        else:
            self.hide()
            self.hidden = True
            
    def on_window_close(self, widget, event):
        # Hide instead of closing
        self.hide()
        self.hidden = True
        return True  # Prevent actual closing

def main():
    window = LLMCompanionWindow()
    window.show_all()
    
    # Set up global hotkey to show window (Ctrl+Alt+L)
    print("🤖 LLM Companion window started!")
    print("📍 Window positioned in bottom-right corner")
    print("🔧 Use Alt+Tab to find it if hidden")
    print("⚡ Press Ctrl+C in terminal to quit")
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\n👋 LLM Companion closed")

if __name__ == "__main__":
    main()
