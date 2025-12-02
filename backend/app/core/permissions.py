"""
Fine-Grained RBAC (Role-Based Access Control) Module

This module provides comprehensive permission management including:
- Resource-level permissions
- Action-based permissions (create, read, update, delete, approve, export)
- Permission decorators for endpoints
- Dynamic permission checking
- Role hierarchy
- Attribute-Based Access Control (ABAC) support

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Union

from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.role import Role


class Resource(str, Enum):
    """System resources that can be permission-controlled"""
    COURIERS = "couriers"
    VEHICLES = "vehicles"
    WORKFLOWS = "workflows"
    FINANCES = "finances"
    REPORTS = "reports"
    USERS = "users"
    SETTINGS = "settings"
    ANALYTICS = "analytics"
    ROUTES = "routes"
    TICKETS = "tickets"
    OPERATIONS = "operations"
    ORGANIZATIONS = "organizations"
    ROLES = "roles"
    PERMISSIONS = "permissions"
    AUDIT_LOGS = "audit_logs"


class Action(str, Enum):
    """Actions that can be performed on resources"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"
    IMPORT = "import"
    ASSIGN = "assign"
    UNASSIGN = "unassign"
    ARCHIVE = "archive"
    RESTORE = "restore"


class Permission:
    """
    Permission class representing a specific action on a resource

    Format: resource:action (e.g., "couriers:create", "vehicles:read")
    """

    def __init__(self, resource: Union[Resource, str], action: Union[Action, str]):
        self.resource = resource if isinstance(resource, str) else resource.value
        self.action = action if isinstance(action, str) else action.value

    def __str__(self) -> str:
        return f"{self.resource}:{self.action}"

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return str(self) == other
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    @classmethod
    def from_string(cls, permission_str: str) -> "Permission":
        """Parse permission from string format (resource:action)"""
        try:
            resource, action = permission_str.split(":", 1)
            return cls(resource, action)
        except ValueError:
            raise ValueError(f"Invalid permission format: {permission_str}")


class RoleHierarchy:
    """
    Role hierarchy definition

    Higher roles inherit all permissions from lower roles:
    system_admin > organization_admin > manager > supervisor > user > guest
    """

    HIERARCHY = {
        "system_admin": 100,
        "organization_admin": 80,
        "manager": 60,
        "supervisor": 40,
        "user": 20,
        "guest": 10,
    }

    @classmethod
    def get_level(cls, role_name: str) -> int:
        """Get hierarchy level for a role"""
        return cls.HIERARCHY.get(role_name.lower(), 0)

    @classmethod
    def is_higher_or_equal(cls, role1: str, role2: str) -> bool:
        """Check if role1 is higher or equal to role2 in hierarchy"""
        return cls.get_level(role1) >= cls.get_level(role2)

    @classmethod
    def is_higher(cls, role1: str, role2: str) -> bool:
        """Check if role1 is strictly higher than role2"""
        return cls.get_level(role1) > cls.get_level(role2)


class PermissionChecker:
    """
    Permission checking utilities with support for:
    - Direct permission checks
    - Role-based checks
    - Resource ownership checks
    - Tenant isolation
    """

    @staticmethod
    def has_permission(
        user: User,
        required_permission: Union[Permission, str],
        db: Optional[Session] = None
    ) -> bool:
        """
        Check if user has a specific permission

        Args:
            user: User object
            required_permission: Permission to check
            db: Database session (optional, for dynamic permission loading)

        Returns:
            True if user has permission, False otherwise
        """
        if isinstance(required_permission, Permission):
            required_permission = str(required_permission)

        # System admins have all permissions
        if user.role and user.role.name == "system_admin":
            return True

        # Check user's role permissions
        if user.role and user.role.permissions:
            user_permissions = set(user.role.permissions)

            # Direct permission match
            if required_permission in user_permissions:
                return True

            # Check wildcard permissions (e.g., "couriers:*" grants all courier actions)
            resource = required_permission.split(":")[0]
            wildcard = f"{resource}:*"
            if wildcard in user_permissions:
                return True

            # Check global wildcard
            if "*:*" in user_permissions:
                return True

        return False

    @staticmethod
    def has_any_permission(
        user: User,
        required_permissions: List[Union[Permission, str]],
        db: Optional[Session] = None
    ) -> bool:
        """Check if user has any of the required permissions"""
        return any(
            PermissionChecker.has_permission(user, perm, db)
            for perm in required_permissions
        )

    @staticmethod
    def has_all_permissions(
        user: User,
        required_permissions: List[Union[Permission, str]],
        db: Optional[Session] = None
    ) -> bool:
        """Check if user has all required permissions"""
        return all(
            PermissionChecker.has_permission(user, perm, db)
            for perm in required_permissions
        )

    @staticmethod
    def can_access_resource(
        user: User,
        resource_owner_id: int,
        organization_id: Optional[int] = None
    ) -> bool:
        """
        Check if user can access a resource based on ownership and tenant isolation

        Args:
            user: User object
            resource_owner_id: ID of the resource owner
            organization_id: Optional organization ID for tenant isolation

        Returns:
            True if user can access the resource
        """
        # System admins can access everything
        if user.role and user.role.name == "system_admin":
            return True

        # Tenant isolation check
        if organization_id and user.organization_id != organization_id:
            return False

        # Resource ownership or organization admin access
        if user.id == resource_owner_id:
            return True

        if user.role and user.role.name == "organization_admin":
            return user.organization_id is not None

        return False

    @staticmethod
    def enforce_tenant_isolation(user: User, resource_organization_id: int) -> bool:
        """
        Enforce tenant isolation - ensure user can only access their organization's resources

        Args:
            user: User object
            resource_organization_id: Organization ID of the resource

        Returns:
            True if access allowed, False otherwise
        """
        # System admins bypass tenant isolation
        if user.role and user.role.name == "system_admin":
            return True

        # Ensure user belongs to the same organization
        return user.organization_id == resource_organization_id


class PermissionDependency:
    """
    FastAPI dependency for permission checking

    Usage:
        @router.get("/couriers", dependencies=[Depends(require_permission("couriers:read"))])
        async def get_couriers(...):
            ...
    """

    def __init__(self, required_permission: Union[Permission, str, List[Union[Permission, str]]]):
        if isinstance(required_permission, list):
            self.required_permissions = [
                str(p) if isinstance(p, Permission) else p
                for p in required_permission
            ]
            self.mode = "all"  # Require all permissions by default
        else:
            self.required_permissions = [
                str(required_permission) if isinstance(required_permission, Permission) else required_permission
            ]
            self.mode = "all"

    def __call__(self, request: Request, current_user: User = None):
        """Dependency injection - check permissions"""
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )

        # Check permissions
        if self.mode == "all":
            has_access = PermissionChecker.has_all_permissions(
                current_user, self.required_permissions
            )
        else:
            has_access = PermissionChecker.has_any_permission(
                current_user, self.required_permissions
            )

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {', '.join(self.required_permissions)}"
            )

        return current_user


def require_permission(
    permission: Union[Permission, str, List[Union[Permission, str]]],
    mode: str = "all"
) -> PermissionDependency:
    """
    Create permission dependency for route protection

    Args:
        permission: Single permission or list of permissions
        mode: "all" (require all permissions) or "any" (require any permission)

    Returns:
        PermissionDependency instance

    Example:
        @router.delete("/couriers/{id}", dependencies=[Depends(require_permission("couriers:delete"))])
        async def delete_courier(...):
            ...
    """
    dep = PermissionDependency(permission)
    dep.mode = mode
    return dep


def require_role(role_name: str):
    """
    Decorator to require specific role for endpoint access

    Args:
        role_name: Required role name

    Example:
        @require_role("organization_admin")
        async def admin_only_function(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if not current_user.role or current_user.role.name != role_name:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{role_name}' required"
                )

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


def require_role_level(minimum_role: str):
    """
    Decorator to require minimum role level based on hierarchy

    Args:
        minimum_role: Minimum required role (user, supervisor, manager, etc.)

    Example:
        @require_role_level("manager")
        async def manager_and_above(...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            if not current_user.role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User has no role assigned"
                )

            if not RoleHierarchy.is_higher_or_equal(current_user.role.name, minimum_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Minimum role '{minimum_role}' required"
                )

            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


# Pre-defined permission sets for common use cases
class CommonPermissions:
    """Common permission sets for easy reuse"""

    # Courier permissions
    COURIER_READ = Permission(Resource.COURIERS, Action.READ)
    COURIER_CREATE = Permission(Resource.COURIERS, Action.CREATE)
    COURIER_UPDATE = Permission(Resource.COURIERS, Action.UPDATE)
    COURIER_DELETE = Permission(Resource.COURIERS, Action.DELETE)
    COURIER_ASSIGN = Permission(Resource.COURIERS, Action.ASSIGN)

    # Vehicle permissions
    VEHICLE_READ = Permission(Resource.VEHICLES, Action.READ)
    VEHICLE_CREATE = Permission(Resource.VEHICLES, Action.CREATE)
    VEHICLE_UPDATE = Permission(Resource.VEHICLES, Action.UPDATE)
    VEHICLE_DELETE = Permission(Resource.VEHICLES, Action.DELETE)
    VEHICLE_ASSIGN = Permission(Resource.VEHICLES, Action.ASSIGN)

    # Workflow permissions
    WORKFLOW_READ = Permission(Resource.WORKFLOWS, Action.READ)
    WORKFLOW_CREATE = Permission(Resource.WORKFLOWS, Action.CREATE)
    WORKFLOW_UPDATE = Permission(Resource.WORKFLOWS, Action.UPDATE)
    WORKFLOW_DELETE = Permission(Resource.WORKFLOWS, Action.DELETE)
    WORKFLOW_APPROVE = Permission(Resource.WORKFLOWS, Action.APPROVE)
    WORKFLOW_REJECT = Permission(Resource.WORKFLOWS, Action.REJECT)

    # Report permissions
    REPORT_READ = Permission(Resource.REPORTS, Action.READ)
    REPORT_EXPORT = Permission(Resource.REPORTS, Action.EXPORT)

    # User management permissions
    USER_READ = Permission(Resource.USERS, Action.READ)
    USER_CREATE = Permission(Resource.USERS, Action.CREATE)
    USER_UPDATE = Permission(Resource.USERS, Action.UPDATE)
    USER_DELETE = Permission(Resource.USERS, Action.DELETE)

    # Settings permissions
    SETTINGS_READ = Permission(Resource.SETTINGS, Action.READ)
    SETTINGS_UPDATE = Permission(Resource.SETTINGS, Action.UPDATE)

    # Audit log permissions
    AUDIT_READ = Permission(Resource.AUDIT_LOGS, Action.READ)
    AUDIT_EXPORT = Permission(Resource.AUDIT_LOGS, Action.EXPORT)


def get_default_role_permissions(role_name: str) -> Set[str]:
    """
    Get default permissions for a role

    Args:
        role_name: Role name

    Returns:
        Set of permission strings
    """
    permissions_map = {
        "system_admin": {"*:*"},  # All permissions

        "organization_admin": {
            "couriers:*", "vehicles:*", "workflows:*", "routes:*",
            "reports:read", "reports:export",
            "users:read", "users:create", "users:update",
            "settings:read", "settings:update",
            "analytics:read",
        },

        "manager": {
            "couriers:read", "couriers:create", "couriers:update", "couriers:assign",
            "vehicles:read", "vehicles:create", "vehicles:update", "vehicles:assign",
            "workflows:read", "workflows:create", "workflows:update", "workflows:approve",
            "routes:read", "routes:create", "routes:update",
            "reports:read", "reports:export",
            "analytics:read",
        },

        "supervisor": {
            "couriers:read", "couriers:assign",
            "vehicles:read", "vehicles:assign",
            "workflows:read", "workflows:create", "workflows:update",
            "routes:read", "routes:create",
            "reports:read",
        },

        "user": {
            "couriers:read",
            "vehicles:read",
            "workflows:read",
            "routes:read",
            "reports:read",
        },

        "guest": {
            "workflows:read",
            "reports:read",
        }
    }

    return permissions_map.get(role_name.lower(), set())