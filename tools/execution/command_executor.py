#!/usr/bin/env python3
"""
AI-Powered Terminal Command Executor
Allows AI to suggest and execute terminal commands with safety checks.
"""

import subprocess
import os
import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CommandResult:
    """Result of command execution."""
    command: str
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float


class SafeCommandExecutor:
    """Execute terminal commands with safety checks."""
    
    # Commands that require explicit confirmation
    DANGEROUS_COMMANDS = [
        'rm -rf /',
        'dd ',
        'mkfs',
        ':(){ :|:& };:',  # Fork bomb
        'chmod -R 777 /',
        'chown -R',
    ]
    
    # Commands that require root/sudo
    ROOT_COMMANDS = [
        'apt',
        'apt-get',
        'systemctl',
        'service',
        'useradd',
        'userdel',
        'passwd',
        'mount',
        'umount',
        'fdisk',
        'parted',
    ]
    
    # Safe commands that can run without confirmation
    SAFE_COMMANDS = [
        'ls', 'pwd', 'whoami', 'date', 'echo', 'cat',
        'grep', 'find', 'which', 'type', 'help',
        'python3', 'node', 'git status', 'git log',
        'df', 'du', 'ps', 'top', 'htop', 'free',
        'uname', 'hostname', 'uptime', 'w',
    ]
    
    def __init__(self, interactive: bool = True, allow_root: bool = False):
        """Initialize executor.
        
        Args:
            interactive: Require user confirmation for dangerous commands
            allow_root: Allow commands that require root privileges
        """
        self.interactive = interactive
        self.allow_root = allow_root
        self.command_history = []
    
    def is_dangerous(self, command: str) -> bool:
        """Check if command is potentially dangerous."""
        command_lower = command.lower()
        return any(dangerous in command_lower for dangerous in self.DANGEROUS_COMMANDS)
    
    def requires_root(self, command: str) -> bool:
        """Check if command requires root privileges."""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
        
        base_cmd = cmd_parts[0]
        
        # Check if starts with sudo
        if base_cmd == 'sudo':
            return True
        
        # Check if command is in root command list
        return any(base_cmd.startswith(root_cmd) for root_cmd in self.ROOT_COMMANDS)
    
    def is_safe(self, command: str) -> bool:
        """Check if command is in the safe list."""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False
        
        base_cmd = cmd_parts[0]
        return any(command.startswith(safe) for safe in self.SAFE_COMMANDS)
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command safety.
        
        Returns:
            (is_valid, reason)
        """
        if not command or not command.strip():
            return False, "Empty command"
        
        if self.is_dangerous(command):
            return False, "Dangerous command detected"
        
        if self.requires_root(command) and not self.allow_root:
            return False, "Command requires root privileges (not allowed)"
        
        return True, "Command is valid"
    
    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 30,
        confirm: bool = None
    ) -> CommandResult:
        """Execute a shell command.
        
        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds
            confirm: Override interactive confirmation
            
        Returns:
            CommandResult object
        """
        import time
        start_time = time.time()
        
        # Validate command
        is_valid, reason = self.validate_command(command)
        
        if not is_valid:
            print(f"❌ Command validation failed: {reason}")
            if not self.interactive or (confirm is False):
                return CommandResult(
                    command=command,
                    success=False,
                    stdout="",
                    stderr=f"Validation failed: {reason}",
                    exit_code=-1,
                    execution_time=0
                )
        
        # Check if we need confirmation
        needs_confirmation = not self.is_safe(command) and self.interactive
        
        if needs_confirmation and confirm is None:
            print(f"\n⚠️  Command requires confirmation:")
            print(f"   {command}")
            response = input("Execute? (yes/no): ").lower()
            if response not in ['yes', 'y']:
                print("❌ Command cancelled")
                return CommandResult(
                    command=command,
                    success=False,
                    stdout="",
                    stderr="User cancelled execution",
                    exit_code=-1,
                    execution_time=0
                )
        
        # Execute command
        print(f"🔧 Executing: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            cmd_result = CommandResult(
                command=command,
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time=execution_time
            )
            
            self.command_history.append(cmd_result)
            
            if cmd_result.success:
                print(f"✅ Command completed in {execution_time:.2f}s")
            else:
                print(f"❌ Command failed with exit code {result.returncode}")
            
            return cmd_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"⏱️  Command timed out after {timeout}s")
            return CommandResult(
                command=command,
                success=False,
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                exit_code=-1,
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Error executing command: {e}")
            return CommandResult(
                command=command,
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=execution_time
            )
    
    def execute_script(self, script: str, interpreter: str = "bash") -> CommandResult:
        """Execute a multi-line script.
        
        Args:
            script: Script content
            interpreter: Script interpreter (bash, python3, etc.)
            
        Returns:
            CommandResult object
        """
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{interpreter}', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            os.chmod(script_path, 0o755)
            result = self.execute(f"{interpreter} {script_path}")
            return result
        finally:
            if os.path.exists(script_path):
                os.unlink(script_path)
    
    def get_history(self) -> List[CommandResult]:
        """Get command execution history."""
        return self.command_history
    
    def print_result(self, result: CommandResult, verbose: bool = True):
        """Print command result in formatted way."""
        print("\n" + "=" * 60)
        print(f"Command: {result.command}")
        print(f"Exit Code: {result.exit_code}")
        print(f"Execution Time: {result.execution_time:.2f}s")
        print(f"Success: {'✅' if result.success else '❌'}")
        
        if result.stdout and verbose:
            print("\nOutput:")
            print(result.stdout)
        
        if result.stderr:
            print("\nErrors:")
            print(result.stderr)
        
        print("=" * 60)


def main():
    """Interactive command executor."""
    print("\n🔧 Safe Command Executor")
    print("=" * 60)
    print("Type commands to execute, or:")
    print("  /help     - Show help")
    print("  /history  - Show command history")
    print("  /quit     - Exit")
    print("=" * 60)
    print()
    
    executor = SafeCommandExecutor(interactive=True, allow_root=False)
    
    while True:
        try:
            command = input("$ ").strip()
            
            if not command:
                continue
            
            if command == "/quit":
                print("👋 Goodbye!")
                break
            elif command == "/help":
                print("\nAvailable commands:")
                print("  /help     - Show this help")
                print("  /history  - Show command history")
                print("  /quit     - Exit")
                print("\nSafe commands can run without confirmation.")
                print("Dangerous commands will require confirmation.")
                print("Root commands are disabled by default.\n")
                continue
            elif command == "/history":
                history = executor.get_history()
                if not history:
                    print("No command history yet.")
                else:
                    print(f"\n📜 Command History ({len(history)} commands):")
                    for i, cmd in enumerate(history, 1):
                        status = "✅" if cmd.success else "❌"
                        print(f"  {i}. {status} {cmd.command} ({cmd.exit_code})")
                print()
                continue
            
            result = executor.execute(command)
            executor.print_result(result)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
