"""Unit tests for command security policy."""

import unittest

from tools.execution.command_policy import CommandSecurityPolicy


class TestCommandSecurityPolicy(unittest.TestCase):
    def test_blocks_rm(self):
        decision = CommandSecurityPolicy.evaluate("rm -rf /tmp/test")
        self.assertTrue(decision.blocked)
        self.assertIn("blocked", decision.reason.lower())

    def test_blocks_known_harmful_pattern(self):
        decision = CommandSecurityPolicy.evaluate("echo x | sh")
        self.assertTrue(decision.blocked)

    def test_marks_sudo_as_privileged(self):
        decision = CommandSecurityPolicy.evaluate("sudo apt update")
        self.assertFalse(decision.blocked)
        self.assertTrue(decision.privileged)

    def test_marks_systemctl_as_privileged(self):
        decision = CommandSecurityPolicy.evaluate("systemctl restart nginx")
        self.assertFalse(decision.blocked)
        self.assertTrue(decision.privileged)

    def test_safe_non_privileged_command(self):
        decision = CommandSecurityPolicy.evaluate("ls -la")
        self.assertFalse(decision.blocked)
        self.assertFalse(decision.privileged)


if __name__ == "__main__":
    unittest.main()
