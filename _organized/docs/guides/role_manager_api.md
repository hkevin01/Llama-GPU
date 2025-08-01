# RoleManager API Documentation

## Overview
The `RoleManager` class provides user, role, and permission management for authorization.

## Methods
- `get_role(username: str) -> str`: Get user's role.
- `has_permission(username: str, action: str) -> bool`: Check if user can perform action.
- `authenticate(username: str, password: str) -> bool`: Validate credentials.
- `add_user(username: str, password: str, role: str = 'user') -> None`: Add user.
- `remove_user(username: str) -> None`: Remove user.
- `change_role(username: str, role: str) -> None`: Change user's role.
- `list_users() -> Dict[str, str]`: List all users and roles.
- `set_password(username: str, password: str) -> None`: Set/update password.
- `check_permission(username: str) -> Dict[str, list]`: Get all permissions for user's role.
- `get_user_info(username: str) -> Dict[str, str]`: Get info for a user.
- `update_user(username: str, password: Optional[str], role: Optional[str]) -> None`: Update password/role.
- `find_users_by_role(role: str) -> Dict[str, str]`: Find users by role.
- `get_all_permissions() -> Dict[str, list]`: Get all roles and permissions.

## Usage
Import and instantiate `RoleManager` in backend, dashboard, or admin modules for secure access control and user management.
