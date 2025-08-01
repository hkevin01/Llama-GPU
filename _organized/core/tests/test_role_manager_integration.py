import unittest
from src.utils.role_manager import RoleManager

class TestRoleManagerIntegration(unittest.TestCase):
    def setUp(self):
        self.rm = RoleManager()
        self.rm.add_user('alice', 'alicepass', 'user')
        self.rm.add_user('bob', 'bobpass', 'admin')

    def test_user_lifecycle(self):
        self.assertTrue(self.rm.authenticate('alice', 'alicepass'))
        self.assertEqual(self.rm.get_role('alice'), 'user')
        self.rm.change_role('alice', 'admin')
        self.assertEqual(self.rm.get_role('alice'), 'admin')
        self.rm.set_password('alice', 'newpass')
        self.assertTrue(self.rm.authenticate('alice', 'newpass'))
        info = self.rm.get_user_info('alice')
        self.assertEqual(info['role'], 'admin')
        self.rm.remove_user('alice')
        self.assertFalse(self.rm.authenticate('alice', 'newpass'))

    def test_find_users_by_role(self):
        admins = self.rm.find_users_by_role('admin')
        self.assertIn('bob', admins)
        self.assertIn('admin', admins)
        users = self.rm.find_users_by_role('user')
        self.assertIn('user', users)

    def test_get_all_permissions(self):
        perms = self.rm.get_all_permissions()
        self.assertIn('admin', perms)
        self.assertIn('user', perms)
        self.assertIn('manage_users', perms['admin'])
        self.assertIn('infer', perms['user'])

if __name__ == '__main__':
    unittest.main()
