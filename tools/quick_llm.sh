#!/bin/bash
# Quick LLM Companion Launcher

clear
echo "🤖 QUICK LLM COMPANION"
echo "====================="
echo ""
echo "Choose an option:"
echo "1. 🌐 Open Web Interface (http://localhost:3000)"
echo "2. 💬 Start Terminal Chat"
echo "3. 🔄 Start Floating Button"
echo "4. 📊 Check Status"
echo "5. ❌ Exit"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "🌐 Opening web interface..."
        xdg-open http://localhost:3000 2>/dev/null || firefox http://localhost:3000 2>/dev/null || google-chrome http://localhost:3000 2>/dev/null
        ;;
    2)
        echo "💬 Starting terminal chat..."
        ai-chat
        ;;
    3)
        echo "�� Starting floating button..."
        python3 simple_floating_button.py &
        echo "✅ Floating button started - look for it on your screen!"
        ;;
    4)
        echo "📊 Checking LLM status..."
        echo ""
        echo "Ollama: $(systemctl is-active ollama 2>/dev/null || echo 'inactive')"
        echo "WebUI: $(docker ps --format 'table {{.Status}}' | grep webui || echo 'Not running')"
        echo ""
        echo "Available models:"
        ollama list 2>/dev/null || echo "No models found"
        echo ""
        read -p "Press Enter to continue..."
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac
