"""Role and Permission Management Service"""

from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.role import Permission, Role, role_permissions, user_roles
from app.models.user import User
from app.schemas.role import PermissionCreate, PermissionUpdate, RoleCreate, RoleUpdate


class PermissionService:
    """Service for permission management"""

    def create_permission(
        self,
        db: Session,
        *,
        name: str,
        resource: str,
        action: str,
        description: Optional[str] = None,
    ) -> Permission:
        """Create a new permission"""
        permission = Permission(
            name=name, resource=resource, action=action, description=description
        )
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission

    def get_permission(self, db: Session, permission_id: int) -> Optional[Permission]:
        """Get permission by ID"""
        return db.query(Permission).filter(Permission.id == permission_id).first()

    def get_permission_by_name(self, db: Session, name: str) -> Optional[Permission]:
        """Get permission by name"""
        return db.query(Permission).filter(Permission.name == name).first()

    def get_all_permissions(self, db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
        """Get all permissions"""
        return db.query(Permission).offset(skip).limit(limit).all()

    def get_permissions_by_resource(self, db: Session, resource: str) -> List[Permission]:
        """Get all permissions for a resource"""
        return db.query(Permission).filter(Permission.resource == resource).all()

    def update_permission(
        self, db: Session, permission_id: int, description: Optional[str] = None
    ) -> Optional[Permission]:
        """Update permission"""
        permission = self.get_permission(db, permission_id)
        if not permission:
            return None

        if description is not None:
            permission.description = description

        db.commit()
        db.refresh(permission)
        return permission

    def delete_permission(self, db: Session, permission_id: int) -> bool:
        """Delete permission"""
        permission = self.get_permission(db, permission_id)
        if not permission:
            return False

        db.delete(permission)
        db.commit()
        return True

    def seed_default_permissions(self, db: Session) -> List[Permission]:
        """
        Seed default system permissions

        Creates permissions for all resources with standard CRUD actions
        """
        from app.models.role import PermissionAction, PermissionResource

        permissions_created = []

        # Define which actions apply to which resources
        standard_crud = [
            PermissionAction.CREATE,
            PermissionAction.READ,
            PermissionAction.UPDATE,
            PermissionAction.DELETE,
        ]

        for resource in PermissionResource:
            # Add standard CRUD permissions
            for action in standard_crud:
                permission_name = f"{resource.value}:{action.value}"

                # Check if permission already exists
                existing = self.get_permission_by_name(db, permission_name)
                if not existing:
                    permission = self.create_permission(
                        db,
                        name=permission_name,
                        resource=resource.value,
                        action=action.value,
                        description=f"Can {action.value} {resource.value}",
                    )
                    permissions_created.append(permission)

            # Add special permissions for certain resources
            if resource in [PermissionResource.LEAVE, PermissionResource.LOAN]:
                # Add approve permission
                permission_name = f"{resource.value}:approve"
                if not self.get_permission_by_name(db, permission_name):
                    permission = self.create_permission(
                        db,
                        name=permission_name,
                        resource=resource.value,
                        action=PermissionAction.APPROVE.value,
                        description=f"Can approve {resource.value} requests",
                    )
                    permissions_created.append(permission)

        return permissions_created


class RoleService:
    """Service for role management"""

    def __init__(self):
        self.permission_service = PermissionService()

    def create_role(
        self,
        db: Session,
        *,
        name: str,
        display_name: str,
        description: Optional[str] = None,
        permission_ids: List[int] = [],
        is_system_role: bool = False,
    ) -> Role:
        """Create a new role"""
        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            is_system_role=is_system_role,
        )

        # Add permissions
        if permission_ids:
            permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions

        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    def get_role(self, db: Session, role_id: int) -> Optional[Role]:
        """Get role by ID"""
        return db.query(Role).filter(Role.id == role_id).first()

    def get_role_by_name(self, db: Session, name: str) -> Optional[Role]:
        """Get role by name"""
        return db.query(Role).filter(Role.name == name).first()

    def get_all_roles(
        self, db: Session, skip: int = 0, limit: int = 100, include_inactive: bool = False
    ) -> List[Role]:
        """Get all roles"""
        query = db.query(Role)

        if not include_inactive:
            query = query.filter(Role.is_active == True)

        return query.offset(skip).limit(limit).all()

    def update_role(
        self,
        db: Session,
        role_id: int,
        display_name: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None,
        permission_ids: Optional[List[int]] = None,
    ) -> Optional[Role]:
        """Update role"""
        role = self.get_role(db, role_id)
        if not role:
            return None

        # Can't modify system roles
        if role.is_system_role:
            raise ValueError("Cannot modify system roles")

        if display_name is not None:
            role.display_name = display_name

        if description is not None:
            role.description = description

        if is_active is not None:
            role.is_active = is_active

        if permission_ids is not None:
            permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
            role.permissions = permissions

        db.commit()
        db.refresh(role)
        return role

    def delete_role(self, db: Session, role_id: int) -> bool:
        """Delete role"""
        role = self.get_role(db, role_id)
        if not role:
            return False

        if role.is_system_role:
            raise ValueError("Cannot delete system roles")

        db.delete(role)
        db.commit()
        return True

    def assign_permissions_to_role(
        self, db: Session, role_id: int, permission_ids: List[int]
    ) -> Optional[Role]:
        """Assign permissions to role"""
        role = self.get_role(db, role_id)
        if not role:
            return None

        permissions = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()

        # Add new permissions (keeps existing ones)
        for permission in permissions:
            if permission not in role.permissions:
                role.permissions.append(permission)

        db.commit()
        db.refresh(role)
        return role

    def remove_permissions_from_role(
        self, db: Session, role_id: int, permission_ids: List[int]
    ) -> Optional[Role]:
        """Remove permissions from role"""
        role = self.get_role(db, role_id)
        if not role:
            return None

        permissions_to_remove = db.query(Permission).filter(Permission.id.in_(permission_ids)).all()

        for permission in permissions_to_remove:
            if permission in role.permissions:
                role.permissions.remove(permission)

        db.commit()
        db.refresh(role)
        return role

    def assign_roles_to_user(
        self, db: Session, user_id: int, role_ids: List[int]
    ) -> Optional[User]:
        """Assign roles to user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        roles = db.query(Role).filter(and_(Role.id.in_(role_ids), Role.is_active == True)).all()

        user.roles = roles

        db.commit()
        db.refresh(user)
        return user

    def get_user_roles(self, db: Session, user_id: int) -> List[Role]:
        """Get all roles for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        return user.roles

    def get_user_permissions(self, db: Session, user_id: int) -> List[Permission]:
        """Get all permissions for a user (from all their roles)"""
        user_roles = self.get_user_roles(db, user_id)

        # Collect unique permissions from all roles
        permissions_set = set()
        for role in user_roles:
            for permission in role.permissions:
                permissions_set.add(permission)

        return list(permissions_set)

    def user_has_permission(self, db: Session, user_id: int, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        permissions = self.get_user_permissions(db, user_id)
        return any(p.name == permission_name for p in permissions)

    def user_has_resource_action(
        self, db: Session, user_id: int, resource: str, action: str
    ) -> bool:
        """Check if user has permission for resource and action"""
        permission_name = f"{resource}:{action}"
        return self.user_has_permission(db, user_id, permission_name)

    def seed_default_roles(self, db: Session) -> List[Role]:
        """
        Seed default system roles

        Creates:
        - Super Admin (all permissions)
        - Admin (most permissions)
        - HR Manager (HR module permissions)
        - Fleet Manager (Fleet module permissions)
        - Operations Manager (Operations module permissions)
        - Courier (limited self-service permissions)
        - Viewer (read-only permissions)
        """
        # First seed permissions
        self.permission_service.seed_default_permissions(db)

        roles_created = []

        # Super Admin Role
        if not self.get_role_by_name(db, "super_admin"):
            all_permissions = self.permission_service.get_all_permissions(db, limit=1000)
            super_admin = self.create_role(
                db,
                name="super_admin",
                display_name="Super Administrator",
                description="Full system access with all permissions",
                permission_ids=[p.id for p in all_permissions],
                is_system_role=True,
            )
            roles_created.append(super_admin)

        # Admin Role
        if not self.get_role_by_name(db, "admin"):
            # Admin gets most permissions except user/role management
            admin_permissions = (
                db.query(Permission).filter(~Permission.resource.in_(["role", "permission"])).all()
            )
            admin = self.create_role(
                db,
                name="admin",
                display_name="Administrator",
                description="Administrative access to most system features",
                permission_ids=[p.id for p in admin_permissions],
                is_system_role=True,
            )
            roles_created.append(admin)

        # HR Manager Role
        if not self.get_role_by_name(db, "hr_manager"):
            hr_permissions = (
                db.query(Permission)
                .filter(
                    Permission.resource.in_(
                        ["leave", "loan", "attendance", "salary", "asset", "courier"]
                    )
                )
                .all()
            )
            hr_manager = self.create_role(
                db,
                name="hr_manager",
                display_name="HR Manager",
                description="Full access to HR module",
                permission_ids=[p.id for p in hr_permissions],
                is_system_role=True,
            )
            roles_created.append(hr_manager)

        # Fleet Manager Role
        if not self.get_role_by_name(db, "fleet_manager"):
            fleet_permissions = (
                db.query(Permission)
                .filter(
                    Permission.resource.in_(["courier", "vehicle", "assignment", "maintenance"])
                )
                .all()
            )
            fleet_manager = self.create_role(
                db,
                name="fleet_manager",
                display_name="Fleet Manager",
                description="Full access to Fleet module",
                permission_ids=[p.id for p in fleet_permissions],
                is_system_role=True,
            )
            roles_created.append(fleet_manager)

        # Viewer Role
        if not self.get_role_by_name(db, "viewer"):
            read_permissions = db.query(Permission).filter(Permission.action == "read").all()
            viewer = self.create_role(
                db,
                name="viewer",
                display_name="Viewer",
                description="Read-only access to most resources",
                permission_ids=[p.id for p in read_permissions],
                is_system_role=True,
            )
            roles_created.append(viewer)

        return roles_created


# Singleton instances
permission_service = PermissionService()
role_service = RoleService()
