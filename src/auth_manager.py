"""
Authentication and Role-Based Access Control Module
Provides user login, token validation, and role management.
"""

import logging
logging.basicConfig(filename='logs/auth_manager.log', level=logging.INFO)

class AuthManager:
    def __init__(self):
        self.users = {'admin': 'adminpass'}
        self.roles = {'admin': 'admin'}

    def authenticate(self, username, password):
        if self.users.get(username) == password:
            logging.info('User %s authenticated', username)
            return True
        logging.warning('Failed authentication for user %s', username)
        return False

    def get_role(self, username):
        return self.roles.get(username, 'user')

    def add_user(self, username, password, role='user'):
        self.users[username] = password
        self.roles[username] = role
        logging.info('User %s added with role %s', username, role)
