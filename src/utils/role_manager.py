"""
Role Management Utility
Handles user roles, permissions, and user management for authorization.
"""

from typing import Dict, Optional

class RoleManager:
    """
    Manages user roles, permissions, and basic user management.
    Passwords are stored in-memory for demonstration purposes only.
    """
    def __init__(self):
        self.roles: Dict[str, str] = {'admin': 'admin', 'user': 'user'}
        self.passwords: Dict[str, str] = {'admin': 'adminpass', 'user': 'userpass'}
        self.permissions: Dict[str, list] = {
            'admin': ['infer', 'load_model', 'manage_plugins', 'manage_users'],
            'user': ['infer']
        }

    def get_role(self, username: str) -> str:
        """Return the role for a given user."""
        return self.roles.get(username, 'user')

    def has_permission(self, username: str, action: str) -> bool:
        """Check if user has permission for an action."""
        role = self.get_role(username)
        return action in self.permissions.get(role, [])

    def authenticate(self, username: str, password: str) -> bool:
        """Validate user credentials."""
        return self.passwords.get(username) == password

    def add_user(self, username: str, password: str, role: str = 'user') -> None:
        """Add a new user with role and password."""
        self.roles[username] = role
        self.passwords[username] = password

    def remove_user(self, username: str) -> None:
        """Remove a user from the system."""
        self.roles.pop(username, None)
        self.passwords.pop(username, None)

    def change_role(self, username: str, role: str) -> None:
        """Change the role of an existing user."""
        if username in self.roles:
            self.roles[username] = role

    def list_users(self) -> Dict[str, str]:
        """Return a dictionary of all users and their roles."""
        return self.roles.copy()

    def set_password(self, username: str, password: str) -> None:
        """Set or update a user's password."""
        if username in self.roles:
            self.passwords[username] = password

    def check_permission(self, username: str) -> Dict[str, list]:
        """Return all permissions for a user's role."""
        role = self.get_role(username)
        return {role: self.permissions.get(role, [])}

    def get_user_info(self, username: str) -> Dict[str, str]:
        """Return info for a specific user (role, password)."""
        return {
            'username': username,
            'role': self.get_role(username),
            'password': self.passwords.get(username, '')
        }

    def update_user(self, username: str, password: Optional[str] = None, role: Optional[str] = None) -> None:
        """Update user's password and/or role."""
        if username in self.roles:
            if password is not None:
                self.passwords[username] = password
            if role is not None:
                self.roles[username] = role

    def find_users_by_role(self, role: str) -> Dict[str, str]:
        """Return all users with a specific role."""
        return {user: r for user, r in self.roles.items() if r == role}

    def get_all_permissions(self) -> Dict[str, list]:
        """Return all defined roles and their permissions."""
        return self.permissions.copy()
