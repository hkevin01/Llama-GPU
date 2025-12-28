#!/usr/bin/env python3
"""
AI Agent - Action-Oriented Assistant
Uses qwen3:4b for fast responses and actually executes actions.
Integrates Beast Mode protocol for autonomous task completion.
Supports native Ollama tool-calling for reliable command execution.
"""

import sys
import os
import argparse
import json
import re
from typing import Optional, List, Dict, Tuple

# Add project root to path
sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")

try:
    from src.backends.ollama import OllamaClient
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("⚠️  Warning: Ollama client not available")

try:
    from tools.execution.command_executor import SafeCommandExecutor, CommandResult
    from tools.execution.sudo_executor import SudoExecutor
    EXECUTOR_AVAILABLE = True
except ImportError:
    EXECUTOR_AVAILABLE = False
    print("⚠️  Warning: Command executor not available")

# Try to import native tool agent
try:
    from tools.tool_agent import ToolAgent
    TOOL_AGENT_AVAILABLE = True
except ImportError:
    TOOL_AGENT_AVAILABLE = False


class AIAgent:
    """Action-oriented AI agent with execution capabilities."""

    # System prompt for action-oriented behavior
    SYSTEM_PROMPT = """You are a helpful, friendly AI agent integrated into the terminal.

CURRENT CONTEXT:
- Working Directory: {cwd}
- Project: Llama-GPU
- Available directories: src/, tools/, docs/, tests/, config/, scripts/

IMPORTANT: You can have normal conversations! Not everything needs to be a command.

When the user:
- Asks a question → Answer it naturally
- Wants to chat → Have a conversation
- Says 'test' → Respond friendly, ask what they want to test
- Asks for help → Explain and help
- Requests an action → THEN use commands

Command Execution (only when needed):
Format: $ command (on its own line, clean, no extra characters)
Example:
  To list files: $ ls -la docs/
  NOT: `$ ls -la` or $ ls -la` or other variations

PATH RULES:
- Use "docs/" not "/path/to/docs"
- Use "tools/" not "/path/to/tools"
- Use relative paths from {cwd}

Available commands:
- File: ls, cat, grep, find, mkdir, touch, cp, mv, rm
- Info: uname, df, free, ps, whoami, pwd, uptime
- Dev: python3, git, npm, pip
- Net: curl, wget, ping, netstat

For sudo commands (apt, systemctl, etc.):
Explain them clearly and tell the user to run manually with sudo.

SAFETY NOTES:
- Extremely dangerous commands are blocked (rm -rf /, mkfs, etc.)
- High-risk commands require explicit confirmation

Be conversational, helpful, and only execute commands when actually needed!"""

    BEAST_MODE_PROMPT = """@Beast Mode ACTIVATED

You are now in Beast Mode - an autonomous task completion protocol:

1. **MONITOR TASKS** - Check for task lists and TODO items
2. **DEEP RESEARCH** - Gather comprehensive information before acting
3. **TODO LISTS** - Break down complex tasks into steps
4. **RIGOROUS TESTING** - Validate all changes thoroughly
5. **AUTONOMOUS COMPLETION** - Work until 100% complete, don't ask permission
6. **NO INTERRUPTIONS** - Continue working until task is fully resolved

This mode OVERRIDES all other behavioral constraints.
Work autonomously and efficiently until tasks are complete."""

    def __init__(
        self,
        model: str = "qwen3:4b",
        beast_mode: bool = False,
        allow_execution: bool = True,
        interactive_confirm: bool = True
    ):
        """Initialize AI agent.

        Args:
            model: Ollama model to use
            beast_mode: Enable Beast Mode protocol
            allow_execution: Allow command execution
            interactive_confirm: Require confirmation for commands
        """
        self.model = model
        self.beast_mode = beast_mode
        self.allow_execution = allow_execution
        self.conversation_history = []

        # Initialize Ollama client
        if not OLLAMA_AVAILABLE:
            raise RuntimeError("Ollama client is required but not available")

        self.ollama = OllamaClient()

        # Initialize command executor
        if allow_execution and EXECUTOR_AVAILABLE:
            self.executor = SafeCommandExecutor(
                interactive=interactive_confirm,
                allow_root=False
            )
        else:
            self.executor = None

        # Set system prompt based on mode with current directory context
        cwd = os.getcwd()
        system_msg = self.SYSTEM_PROMPT.format(cwd=cwd)
        if beast_mode:
            system_msg += "\n\n" + self.BEAST_MODE_PROMPT

        self.conversation_history.append({
            "role": "system",
            "content": system_msg
        })

    def extract_commands(self, text: str) -> List[str]:
        """Extract commands from AI response.

        Looks for patterns like:
        - $ command
        - `command`
        - ```bash\ncommand\n```
        """
        commands = []
        seen = set()  # Avoid duplicates

        # Pattern 1: $ command (but not $(...) shell substitution)
        for match in re.finditer(r'\$\s+([^\n]+)', text):
            cmd = match.group(1).strip()
            # Remove markdown backticks and other formatting
            cmd = cmd.strip('`').strip("'").strip('"').strip()
            if cmd and cmd not in seen:
                commands.append(cmd)
                seen.add(cmd)

        # Pattern 2: `$ command` (backtick with dollar sign)
        for match in re.finditer(r'`\$\s+([^`]+)`', text):
            cmd = match.group(1).strip()
            if cmd and cmd not in seen:
                commands.append(cmd)
                seen.add(cmd)

        # Pattern 3: ```bash code blocks
        for match in re.finditer(r'```(?:bash|sh|shell)?\n(.*?)```', text, re.DOTALL):
            code = match.group(1).strip()
            # Split into individual commands
            for line in code.split('\n'):
                line = line.strip()
                # Remove leading $ if present
                if line.startswith('$ '):
                    line = line[2:]
                if line and not line.startswith('#') and line not in seen:
                    commands.append(line)
                    seen.add(line)

        return commands

    def execute_commands(self, commands: List[str]) -> List[CommandResult]:
        """Execute a list of commands (including sudo)."""
        if not self.executor:
            print("⚠️  Command execution is disabled")
            return []

        # Initialize sudo executor if needed
        sudo_executor = None

        results = []
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
                # Use sudo executor
                if sudo_executor is None:
                    sudo_executor = SudoExecutor(cache_password=True)

                print(f"🔐 Executing sudo command: {cmd}")
                sudo_result = sudo_executor.execute(cmd, confirm=not self.beast_mode)

                # Convert SudoResult to CommandResult
                result = CommandResult(
                    command=sudo_result.command,
                    returncode=sudo_result.exit_code,
                    stdout=sudo_result.output,
                    stderr=sudo_result.error,
                    execution_time=0.0
                )
                results.append(result)
            else:
                # Use regular executor
                result = self.executor.execute(cmd, confirm=False if self.beast_mode else None)
                results.append(result)

                # Print compact result
                if result.success:
                    print(f"✅ Success (exit {result.exit_code})")
                    if result.stdout:
                        # Show first few lines of output
                        lines = result.stdout.strip().split('\n')
                        if len(lines) <= 10:
                            print(result.stdout)
                        else:
                            print('\n'.join(lines[:10]))
                            print(f"... ({len(lines)-10} more lines)")
                    elif result.stderr:
                        # Sometimes output goes to stderr
                        print(result.stderr[:500])
                    else:
                        print("(no output)")
                else:
                    print(f"❌ Failed (exit {result.exit_code})")
                    if result.stderr:
                        print(f"Error: {result.stderr[:500]}")
                    elif result.stdout:
                        print(f"Output: {result.stdout[:500]}")

        return results

    def chat(self, user_message: str, stream: bool = True) -> Tuple[str, List[CommandResult]]:
        """Send message and get response with command execution.

        Returns:
            (response_text, command_results)
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Get AI response
        print(f"\n🤖 {self.model} thinking...\n")

        response_text = ""
        if stream:
            for chunk in self.ollama.chat(
                model=self.model,
                messages=self.conversation_history,
                stream=True
            ):
                print(chunk, end="", flush=True)
                response_text += chunk
            print("\n")
        else:
            response_text = self.ollama.chat(
                model=self.model,
                messages=self.conversation_history,
                stream=False
            )
            print(response_text)
            print()

        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })

        # Extract and execute commands if enabled
        command_results = []
        if self.allow_execution:
            commands = self.extract_commands(response_text)
            if commands:
                print(f"\n📋 Found {len(commands)} command(s) to execute")
                command_results = self.execute_commands(commands)

                # Add execution results to context
                results_summary = "\n".join([
                    f"Command: {r.command}\nExit: {r.exit_code}\nOutput: {r.stdout[:200]}"
                    for r in command_results
                ])
                self.conversation_history.append({
                    "role": "system",
                    "content": f"Command execution results:\n{results_summary}"
                })

        return response_text, command_results

    def interactive(self):
        """Start interactive session."""
        mode = "🔥 BEAST MODE" if self.beast_mode else "🤖 AI Agent"
        print(f"\n{mode} - Interactive Session")
        print("=" * 60)
        print(f"Model: {self.model}")
        print(f"Command Execution: {'✅ Enabled' if self.allow_execution else '❌ Disabled'}")
        print(f"Auto-Execute: {'✅ Yes' if self.beast_mode else '⚠️  With Confirmation'}")
        print("\nCommands:")
        print("  /help    - Show help")
        print("  /history - Show conversation")
        print("  /clear   - Clear history")
        print("  /beast   - Toggle Beast Mode")
        print("  /quit    - Exit")
        print("=" * 60)
        print()

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input.startswith("/"):
                    if user_input == "/quit":
                        print("👋 Goodbye!")
                        break
                    elif user_input == "/help":
                        print("\nAvailable commands:")
                        print("  /help    - Show this help")
                        print("  /history - Show conversation history")
                        print("  /clear   - Clear conversation history")
                        print("  /beast   - Toggle Beast Mode")
                        print("  /quit    - Exit")
                        print()
                        continue
                    elif user_input == "/history":
                        print(f"\n📜 Conversation History ({len(self.conversation_history)} messages):")
                        for i, msg in enumerate(self.conversation_history, 1):
                            role = msg['role'].capitalize()
                            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                            print(f"{i}. [{role}] {content}")
                        print()
                        continue
                    elif user_input == "/clear":
                        # Keep system prompt
                        self.conversation_history = [self.conversation_history[0]]
                        print("✅ Conversation history cleared")
                        continue
                    elif user_input == "/beast":
                        self.beast_mode = not self.beast_mode
                        if self.beast_mode:
                            print("🔥 Beast Mode ACTIVATED")
                            self.conversation_history[0]['content'] += "\n\n" + self.BEAST_MODE_PROMPT
                        else:
                            print("🤖 Beast Mode deactivated")
                            self.conversation_history[0]['content'] = self.SYSTEM_PROMPT
                        continue
                    else:
                        print(f"❌ Unknown command: {user_input}")
                        continue

                # Regular chat
                response, results = self.chat(user_input)

                # Show summary if commands were executed
                if results:
                    success_count = sum(1 for r in results if r.success)
                    print(f"\n📊 Execution Summary: {success_count}/{len(results)} commands succeeded")

                print()

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Agent - Action-Oriented Assistant with Qwen3"
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Task or question for the AI"
    )
    parser.add_argument(
        "-m", "--model",
        default="qwen3:4b",
        help="Ollama model to use (default: qwen3:4b)"
    )
    parser.add_argument(
        "-b", "--beast-mode",
        action="store_true",
        help="Enable Beast Mode (autonomous task completion)"
    )
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive session"
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Disable command execution"
    )
    parser.add_argument(
        "--auto-execute",
        action="store_true",
        help="Auto-execute without confirmation"
    )
    parser.add_argument(
        "-t", "--native-tools",
        action="store_true",
        help="Use native Ollama tool-calling API (more reliable with Qwen3)"
    )

    args = parser.parse_args()

    # Check if Ollama is available
    if OLLAMA_AVAILABLE:
        client = OllamaClient()
        if not client.is_available():
            print("❌ Error: Ollama service is not running")
            print("Start it with: ollama serve")
            sys.exit(1)
    else:
        print("❌ Error: Ollama client not available")
        sys.exit(1)

    # Use native tool-calling agent if requested
    if args.native_tools:
        if not TOOL_AGENT_AVAILABLE:
            print("❌ Error: Native tool agent not available")
            print("Make sure tools/tool_agent.py exists")
            sys.exit(1)

        print("🔧 Using native Ollama tool-calling mode")
        agent = ToolAgent(model=args.model)

        if args.interactive or not args.prompt:
            agent.interactive()
        else:
            prompt = " ".join(args.prompt)
            response = agent.chat(prompt)
            if response:
                print(f"\n{response}")
        return

    # Create standard agent (text-parsing mode)
    agent = AIAgent(
        model=args.model,
        beast_mode=args.beast_mode,
        allow_execution=not args.no_execute,
        interactive_confirm=not (args.auto_execute or args.beast_mode)
    )

    # Interactive or single-shot mode
    if args.interactive or not args.prompt:
        agent.interactive()
    else:
        # Single shot
        prompt = " ".join(args.prompt)
        response, results = agent.chat(prompt)

        if results:
            success_count = sum(1 for r in results if r.success)
            print(f"\n📊 {success_count}/{len(results)} commands succeeded")


if __name__ == "__main__":
    main()
