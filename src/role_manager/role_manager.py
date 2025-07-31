"""
Role Manager Module
Handles user/role management, access control, and audit logging.
"""

import logging
from typing import Dict, List, Optional

logging.basicConfig(filename='logs/role_manager.log', level=logging.INFO)


class RoleManager:
    """
    Manages users, roles, permissions, and audit logs.
    """
    def __init__(self) -> None:
        self.users: Dict[str, Dict] = {}
        self.roles: Dict[str, List[str]] = {}
        self.audit_log: List[Dict] = []

    def add_user(self, username: str, 
                 roles: Optional[List[str]] = None) -> None:
        self.users[username] = {'roles': roles or []}
        logging.info('User added: %s', username)
        self._log_action('add_user', username)

    def assign_role(self, username: str, role: str) -> None:
        if username in self.users:
            self.users[username]['roles'].append(role)
            logging.info('Role %s assigned to %s', role, username)
            self._log_action('assign_role', username, role)

    def remove_user(self, username: str) -> None:
        if username in self.users:
            del self.users[username]
            logging.info('User removed: %s', username)
            self._log_action('remove_user', username)

    def check_permission(self, username: str, permission: str) -> bool:
        roles = self.users.get(username, {}).get('roles', [])
        for role in roles:
            if permission in self.roles.get(role, []):
                return True
        return False

    def add_role(self, role: str, permissions: List[str]) -> None:
        self.roles[role] = permissions
        logging.info('Role added: %s', role)
        self._log_action('add_role', role)

    def _log_action(self, action: str, username: str, 
                    role: Optional[str] = None) -> None:
        entry = {'action': action, 'username': username, 'role': role}
        self.audit_log.append(entry)

    def get_audit_log(self) -> List[Dict]:
        return self.audit_log
