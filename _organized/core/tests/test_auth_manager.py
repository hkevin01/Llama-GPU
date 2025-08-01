import unittest
from src.auth_manager import AuthManager

class TestAuthManager(unittest.TestCase):
    def setUp(self):
        self.auth = AuthManager()

    def test_authenticate_success(self):
        self.assertTrue(self.auth.authenticate('admin', 'adminpass'))

    def test_authenticate_failure(self):
        self.assertFalse(self.auth.authenticate('admin', 'wrongpass'))

    def test_add_user_and_role(self):
        self.auth.add_user('user1', 'pass1', 'editor')
        self.assertTrue(self.auth.authenticate('user1', 'pass1'))
        self.assertEqual(self.auth.get_role('user1'), 'editor')

if __name__ == '__main__':
    unittest.main()
