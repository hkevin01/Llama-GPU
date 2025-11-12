#!/bin/bash
# Local LLM Complete Setup - Ollama + Open WebUI
# One-click setup for local AI assistance with GUI and terminal interfaces

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🤖 Local LLM Complete Setup${NC}"
echo -e "${CYAN}============================${NC}"
echo ""
echo -e "${BLUE}This script will install:${NC}"
echo "• Ollama - Local LLM engine"
echo "• Open WebUI - Web interface for chat"  
echo "• AI helper scripts for terminal"
echo "• Lightweight AI models for quick responses"
echo ""

# Function to print status
print_status() {
    local status="$1"
    local message="$2"
    case $status in
        "INFO")  echo -e "${BLUE}ℹ️  $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
    esac
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to show installation menu
show_menu() {
    echo -e "${BLUE}🚀 Choose installation option:${NC}"
    echo ""
    echo "1. Complete Setup (Recommended)"
    echo "   - Install Ollama + Open WebUI"
    echo "   - Download lightweight AI models"
    echo "   - Setup terminal helpers"
    echo "   - Configure auto-start & system tray"
    echo ""
    echo "2. Complete Setup + Auto-Start"
    echo "   - Everything from option 1"
    echo "   - Boot-time AI companion"
    echo "   - System tray icon"
    echo ""
    echo "3. Ollama Only"
    echo "   - Terminal-based AI assistance"
    echo "   - Lightweight and fast"
    echo ""
    echo "4. Open WebUI Only"
    echo "   - Requires existing Ollama installation"
    echo "   - Web-based chat interface"
    echo ""
    echo "5. Auto-Start Setup Only"
    echo "   - Add auto-start to existing installation"
    echo "   - System tray integration"
    echo ""
    echo "6. Check Current Installation"
    echo "   - Test and show status"
    echo ""
    echo "7. Launch AI Assistant"
    echo "   - Open existing AI interface"
    echo ""
    
    read -p "Enter your choice (1-7): " choice
    echo ""
    
    case $choice in
        1) install_complete_setup ;;
        2) install_complete_setup_autostart ;;
        3) install_ollama_only ;;
        4) install_webui_only ;;
        5) install_autostart_only ;;
        6) check_installation ;;
        7) launch_assistant ;;
        *) 
            print_status "ERROR" "Invalid choice. Please run the script again."
            exit 1
            ;;
    esac
}

# Function for complete setup
install_complete_setup() {
    print_status "INFO" "Starting complete Local LLM setup..."
    echo ""
    
    # Step 1: Install Ollama
    print_status "INFO" "Step 1/3: Installing Ollama..."
    if ! "$PWD/scripts/system/install_ollama.sh"; then
        print_status "ERROR" "Ollama installation failed"
        exit 1
    fi
    
    echo ""
    print_status "SUCCESS" "Ollama installation completed"
    echo ""
    
    # Step 2: Install Open WebUI
    print_status "INFO" "Step 2/3: Installing Open WebUI..."
    if ! "$PWD/scripts/system/install_open_webui.sh"; then
        print_status "ERROR" "Open WebUI installation failed"
        exit 1
    fi
    
    echo ""
    print_status "SUCCESS" "Open WebUI installation completed"
    echo ""
    
    # Step 3: Final setup and testing
    print_status "INFO" "Step 3/3: Final setup and testing..."
    sleep 2
    
    create_desktop_launchers
    show_completion_summary
    
    print_status "SUCCESS" "Complete setup finished!"
}

# Function for complete setup with auto-start
install_complete_setup_autostart() {
    print_status "INFO" "Starting complete Local LLM setup with auto-start..."
    echo ""
    
    # Step 1: Install Ollama
    print_status "INFO" "Step 1/4: Installing Ollama..."
    if ! "$PWD/scripts/system/install_ollama.sh"; then
        print_status "ERROR" "Ollama installation failed"
        exit 1
    fi
    
    echo ""
    print_status "SUCCESS" "Ollama installation completed"
    echo ""
    
    # Step 2: Install Open WebUI
    print_status "INFO" "Step 2/4: Installing Open WebUI..."
    if ! "$PWD/scripts/system/install_open_webui.sh"; then
        print_status "ERROR" "Open WebUI installation failed"
        exit 1
    fi
    
    echo ""
    print_status "SUCCESS" "Open WebUI installation completed"
    echo ""
    
    # Step 3: Setup auto-start and system tray
    print_status "INFO" "Step 3/4: Setting up auto-start and system tray..."
    if ! "$PWD/scripts/system/setup_llm_autostart.sh"; then
        print_status "ERROR" "Auto-start setup failed"
        exit 1
    fi
    
    echo ""
    print_status "SUCCESS" "Auto-start setup completed"
    echo ""
    
    # Step 4: Final setup and testing
    print_status "INFO" "Step 4/4: Final setup and testing..."
    sleep 2
    
    show_completion_summary_with_autostart
    
    print_status "SUCCESS" "Complete setup with auto-start finished!"
}

# Function to install auto-start only
install_autostart_only() {
    print_status "INFO" "Setting up auto-start for existing installation..."
    if ! "$PWD/scripts/system/setup_llm_autostart.sh"; then
        print_status "ERROR" "Auto-start setup failed"
        exit 1
    fi
    print_status "SUCCESS" "Auto-start setup completed!"
}

# Function to install Ollama only
install_ollama_only() {
    print_status "INFO" "Installing Ollama only..."
    if ! "$PWD/scripts/system/install_ollama.sh"; then
        print_status "ERROR" "Ollama installation failed"
        exit 1
    fi
    print_status "SUCCESS" "Ollama installation completed!"
}

# Function to install Open WebUI only
install_webui_only() {
    print_status "INFO" "Installing Open WebUI only..."
    if ! "$PWD/scripts/system/install_open_webui.sh"; then
        print_status "ERROR" "Open WebUI installation failed"
        exit 1
    fi
    print_status "SUCCESS" "Open WebUI installation completed!"
}

# Function to check current installation
check_installation() {
    print_status "INFO" "Checking current installation status..."
    echo ""
    
    # Check Ollama
    if command_exists "ollama"; then
        local ollama_version=$(ollama --version 2>/dev/null || echo "unknown")
        print_status "SUCCESS" "Ollama installed: $ollama_version"
        
        # Check if Ollama is running
        if curl -s http://localhost:11434 >/dev/null 2>&1; then
            print_status "SUCCESS" "Ollama service is running"
        else
            print_status "WARNING" "Ollama service is not running"
            echo "  Start with: ollama serve"
        fi
        
        # List models
        print_status "INFO" "Installed models:"
        ollama list | head -10
    else
        print_status "ERROR" "Ollama is not installed"
    fi
    
    echo ""
    
    # Check Open WebUI
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_status "SUCCESS" "Open WebUI is running on port 3000"
    elif command_exists "docker" && docker ps | grep -q "open-webui"; then
        print_status "SUCCESS" "Open WebUI Docker container is running"
    elif command_exists "open-webui"; then
        print_status "WARNING" "Open WebUI is installed but not running"
        echo "  Start with: open-webui start"
    else
        print_status "ERROR" "Open WebUI is not installed"
    fi
    
    echo ""
    
    # Check helper scripts
    if command_exists "ai-chat"; then
        print_status "SUCCESS" "ai-chat helper script is available"
    else
        print_status "WARNING" "ai-chat helper script not found"
    fi
    
    if command_exists "ai-models"; then
        print_status "SUCCESS" "ai-models helper script is available"
    else
        print_status "WARNING" "ai-models helper script not found"
    fi
    
    if command_exists "ai-assistant"; then
        print_status "SUCCESS" "ai-assistant launcher is available"
    else
        print_status "WARNING" "ai-assistant launcher not found"
    fi
}

# Function to launch assistant
launch_assistant() {
    print_status "INFO" "Launching AI Assistant..."
    
    if command_exists "ai-assistant"; then
        ai-assistant
    elif command_exists "ai-chat"; then
        ai-chat
    elif curl -s http://localhost:3000 >/dev/null 2>&1; then
        print_status "INFO" "Opening web interface..."
        xdg-open "http://localhost:3000" 2>/dev/null || echo "Open: http://localhost:3000"
    else
        print_status "ERROR" "No AI assistant found. Please install first."
        exit 1
    fi
}

# Function to create desktop launchers
create_desktop_launchers() {
    print_status "INFO" "Creating desktop launchers..."
    
    # Create desktop directory
    mkdir -p "$HOME/.local/share/applications"
    
    # Create Open WebUI desktop launcher
    cat > "$HOME/.local/share/applications/open-webui.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Open WebUI
Comment=Local AI Chat Interface
Icon=applications-internet
Exec=sh -c 'xdg-open http://localhost:3000'
Categories=Network;Chat;
StartupNotify=true
EOF
    
    # Create AI Assistant desktop launcher
    cat > "$HOME/.local/share/applications/ai-assistant.desktop" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=AI Assistant
Comment=Local AI Terminal Assistant
Icon=applications-development
Exec=gnome-terminal -- ai-assistant
Categories=System;Utility;
StartupNotify=true
EOF
    
    print_status "SUCCESS" "Desktop launchers created"
}

# Function to show completion summary
show_completion_summary() {
    echo ""
    echo -e "${GREEN}🎉 Local LLM Setup Complete!${NC}"
    echo ""
    echo -e "${CYAN}🚀 Available Interfaces:${NC}"
    echo ""
    echo -e "${BLUE}1. Web Interface (GUI):${NC}"
    echo "   • URL: http://localhost:3000"
    echo "   • Command: open-webui open"
    echo "   • Features: File upload, web search, model switching"
    echo ""
    echo -e "${BLUE}2. Terminal Interface:${NC}"
    echo "   • Command: ai-chat \"your question\""
    echo "   • Quick and lightweight"
    echo "   • Perfect for coding assistance"
    echo ""
    echo -e "${BLUE}3. Combined Launcher:${NC}"
    echo "   • Command: ai-assistant"
    echo "   • Choose between terminal/web interface"
    echo ""
    echo -e "${CYAN}📚 Model Management:${NC}"
    echo "   • List models: ai-models list"
    echo "   • Download models: ai-models download <name>"
    echo "   • Set default: ai-models set-default <name>"
    echo ""
    echo -e "${CYAN}🔧 Service Management:${NC}"
    echo "   • Start web UI: open-webui start"
    echo "   • Stop web UI: open-webui stop"
    echo "   • Check status: open-webui status"
    echo ""
    echo -e "${YELLOW}💡 Quick Examples:${NC}"
    echo '   ai-chat "how to install nodejs"'
    echo '   ai-chat "fix file permissions in linux"'
    echo '   ai-chat "explain this error message"'
    echo ""
    echo -e "${YELLOW}🎯 Next Steps:${NC}"
    echo "1. Open http://localhost:3000 and create your account"
    echo "2. Try the terminal interface with: ai-chat"
    echo "3. Download additional models if needed"
    echo "4. Restart terminal to use new commands"
    echo ""
    print_status "SUCCESS" "Setup completed! Enjoy your local AI assistant!"
}

# Function to show completion summary with auto-start
show_completion_summary_with_autostart() {
    echo ""
    echo -e "${GREEN}🎉 Local LLM Setup Complete with Auto-Start!${NC}"
    echo ""
    echo -e "${CYAN}🚀 Your AI Companion is Always Available:${NC}"
    echo ""
    echo -e "${BLUE}✅ Auto-Start Features:${NC}"
    echo "   • Ollama service starts automatically on boot"
    echo "   • System tray icon appears on login"
    echo "   • Open WebUI launches with user session"
    echo "   • Always-on AI assistance"
    echo ""
    echo -e "${BLUE}📱 System Tray Access:${NC}"
    echo "   • Left-click tray icon: Open web interface"
    echo "   • Right-click tray icon: Context menu"
    echo "   • Status indicator: Shows service health"
    echo ""
    echo -e "${BLUE}🎯 Available Interfaces:${NC}"
    echo "   • Web Interface: http://localhost:3000"
    echo "   • Terminal: ai-chat \"your question\""
    echo "   • Application launcher: Search 'LLM Assistant'"
    echo ""
    echo -e "${CYAN}📚 Model Management:${NC}"
    echo "   • ai-models list - Show installed models"
    echo "   • ai-models download <name> - Add new models"
    echo "   • ai-models set-default <name> - Change default"
    echo ""
    echo -e "${YELLOW}💡 Quick Examples:${NC}"
    echo '   ai-chat "how to update ubuntu"'
    echo '   ai-chat "fix docker permission error"'
    echo '   ai-chat "python script to read csv"'
    echo ""
    echo -e "${YELLOW}🎊 Next Steps:${NC}"
    echo "1. Reboot to test full auto-start functionality"
    echo "2. Look for AI assistant icon in system tray after reboot"
    echo "3. Click tray icon to access your AI assistant anytime"
    echo "4. Search for 'LLM Assistant' in application launcher"
    echo ""
    echo -e "${CYAN}🌟 Your persistent AI companion is ready!${NC}"
    echo -e "${GREEN}No more manual startup - AI assistance is always one click away!${NC}"
}

# Function to check script dependencies
check_dependencies() {
    local script_dir="$PWD"
    
    if [ ! -f "$script_dir/scripts/system/install_ollama.sh" ]; then
        print_status "ERROR" "install_ollama.sh script not found"
        print_status "INFO" "Please run this from the useful-scripts directory"
        exit 1
    fi
    
    if [ ! -f "$script_dir/scripts/system/install_open_webui.sh" ]; then
        print_status "ERROR" "install_open_webui.sh script not found"
        print_status "INFO" "Please run this from the useful-scripts directory"
        exit 1
    fi
    
    # Make scripts executable
    chmod +x "$script_dir/scripts/system/install_ollama.sh"
    chmod +x "$script_dir/scripts/system/install_open_webui.sh"
}

# Main function
main() {
    # Check if we're in the right directory
    check_dependencies
    
    # Show menu and handle choice
    show_menu
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "Local LLM Complete Setup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h        Show this help message"
        echo "  --complete        Run complete setup (non-interactive)"
        echo "  --complete-auto   Run complete setup with auto-start"
        echo "  --ollama-only     Install Ollama only"
        echo "  --webui-only      Install Open WebUI only"  
        echo "  --autostart-only  Setup auto-start for existing installation"
        echo "  --check           Check current installation"
        echo "  --launch          Launch AI assistant"
        echo ""
        echo "This script provides a complete local LLM setup with both"
        echo "terminal and web interfaces for AI assistance."
        exit 0
        ;;
    --complete)
        check_dependencies
        install_complete_setup
        ;;
    --complete-auto)
        check_dependencies
        install_complete_setup_autostart
        ;;
    --ollama-only)
        check_dependencies
        install_ollama_only
        ;;
    --webui-only)
        check_dependencies
        install_webui_only
        ;;
    --autostart-only)
        check_dependencies
        install_autostart_only
        ;;
    --check)
        check_installation
        ;;
    --launch)
        launch_assistant
        ;;
    *)
        main
        ;;
esac