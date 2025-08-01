"""
Unit tests for RoleManager
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.role_manager.role_manager import RoleManager


class TestRoleManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.role_manager = RoleManager()
    
    def test_add_user(self):
        """Test adding a new user"""
        self.role_manager.add_user("test_user", ["admin"])
        self.assertIn("test_user", self.role_manager.users)
        self.assertEqual(self.role_manager.users["test_user"]["roles"], ["admin"])
    
    def test_assign_role(self):
        """Test assigning a role to an existing user"""
        self.role_manager.add_user("test_user", [])
        self.role_manager.assign_role("test_user", "editor")
        self.assertIn("editor", self.role_manager.users["test_user"]["roles"])
    
    def test_remove_user(self):
        """Test removing a user"""
        self.role_manager.add_user("test_user", ["admin"])
        self.role_manager.remove_user("test_user")
        self.assertNotIn("test_user", self.role_manager.users)
    
    def test_check_permission(self):
        """Test permission checking"""
        # Add role with permissions
        self.role_manager.add_role("admin", ["read", "write", "delete"])
        self.role_manager.add_user("admin_user", ["admin"])
        
        # Test permission check
        self.assertTrue(self.role_manager.check_permission("admin_user", "read"))
        self.assertTrue(self.role_manager.check_permission("admin_user", "write"))
        self.assertFalse(self.role_manager.check_permission("admin_user", "invalid"))
    
    def test_audit_log(self):
        """Test audit logging functionality"""
        initial_log_count = len(self.role_manager.get_audit_log())
        
        self.role_manager.add_user("test_user", ["admin"])
        self.role_manager.assign_role("test_user", "editor")
        
        # Should have 2 new log entries
        final_log_count = len(self.role_manager.get_audit_log())
        self.assertEqual(final_log_count, initial_log_count + 2)
        
        # Check log content
        logs = self.role_manager.get_audit_log()
        self.assertEqual(logs[-2]["action"], "add_user")
        self.assertEqual(logs[-1]["action"], "assign_role")


if __name__ == '__main__':
    unittest.main()
