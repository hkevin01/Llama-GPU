"""Security tests for tool agent command handlers."""

import unittest
from unittest.mock import patch

from tools.tool_agent import ToolRegistry
import tools.tool_agent as tool_agent_module


class TestToolAgentSecurity(unittest.TestCase):
    def setUp(self):
        self.registry = ToolRegistry()

    def test_run_command_blocks_privileged(self):
        result = self.registry._handle_run_command({"command": "sudo apt update"})
        self.assertIn("privileged", result.lower())
        self.assertIn("run_privileged_command", result)

    def test_run_command_blocks_harmful_rm(self):
        result = self.registry._handle_run_command({"command": "rm -rf /tmp/demo"})
        self.assertIn("error", result.lower())
        self.assertIn("blocked", result.lower())

    def test_privileged_command_requires_explicit_approval(self):
        result = self.registry._handle_run_privileged_command(
            {"command": "sudo apt update", "approved_action": False}
        )
        self.assertIn("denied", result.lower())

    @unittest.skipIf(
        tool_agent_module.SudoExecutor is None,
        "pexpect/sudo executor unavailable in test environment",
    )
    @patch("tools.tool_agent.SudoExecutor.execute")
    def test_privileged_command_executes_when_approved(self, mock_execute):
        class MockResult:
            command = "sudo apt update"
            success = True
            output = "ok"
            error = ""
            exit_code = 0

        mock_execute.return_value = MockResult()

        result = self.registry._handle_run_privileged_command(
            {"command": "sudo apt update", "approved_action": True}
        )
        self.assertEqual(result, "ok")


if __name__ == "__main__":
    unittest.main()
