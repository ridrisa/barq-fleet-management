"""Role and Permission Models for RBAC"""

import enum

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

# Association table for role-permission many-to-many relationship
role_permissions = Table(
    "role_permissions",
    BaseModel.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    ),
)

# Association table for user-role many-to-many relationship
user_roles = Table(
    "user_roles",
    BaseModel.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class PermissionAction(str, enum.Enum):
    """Permission actions"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"
    MANAGE = "manage"


class PermissionResource(str, enum.Enum):
    """System resources that can have permissions"""

    # Fleet
    COURIER = "courier"
    VEHICLE = "vehicle"
    ASSIGNMENT = "assignment"
    MAINTENANCE = "maintenance"

    # HR
    LEAVE = "leave"
    LOAN = "loan"
    ATTENDANCE = "attendance"
    SALARY = "salary"
    ASSET = "asset"

    # Operations
    COD = "cod"
    DELIVERY = "delivery"
    ROUTE = "route"
    INCIDENT = "incident"

    # Accommodation
    BUILDING = "building"
    ROOM = "room"
    BED = "bed"
    ALLOCATION = "allocation"

    # Workflow
    WORKFLOW_TEMPLATE = "workflow_template"
    WORKFLOW_INSTANCE = "workflow_instance"

    # Support
    TICKET = "ticket"

    # Analytics
    ANALYTICS = "analytics"
    REPORTS = "reports"

    # Admin
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    AUDIT_LOG = "audit_log"
    SETTINGS = "settings"


class Permission(BaseModel):
    """
    Permission model for granular access control

    Permissions are defined as a combination of:
    - Resource (what): e.g., "courier", "vehicle", "salary"
    - Action (how): e.g., "create", "read", "update", "delete"

    Example permissions:
    - courier:read (can view courier data)
    - courier:create (can create new couriers)
    - salary:read (can view salary records)
    - salary:manage (can manage all salary operations)
    """

    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "courier:read"
    resource = Column(String(50), nullable=False, index=True)  # e.g., "courier"
    action = Column(String(20), nullable=False)  # e.g., "read"
    description = Column(Text, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    def __repr__(self):
        return f"<Permission(name={self.name}, resource={self.resource}, action={self.action})>"


class Role(BaseModel):
    """
    Role model for Role-Based Access Control (RBAC)

    Roles group related permissions together.
    Users can have multiple roles.

    Example roles:
    - Admin: Full system access
    - HR Manager: HR operations access
    - Fleet Manager: Fleet operations access
    - Courier: Limited self-service access
    - Viewer: Read-only access
    """

    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_system_role = Column(Boolean, default=False)  # System roles can't be deleted
    is_active = Column(Boolean, default=True)

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role(name={self.name}, display_name={self.display_name})>"

    def has_permission(self, permission_name: str) -> bool:
        """Check if role has a specific permission"""
        return any(p.name == permission_name for p in self.permissions)

    def has_resource_action(self, resource: str, action: str) -> bool:
        """Check if role has permission for resource and action"""
        permission_name = f"{resource}:{action}"
        return self.has_permission(permission_name)
