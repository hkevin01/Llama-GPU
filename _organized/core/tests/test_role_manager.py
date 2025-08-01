import unittest
from src.utils.role_manager import RoleManager

class TestRoleManager(unittest.TestCase):
    def setUp(self):
        self.rm = RoleManager()

    def test_authenticate(self):
        self.assertTrue(self.rm.authenticate('admin', 'adminpass'))
        self.assertFalse(self.rm.authenticate('admin', 'wrongpass'))

    def test_add_and_remove_user(self):
        self.rm.add_user('testuser', 'testpass', 'user')
        self.assertTrue(self.rm.authenticate('testuser', 'testpass'))
        self.rm.remove_user('testuser')
        self.assertFalse(self.rm.authenticate('testuser', 'testpass'))

    def test_change_role(self):
        self.rm.add_user('testuser', 'testpass', 'user')
        self.rm.change_role('testuser', 'admin')
        self.assertEqual(self.rm.get_role('testuser'), 'admin')

    def test_list_users(self):
        users = self.rm.list_users()
        self.assertIn('admin', users)
        self.assertIn('user', users)

    def test_set_password(self):
        self.rm.set_password('admin', 'newpass')
        self.assertTrue(self.rm.authenticate('admin', 'newpass'))

    def test_check_permission(self):
        perms = self.rm.check_permission('admin')
        self.assertIn('infer', perms['admin'])
        self.assertIn('manage_users', perms['admin'])

if __name__ == '__main__':
    unittest.main()
