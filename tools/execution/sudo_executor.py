#!/usr/bin/env python3
"""
Sudo-Enabled Command Executor
Handles sudo commands with password prompting using pexpect.
"""

import os
import sys
import subprocess
import getpass
import pexpect
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class SudoResult:
    """Result of sudo command execution."""
    command: str
    success: bool
    output: str
    error: str
    exit_code: int


class SudoExecutor:
    """Execute commands including sudo with password handling."""

    # Extremely dangerous commands - always block these
    NEVER_ALLOW = [
        'rm -rf /',
        'rm -rf /*',
        'dd if=/dev/zero',
        'mkfs',
        ':(){ :|:& };:',  # Fork bomb
        'chmod -R 777 /',
        'chown -R root /',
    ]

    # High-risk commands that need extra confirmation
    HIGH_RISK = [
        'rm -rf',
        'dd ',
        'fdisk',
        'parted',
        'mkfs',
        'format',
    ]

    def __init__(self,
                 password: Optional[str] = None,
                 cache_password: bool = True,
                 timeout: int = 300):
        """Initialize sudo executor.

        Args:
            password: Sudo password (will prompt if not provided)
            cache_password: Cache password for session
            timeout: Command timeout in seconds
        """
        self.password = password
        self.cache_password = cache_password
        self.timeout = timeout
        self._cached_password = None

    def is_dangerous(self, command: str) -> bool:
        """Check if command is extremely dangerous."""
        cmd_lower = command.lower().strip()
        return any(dangerous in cmd_lower for dangerous in self.NEVER_ALLOW)

    def is_high_risk(self, command: str) -> bool:
        """Check if command is high risk."""
        cmd_lower = command.lower()
        return any(risk in cmd_lower for risk in self.HIGH_RISK)

    def get_password(self, prompt: str = "Enter sudo password: ") -> str:
        """Get sudo password (from cache or prompt)."""
        if self.cache_password and self._cached_password:
            return self._cached_password

        if self.password:
            if self.cache_password:
                self._cached_password = self.password
            return self.password

        # Prompt for password
        password = getpass.getpass(prompt)
        if self.cache_password:
            self._cached_password = password
        return password

    def verify_sudo_access(self) -> bool:
        """Verify user has sudo access with current password."""
        try:
            password = self.get_password()

            # Use sudo -S (read password from stdin) with echo command
            child = pexpect.spawn('sudo -S echo "sudo access verified"', timeout=10)

            # Send password immediately (sudo -S reads from stdin)
            child.sendline(password)

            # Wait for completion or error
            index = child.expect(['sudo access verified', 'Sorry', pexpect.EOF, pexpect.TIMEOUT])
            output = child.before if hasattr(child, 'before') else b''
            child.close()

            # Check if successful (index 0 means our success message appeared)
            if index == 0:
                return True
            elif index == 1:
                print("❌ Incorrect password")
                self._cached_password = None  # Clear bad password
                return False
            else:
                return child.exitstatus == 0 if child.exitstatus is not None else False

        except Exception as e:
            print(f"❌ Sudo verification failed: {e}")
            return False

    def execute_sudo(self,
                     command: str,
                     confirm: bool = True,
                     use_sudo: bool = True) -> SudoResult:
        """Execute command with sudo.

        Args:
            command: Command to execute
            confirm: Ask for confirmation
            use_sudo: Prepend sudo if not present

        Returns:
            SudoResult with execution details
        """
        # Remove leading/trailing whitespace
        command = command.strip()

        # Check if already has sudo
        has_sudo = command.startswith('sudo ')

        # Add sudo if needed
        if use_sudo and not has_sudo:
            command = f'sudo {command}'

        # Safety checks
        if self.is_dangerous(command):
            return SudoResult(
                command=command,
                success=False,
                output="",
                error="❌ BLOCKED: Extremely dangerous command detected!",
                exit_code=-1
            )

        # High risk warning
        if self.is_high_risk(command):
            print(f"\n⚠️  HIGH RISK COMMAND DETECTED")
            print(f"   Command: {command}")
            print(f"   This could damage your system!")

            if confirm:
                response = input("   Type 'YES I UNDERSTAND' to continue: ")
                if response != "YES I UNDERSTAND":
                    return SudoResult(
                        command=command,
                        success=False,
                        output="",
                        error="❌ User cancelled high-risk operation",
                        exit_code=-1
                    )

        # Regular confirmation
        elif confirm:
            print(f"\n🔐 Sudo command:")
            print(f"   {command}")
            response = input("   Execute? (yes/no): ").lower()
            if response not in ['yes', 'y']:
                return SudoResult(
                    command=command,
                    success=False,
                    output="",
                    error="❌ User cancelled execution",
                    exit_code=-1
                )

        # Get password
        try:
            password = self.get_password()
        except KeyboardInterrupt:
            return SudoResult(
                command=command,
                success=False,
                output="",
                error="❌ Password entry cancelled",
                exit_code=-1
            )

        # Execute with pexpect
        print(f"🔧 Executing: {command}")

        try:
            # Ensure command uses sudo -S for stdin password
            if command.startswith('sudo ') and '-S' not in command:
                command = command.replace('sudo ', 'sudo -S ', 1)

            # Spawn the command
            child = pexpect.spawn(command, timeout=self.timeout)

            # Send password immediately (sudo -S reads from stdin)
            child.sendline(password)

            # Collect output
            output = []
            while True:
                try:
                    index = child.expect(['\r\n', '\n', pexpect.EOF, pexpect.TIMEOUT], timeout=1)
                    if index in [0, 1]:
                        line = child.before.decode('utf-8', errors='replace')
                        if line and not line.startswith('[sudo]'):  # Skip password prompt line
                            output.append(line + '\n')
                            print(line)
                    elif index == 2:  # EOF
                        # Get any remaining output
                        remaining = child.before.decode('utf-8', errors='replace')
                        if remaining and not remaining.startswith('[sudo]'):
                            output.append(remaining)
                            print(remaining, end='')
                        break
                    else:  # TIMEOUT
                        continue
                except pexpect.TIMEOUT:
                    break
                except pexpect.EOF:
                    break
                except Exception as e:
                    print(f"⚠️  Read error: {e}")
                    break

            # Wait for completion
            child.close()

            exit_code = child.exitstatus if child.exitstatus is not None else -1
            output_str = ''.join(output)

            success = exit_code == 0

            if success:
                print(f"✅ Command completed successfully (exit {exit_code})")
            else:
                print(f"❌ Command failed (exit {exit_code})")

            return SudoResult(
                command=command,
                success=success,
                output=output_str,
                error="" if success else f"Exit code: {exit_code}",
                exit_code=exit_code
            )

        except pexpect.TIMEOUT:
            return SudoResult(
                command=command,
                success=False,
                output="",
                error=f"❌ Command timed out after {self.timeout}s",
                exit_code=-1
            )
        except Exception as e:
            return SudoResult(
                command=command,
                success=False,
                output="",
                error=f"❌ Execution error: {str(e)}",
                exit_code=-1
            )

    def execute(self, command: str, confirm: bool = True) -> SudoResult:
        """Execute command (with or without sudo as needed).

        Args:
            command: Command to execute
            confirm: Ask for confirmation for sudo commands

        Returns:
            SudoResult with execution details
        """
        # Check if command needs sudo
        needs_sudo = command.strip().startswith('sudo ') or any(
            command.strip().startswith(cmd) for cmd in [
                'apt', 'apt-get', 'systemctl', 'service',
                'useradd', 'userdel', 'usermod', 'passwd',
                'mount', 'umount', 'fdisk', 'parted'
            ]
        )

        if needs_sudo:
            return self.execute_sudo(command, confirm=confirm, use_sudo=True)
        else:
            # Execute as regular command
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                return SudoResult(
                    command=command,
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr,
                    exit_code=result.returncode
                )
            except Exception as e:
                return SudoResult(
                    command=command,
                    success=False,
                    output="",
                    error=str(e),
                    exit_code=-1
                )


def main():
    """Test sudo executor."""
    import argparse

    parser = argparse.ArgumentParser(description="Sudo Command Executor")
    parser.add_argument("command", nargs="+", help="Command to execute")
    parser.add_argument("--no-confirm", action="store_true", help="Skip confirmation")
    parser.add_argument("--password", help="Sudo password")

    args = parser.parse_args()
    command = " ".join(args.command)

    executor = SudoExecutor(password=args.password)

    # Verify sudo access first
    print("🔐 Verifying sudo access...")
    if not executor.verify_sudo_access():
        print("❌ Sudo verification failed. Check your password.")
        sys.exit(1)

    print("✅ Sudo access verified\n")

    # Execute command
    result = executor.execute(command, confirm=not args.no_confirm)

    print(f"\n{'='*60}")
    print(f"Command: {result.command}")
    print(f"Success: {'✅' if result.success else '❌'}")
    print(f"Exit Code: {result.exit_code}")
    if result.output:
        print(f"\nOutput:\n{result.output}")
    if result.error:
        print(f"\nError:\n{result.error}")
    print(f"{'='*60}")

    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
