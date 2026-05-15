#!/usr/bin/env python3
"""
Tool-Calling Agent for Qwen3
Uses native Ollama tool-calling API for reliable command execution on Ubuntu.
"""

import sys
import os
import subprocess
import json
import shlex
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, "/home/kevin/Projects/Llama-GPU")

from src.backends.ollama import OllamaClient
from tools.execution.command_policy import CommandSecurityPolicy

try:
    from tools.execution.sudo_executor import SudoExecutor
except ImportError:
    SudoExecutor = None


@dataclass
class ToolResult:
    """Result from executing a tool."""
    tool_name: str
    arguments: Dict[str, Any]
    result: str
    success: bool
    error: Optional[str] = None


class ToolRegistry:
    """Registry of available tools for the agent."""

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}

        # Register built-in tools
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in Ubuntu command tools."""

        # Run shell command tool
        self.register(
            name="run_command",
            description=(
                "Execute a non-privileged shell command on the Ubuntu system. "
                "This tool blocks harmful commands and does not allow privileged "
                "(root/sudo) operations."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute (e.g., 'ls -la', 'cat file.txt', 'python3 script.py')"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Optional working directory for the command (defaults to current directory)"
                    }
                },
                "required": ["command"]
            },
            handler=self._handle_run_command
        )

        self.register(
            name="run_privileged_command",
            description=(
                "Execute a privileged/root command only after explicit approval. "
                "Use this tool for commands that require sudo (apt, systemctl, etc.)."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The privileged command to execute"
                    },
                    "approved_action": {
                        "type": "boolean",
                        "description": "Must be true to authorize privileged execution"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Short explanation of why privileged execution is needed"
                    }
                },
                "required": ["command", "approved_action"]
            },
            handler=self._handle_run_privileged_command
        )

        # Read file tool
        self.register(
            name="read_file",
            description="Read the contents of a file from the filesystem.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            },
            handler=self._handle_read_file
        )

        # Write file tool
        self.register(
            name="write_file",
            description="Write content to a file on the filesystem.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            },
            handler=self._handle_write_file
        )

        # List directory tool
        self.register(
            name="list_directory",
            description="List the contents of a directory.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory to list (defaults to current directory)"
                    }
                },
                "required": []
            },
            handler=self._handle_list_directory
        )

    def register(self, name: str, description: str, parameters: Dict, handler: Callable):
        """Register a tool."""
        self.tools[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self.handlers[name] = handler

    def get_tool_definitions(self) -> List[Dict]:
        """Get tool definitions for Ollama API."""
        return list(self.tools.values())

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Execute a tool by name."""
        if tool_name not in self.handlers:
            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                result="",
                success=False,
                error=f"Unknown tool: {tool_name}"
            )

        try:
            handler = self.handlers[tool_name]
            result = handler(arguments)
            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                success=True
            )
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                result="",
                success=False,
                error=str(e)
            )

    # Built-in handlers

    def _handle_run_command(self, args: Dict[str, Any]) -> str:
        """Execute a shell command."""
        command = args.get("command", "")
        cwd = args.get("working_directory", os.getcwd())

        decision = CommandSecurityPolicy.evaluate(command)
        if decision.blocked:
            return f"ERROR: {decision.reason}"
        if decision.privileged:
            return (
                "ERROR: Privileged command blocked in run_command. "
                "Use run_privileged_command with approved_action=true."
            )

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=cwd
            )

            output = result.stdout
            if result.stderr:
                output += f"\nSTDERR: {result.stderr}"
            if result.returncode != 0:
                output += f"\n[Exit code: {result.returncode}]"

            return output.strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return "ERROR: Command timed out after 30 seconds"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _handle_run_privileged_command(self, args: Dict[str, Any]) -> str:
        """Execute a privileged command with explicit approval enforcement."""
        command = args.get("command", "")
        approved_action = bool(args.get("approved_action", False))

        if not approved_action:
            return (
                "ERROR: Privileged command denied. "
                "Set approved_action=true only after explicit user approval."
            )

        decision = CommandSecurityPolicy.evaluate(command)
        if decision.blocked:
            return f"ERROR: {decision.reason}"
        if not decision.privileged:
            return (
                "ERROR: Command is not privileged. "
                "Use run_command for non-privileged commands."
            )

        if SudoExecutor is None:
            return (
                "ERROR: Privileged execution is unavailable. "
                "Install pexpect to enable sudo command handling."
            )

        executor = SudoExecutor(cache_password=True)
        result = executor.execute(command, confirm=False)

        if result.success:
            return result.output.strip() or "(no output)"
        return f"ERROR: {result.error or f'Exit code: {result.exit_code}'}"

    def _handle_read_file(self, args: Dict[str, Any]) -> str:
        """Read a file."""
        path = args.get("path", "")
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _handle_write_file(self, args: Dict[str, Any]) -> str:
        """Write to a file."""
        path = args.get("path", "")
        content = args.get("content", "")
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def _handle_list_directory(self, args: Dict[str, Any]) -> str:
        """List directory contents."""
        path = args.get("path", ".")
        try:
            items = os.listdir(path)
            return "\n".join(sorted(items))
        except Exception as e:
            return f"ERROR: {str(e)}"


class ToolAgent:
    """AI Agent with native Ollama tool-calling support."""

    SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools for executing commands on Ubuntu Linux.

When the user asks you to perform actions on the system (list files, run commands, read/write files),
USE THE APPROPRIATE TOOL instead of just explaining what command to run.

Available tools:
- run_command: Execute non-privileged shell commands (safe path)
- run_privileged_command: Execute privileged/root commands with explicit approval
- read_file: Read file contents
- write_file: Write content to files
- list_directory: List directory contents

IMPORTANT:
- When asked to list files, USE list_directory or run_command with 'ls'
- When asked to read a file, USE read_file
- When asked to run normal commands, USE run_command
- When a command requires root access, use run_privileged_command only after explicit user approval
- Always use tools for actions, don't just explain

Current working directory: {cwd}
"""

    def __init__(self, model: str = "qwen3:4b", max_tool_calls: int = 10):
        """Initialize the tool agent.

        Args:
            model: Ollama model to use (must support tools)
            max_tool_calls: Maximum number of tool calls per conversation turn
        """
        self.model = model
        self.max_tool_calls = max_tool_calls
        self.ollama = OllamaClient()
        self.tools = ToolRegistry()
        self.conversation_history: List[Dict[str, Any]] = []

        # Initialize with system prompt
        cwd = os.getcwd()
        self.conversation_history.append({
            "role": "system",
            "content": self.SYSTEM_PROMPT.format(cwd=cwd)
        })

    def chat(self, user_message: str) -> str:
        """Send a message and process tool calls.

        Args:
            user_message: The user's message

        Returns:
            The assistant's final response
        """
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        tool_call_count = 0
        final_response = ""

        while tool_call_count < self.max_tool_calls:
            # Call Ollama with tools
            response = self.ollama.chat(
                model=self.model,
                messages=self.conversation_history,
                tools=self.tools.get_tool_definitions(),
                stream=False,
                temperature=0.3  # Lower temperature for more reliable tool use
            )

            # Extract response components
            content = response.get("content", "")
            tool_calls = response.get("tool_calls", [])

            # If no tool calls, we're done
            if not tool_calls:
                final_response = content
                if content:
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": content
                    })
                break

            # Process tool calls
            print(f"\n🔧 Processing {len(tool_calls)} tool call(s)...")

            # Add assistant message with tool calls to history
            self.conversation_history.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls
            })

            # Execute each tool and add results
            for tool_call in tool_calls:
                func = tool_call.get("function", {})
                tool_name = func.get("name", "")
                arguments = func.get("arguments", {})

                print(f"  → {tool_name}({json.dumps(arguments)})")

                # Execute tool
                result = self.tools.execute(tool_name, arguments)

                if result.success:
                    print(f"  ✅ Success: {result.result[:100]}...")
                else:
                    print(f"  ❌ Error: {result.error}")

                # Add tool result to conversation
                self.conversation_history.append({
                    "role": "tool",
                    "content": result.result if result.success else f"Error: {result.error}",
                    "tool_name": tool_name
                })

                tool_call_count += 1

        return final_response

    def interactive(self):
        """Start an interactive session."""
        print(f"\n🤖 Tool Agent - Interactive Session")
        print("=" * 60)
        print(f"Model: {self.model}")
        print(f"Tools: {', '.join(self.tools.tools.keys())}")
        print("\nCommands: /quit, /clear, /tools")
        print("=" * 60)

        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                if user_input == "/quit":
                    print("👋 Goodbye!")
                    break
                elif user_input == "/clear":
                    self.conversation_history = [self.conversation_history[0]]
                    print("✅ Conversation cleared")
                    continue
                elif user_input == "/tools":
                    print("\n📦 Available Tools:")
                    for name, tool in self.tools.tools.items():
                        desc = tool["function"]["description"][:60]
                        print(f"  • {name}: {desc}...")
                    continue

                # Get response
                response = self.chat(user_input)

                if response:
                    print(f"\n🤖 {response}")
                else:
                    print("\n🤖 (Tool execution complete)")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tool-Calling Agent for Qwen3")
    parser.add_argument("-m", "--model", default="qwen3:4b", help="Ollama model")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("prompt", nargs="*", help="Single prompt (or interactive if empty)")

    args = parser.parse_args()

    # Check Ollama availability
    client = OllamaClient()
    if not client.is_available():
        print("❌ Error: Ollama is not running. Start with: ollama serve")
        sys.exit(1)

    agent = ToolAgent(model=args.model)

    if args.prompt:
        # Single-shot mode
        prompt = " ".join(args.prompt)

        if args.verbose:
            print(f"🤖 Prompt: {prompt}")

        response = agent.chat(prompt)

        if response:
            print(f"\n{response}")
        else:
            # If no text response, show the last tool result
            for msg in reversed(agent.conversation_history):
                if msg.get("role") == "tool":
                    print(f"\n📋 Tool output:\n{msg.get('content', '')}")
                    break
            else:
                print("\n(No response generated)")

        sys.stdout.flush()
    else:
        # Interactive mode
        agent.interactive()


if __name__ == "__main__":
    main()
