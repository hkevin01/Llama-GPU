#!/usr/bin/env python3
"""Shared command security policy for tool and executor modules."""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class PolicyDecision:
    """Result of evaluating a command string against policy."""

    blocked: bool
    privileged: bool
    reason: str = ""


class CommandSecurityPolicy:
    """Policy helper to classify and block dangerous shell commands."""

    # Block harmful command families globally.
    BLOCKED_BASE_COMMANDS = {
        "rm",
        "mkfs",
        "dd",
        "fdisk",
        "parted",
        "shutdown",
        "reboot",
        "poweroff",
    }

    BLOCKED_PATTERNS = [
        "rm -rf /",
        "rm -rf /*",
        "dd if=/dev/zero",
        "mkfs",
        ":(){ :|:& };:",
        "chmod -r 777 /",
        "chmod -R 777 /",
        "chown -r root /",
        "chown -R root /",
        "| sh",
        "| bash",
        "> /dev/sda",
        "> /dev/nvme",
    ]

    PRIVILEGED_COMMANDS = {
        "sudo",
        "apt",
        "apt-get",
        "systemctl",
        "service",
        "mount",
        "umount",
        "passwd",
        "useradd",
        "userdel",
        "usermod",
        "ufw",
        "iptables",
        "visudo",
    }

    @staticmethod
    def _tokens(command: str) -> List[str]:
        try:
            return shlex.split(command)
        except ValueError:
            return command.strip().split()

    @classmethod
    def evaluate(cls, command: str) -> PolicyDecision:
        """Evaluate a command string and classify it as blocked/privileged."""
        normalized = command.strip().lower()
        if not normalized:
            return PolicyDecision(blocked=True, privileged=False, reason="Empty command")

        for pattern in cls.BLOCKED_PATTERNS:
            if pattern.lower() in normalized:
                return PolicyDecision(
                    blocked=True,
                    privileged=False,
                    reason=f"Blocked harmful pattern: {pattern}",
                )

        tokens = cls._tokens(command)
        if not tokens:
            return PolicyDecision(blocked=True, privileged=False, reason="Empty command")

        base = tokens[0].lower()
        if base in cls.BLOCKED_BASE_COMMANDS:
            return PolicyDecision(
                blocked=True,
                privileged=False,
                reason=f"Blocked harmful command: {base}",
            )

        privileged = base in cls.PRIVILEGED_COMMANDS
        return PolicyDecision(blocked=False, privileged=privileged)
