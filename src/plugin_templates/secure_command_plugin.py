"""Secure command policy plugin template."""

from tools.execution.command_policy import CommandSecurityPolicy


class SecureCommandPlugin:
    """Plugin that evaluates command safety and privilege requirements."""

    metadata = {
        "name": "secure_command_plugin",
        "version": "1.0.0",
        "description": "Evaluates shell commands for blocked patterns and privilege needs",
    }

    def initialize(self):
        """Initialize plugin state."""
        return True

    def run(self, command: str):
        """Return security decision for a command string."""
        decision = CommandSecurityPolicy.evaluate(command)
        return {
            "command": command,
            "blocked": decision.blocked,
            "privileged": decision.privileged,
            "reason": decision.reason,
        }
