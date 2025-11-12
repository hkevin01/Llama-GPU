#!/usr/bin/env python3
"""
Simple LLM Companion with notifications and desktop presence
"""

import subprocess
import time
import webbrowser
import os

def send_notification(title, message):
    subprocess.run(['notify-send', title, message], check=False)

def show_menu():
    menu_text = """
🤖 LLM COMPANION MENU
====================
1. 🌐 Open Web Interface
2. 💬 Terminal Chat  
3. 📊 Check Status
4. ❌ Exit

Choose option (1-4): """
    
    choice = input(menu_text).strip()
    
    if choice == "1":
        print("🌐 Opening Web Interface...")
        webbrowser.open('http://localhost:3000')
        send_notification("🤖 LLM Companion", "Web interface opened")
        
    elif choice == "2":
        print("💬 Opening Terminal Chat...")
        subprocess.run(['gnome-terminal', '--', 'bash', '-c', 'ai-chat; read -p "Press Enter to close..."'])
        
    elif choice == "3":
        print("📊 Checking status...")
        subprocess.run(['gnome-terminal', '--', 'bash', '-c', '''
        echo "🤖 LLM COMPANION STATUS"
        echo "======================"
        echo "Ollama: $(systemctl is-active ollama 2>/dev/null || echo 'inactive')"
        echo "WebUI: $(docker ps --format 'table {{.Status}}' | grep webui || echo 'Not running')"
        ollama list 2>/dev/null || echo "No models available"
        read -p "Press Enter to close..."
        '''])
        
    elif choice == "4":
        print("👋 Goodbye!")
        return False
        
    else:
        print("❌ Invalid option. Try again.")
        
    return True

def main():
    send_notification("🤖 LLM Companion", "Started! Run from terminal for menu.")
    print("🤖 LLM Companion running!")
    print("💡 This terminal provides the menu interface")
    print("🔔 Check your notifications for status updates")
    print("")
    
    running = True
    while running:
        try:
            running = show_menu()
            if running:
                print("\n" + "="*40 + "\n")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 LLM Companion stopped")
            break
    
    send_notification("🤖 LLM Companion", "Stopped")

if __name__ == "__main__":
    main()
