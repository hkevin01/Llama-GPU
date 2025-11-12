#!/usr/bin/env python3
"""
AI Assistant - Native Ubuntu Desktop Application
System tray icon with chat window, command execution, and Beast Mode
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk, Gdk, GLib, AppIndicator3, Notify
import sys
import os
import threading
import subprocess

# Add project root to path
sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")

try:
    from src.backends.ollama import OllamaClient
    from tools.execution.command_executor import SafeCommandExecutor, CommandResult
    from tools.execution.sudo_executor import SudoExecutor
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False


class ChatWindow(Gtk.Window):
    """Main chat window for AI interactions."""

    def __init__(self, model="phi4-mini:3.8b"):
        super().__init__(title="AI Assistant")
        self.set_default_size(600, 500)
        self.set_border_width(10)

        self.model = model
        self.conversation_history = []
        self.beast_mode = False

        # Initialize backends
        if BACKEND_AVAILABLE:
            self.ollama = OllamaClient()
            self.executor = SafeCommandExecutor(interactive=False, allow_root=False)
            self.sudo_executor = SudoExecutor(cache_password=True)
        else:
            self.ollama = None
            self.executor = None
            self.sudo_executor = None

        # Create UI
        self.create_ui()

        # System prompt
        self.add_system_message(
            "You are a helpful, friendly AI assistant integrated into Ubuntu.\n\n"
            "IMPORTANT: You can have normal conversations! Not everything needs to be a command.\n\n"
            "When the user:\n"
            "- Asks a question → Answer it naturally\n"
            "- Wants to chat → Have a conversation\n"
            "- Says 'test' → Respond friendly, ask what they want to test\n"
            "- Asks for help → Explain and help\n"
            "- Requests an action → THEN use commands\n\n"
            "Command Execution (only when needed):\n"
            "Format: $ command (on its own line, clean, no extra characters)\n"
            "Example:\n"
            "  To list files: $ ls -la\n"
            "  NOT: `$ ls -la` or $ ls -la` or other variations\n\n"
            "Available commands:\n"
            "- File: ls, cat, find, grep, mkdir, touch, cp, mv\n"
            "- Info: df, free, ps, whoami, pwd, uname\n"
            "- Dev: python3, git, npm, pip\n"
            "- Net: curl, wget, ping\n\n"
            "For sudo commands (apt, systemctl, etc.):\n"
            "Explain them clearly and tell the user to run manually with sudo.\n\n"
            "Be conversational, helpful, and only execute commands when actually needed!"
        )

    def create_ui(self):
        """Create the user interface."""
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # Header with model selector and Beast Mode toggle
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(header, False, False, 0)

        # Model label
        model_label = Gtk.Label(label="Model:")
        header.pack_start(model_label, False, False, 0)

        # Model selector
        self.model_combo = Gtk.ComboBoxText()
        self.model_combo.append_text("phi4-mini:3.8b")
        self.model_combo.append_text("deepseek-r1:7b")
        self.model_combo.set_active(0)
        self.model_combo.connect("changed", self.on_model_changed)
        header.pack_start(self.model_combo, False, False, 0)

        # Beast Mode toggle
        self.beast_toggle = Gtk.CheckButton(label="🔥 Beast Mode")
        self.beast_toggle.connect("toggled", self.on_beast_toggled)
        header.pack_end(self.beast_toggle, False, False, 0)

        # Chat display area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        vbox.pack_start(scrolled, True, True, 0)

        self.chat_view = Gtk.TextView()
        self.chat_view.set_editable(False)
        self.chat_view.set_cursor_visible(False)
        self.chat_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.chat_view.set_left_margin(10)
        self.chat_view.set_right_margin(10)
        scrolled.add(self.chat_view)

        self.chat_buffer = self.chat_view.get_buffer()

        # Create text tags for styling
        self.chat_buffer.create_tag("user", foreground="#2563eb", weight=700)
        self.chat_buffer.create_tag("assistant", foreground="#7c3aed", weight=700)
        self.chat_buffer.create_tag("system", foreground="#059669", style="italic")
        self.chat_buffer.create_tag("command", family="monospace", background="#f3f4f6")
        self.chat_buffer.create_tag("error", foreground="#dc2626")

        # Input area
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(input_box, False, False, 0)

        self.input_entry = Gtk.Entry()
        self.input_entry.set_placeholder_text("Ask me anything or tell me what to do...")
        self.input_entry.connect("activate", self.on_send_clicked)
        input_box.pack_start(self.input_entry, True, True, 0)

        send_button = Gtk.Button(label="Send")
        send_button.connect("clicked", self.on_send_clicked)
        input_box.pack_start(send_button, False, False, 0)

        # Status bar
        self.statusbar = Gtk.Statusbar()
        vbox.pack_start(self.statusbar, False, False, 0)
        self.status_context = self.statusbar.get_context_id("status")
        self.update_status("Ready")

    def add_system_message(self, message):
        """Add system message to conversation."""
        self.conversation_history.append({
            "role": "system",
            "content": message
        })

    def append_chat(self, role, text, tag=None):
        """Append text to chat display."""
        end_iter = self.chat_buffer.get_end_iter()

        # Use tag if provided, otherwise derive from role
        if tag is None and role:
            tag = role.lower()

        if role and tag:
            # Insert role label with tag styling
            self.chat_buffer.insert_with_tags_by_name(
                end_iter, f"{role}: ", tag
            )
            end_iter = self.chat_buffer.get_end_iter()

        # Insert the actual text
        if tag:
            self.chat_buffer.insert_with_tags_by_name(end_iter, text + "\n\n", tag)
        else:
            self.chat_buffer.insert(end_iter, text + "\n\n")

        # Auto-scroll to bottom
        mark = self.chat_buffer.get_insert()
        self.chat_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)

    def update_status(self, message):
        """Update status bar."""
        self.statusbar.pop(self.status_context)
        self.statusbar.push(self.status_context, message)

    def on_model_changed(self, combo):
        """Handle model selection change."""
        self.model = combo.get_active_text()
        self.update_status(f"Model changed to {self.model}")

    def on_beast_toggled(self, toggle):
        """Handle Beast Mode toggle."""
        self.beast_mode = toggle.get_active()
        if self.beast_mode:
            self.update_status("🔥 Beast Mode ACTIVATED - Autonomous execution enabled")
            self.append_chat("System", "Beast Mode activated! I will work autonomously.", "system")
        else:
            self.update_status("Beast Mode deactivated")
            self.append_chat("System", "Beast Mode deactivated.", "system")

    def on_send_clicked(self, widget):
        """Handle send button click."""
        user_input = self.input_entry.get_text().strip()
        if not user_input:
            return

        self.input_entry.set_text("")
        self.append_chat("You", user_input, "user")

        # Disable input while processing
        self.input_entry.set_sensitive(False)
        self.update_status("Thinking...")

        # Process in thread to keep UI responsive
        thread = threading.Thread(target=self.process_message, args=(user_input,))
        thread.daemon = True
        thread.start()

    def process_message(self, user_input):
        """Process user message and get AI response."""
        if not self.ollama or not self.ollama.is_available():
            GLib.idle_add(self.show_error, "Ollama service not available")
            return

        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        try:
            # Get AI response
            response = ""
            for chunk in self.ollama.chat(
                model=self.model,
                messages=self.conversation_history,
                stream=True
            ):
                response += chunk
                # Update UI in main thread
                GLib.idle_add(self.update_assistant_message, response)

            # Add complete response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })

            # Extract and execute commands
            GLib.idle_add(self.execute_commands_from_response, response)

        except Exception as e:
            GLib.idle_add(self.show_error, f"Error: {str(e)}")
        finally:
            GLib.idle_add(self.input_entry.set_sensitive, True)
            GLib.idle_add(self.update_status, "Ready")

    def update_assistant_message(self, text):
        """Update the assistant's message (streaming)."""
        # Remove previous assistant message and add updated one
        # For simplicity, we'll just show the complete message
        pass

    def show_error(self, message):
        """Show error message."""
        self.append_chat("Error", message, "error")
        self.input_entry.set_sensitive(True)
        self.update_status("Error occurred")

    def execute_commands_from_response(self, response):
        """Extract and execute commands from AI response (including sudo)."""
        if not self.executor:
            return

        import re
        commands = []

        # Extract commands with $ prefix
        for match in re.finditer(r'\$\s+([^\n]+)', response):
            cmd = match.group(1).strip()
            # Remove markdown backticks and other formatting
            cmd = cmd.strip('`').strip("'").strip('"').strip()
            if cmd and cmd not in commands:
                commands.append(cmd)

        if not commands:
            self.append_chat("Assistant", response, "assistant")
            return

        # Show AI response first
        self.append_chat("Assistant", response, "assistant")

        # Execute commands
        for cmd in commands:
            # Check if command needs sudo
            needs_sudo = cmd.strip().startswith('sudo ') or any(
                cmd.strip().startswith(root_cmd) for root_cmd in [
                    'apt', 'apt-get', 'systemctl', 'service',
                    'useradd', 'userdel', 'usermod', 'passwd',
                    'mount', 'umount'
                ]
            )

            if needs_sudo:
                # Execute with sudo executor
                self.append_chat("", f"🔐 Executing sudo command: {cmd}", "command")

                try:
                    # Run sudo command in separate thread to avoid blocking UI
                    def run_sudo():
                        sudo_result = self.sudo_executor.execute(cmd, confirm=not self.beast_mode)

                        # Convert to CommandResult format
                        result = CommandResult(
                            command=sudo_result.command,
                            returncode=sudo_result.exit_code,
                            stdout=sudo_result.output,
                            stderr=sudo_result.error,
                            execution_time=0.0
                        )

                        # Display result in UI thread
                        GLib.idle_add(self.show_command_result, result)

                    thread = threading.Thread(target=run_sudo, daemon=True)
                    thread.start()

                except Exception as e:
                    self.append_chat("", f"❌ Sudo execution error: {e}", "error")

            else:
                # Regular command
                self.append_chat("", f"Executing: {cmd}", "command")

                try:
                    result = self.executor.execute(cmd, confirm=not self.beast_mode)
                    self.show_command_result(result)
                except Exception as e:
                    self.append_chat("", f"❌ Error: {str(e)}", "error")

    def show_command_result(self, result):
        """Display command execution result."""
        if result.success:
            output = result.stdout.strip() if result.stdout else "(no output)"
            # Show full output, but truncate extremely long outputs (>5000 chars)
            if len(output) > 5000:
                self.append_chat("", f"✅ {output[:5000]}\n\n... (output truncated, {len(output)} total characters)", "system")
            else:
                self.append_chat("", f"✅ {output}", "system")
        else:
            error = result.stderr.strip() if result.stderr else "Command failed"
            if len(error) > 2000:
                self.append_chat("", f"❌ {error[:2000]}\n\n... (error truncated)", "error")
            else:
                self.append_chat("", f"❌ {error}", "error")


class AIAssistantApp:
    """Main application with system tray."""

    def __init__(self):
        # Initialize notification system
        Notify.init("AI Assistant")

        # Create indicator
        self.indicator = AppIndicator3.Indicator.new(
            "ai-assistant",
            "system-run-symbolic",
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.create_menu())

        # Chat window (initially hidden)
        self.chat_window = None

    def create_menu(self):
        """Create system tray menu."""
        menu = Gtk.Menu()

        # Open Chat
        chat_item = Gtk.MenuItem(label="💬 Open Chat")
        chat_item.connect("activate", self.show_chat_window)
        menu.append(chat_item)

        # Quick Actions submenu
        quick_menu = Gtk.Menu()
        quick_item = Gtk.MenuItem(label="⚡ Quick Actions")
        quick_item.set_submenu(quick_menu)

        action1 = Gtk.MenuItem(label="System Info")
        action1.connect("activate", lambda x: self.quick_action("show system information"))
        quick_menu.append(action1)

        action2 = Gtk.MenuItem(label="Disk Usage")
        action2.connect("activate", lambda x: self.quick_action("check disk usage"))
        quick_menu.append(action2)

        action3 = Gtk.MenuItem(label="Memory Status")
        action3.connect("activate", lambda x: self.quick_action("show memory usage"))
        quick_menu.append(action3)

        menu.append(quick_item)

        # Separator
        menu.append(Gtk.SeparatorMenuItem())

        # About
        about_item = Gtk.MenuItem(label="ℹ️ About")
        about_item.connect("activate", self.show_about)
        menu.append(about_item)

        # Quit
        quit_item = Gtk.MenuItem(label="❌ Quit")
        quit_item.connect("activate", self.quit_app)
        menu.append(quit_item)

        menu.show_all()
        return menu

    def show_chat_window(self, widget=None):
        """Show or create chat window."""
        if self.chat_window is None:
            self.chat_window = ChatWindow()
            self.chat_window.connect("delete-event", self.on_chat_close)

        self.chat_window.show_all()
        self.chat_window.present()

    def on_chat_close(self, window, event):
        """Handle chat window close."""
        window.hide()
        return True  # Prevent destruction

    def quick_action(self, action):
        """Execute quick action."""
        self.show_chat_window()
        self.chat_window.input_entry.set_text(action)
        self.chat_window.on_send_clicked(None)

    def show_about(self, widget):
        """Show about dialog."""
        dialog = Gtk.AboutDialog()
        dialog.set_program_name("AI Assistant")
        dialog.set_version("1.0")
        dialog.set_comments("Native Ubuntu AI Assistant powered by Phi4-Mini")
        dialog.set_website("https://github.com/hkevin01/Llama-GPU")
        dialog.set_logo_icon_name("system-run-symbolic")
        dialog.run()
        dialog.destroy()

    def quit_app(self, widget):
        """Quit application."""
        Notify.uninit()
        Gtk.main_quit()


def main():
    """Main entry point."""
    # Check if Ollama is available
    if BACKEND_AVAILABLE:
        client = OllamaClient()
        if not client.is_available():
            dialog = Gtk.MessageDialog(
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Ollama Service Not Running"
            )
            dialog.format_secondary_text(
                "Please start Ollama service:\n\n"
                "$ ollama serve\n\n"
                "Or install Ollama if not installed."
            )
            dialog.run()
            dialog.destroy()
            return

    app = AIAssistantApp()

    # Show notification
    notification = Notify.Notification.new(
        "AI Assistant Started",
        "Click the system tray icon to open chat",
        "system-run-symbolic"
    )
    notification.show()

    Gtk.main()


if __name__ == "__main__":
    main()
