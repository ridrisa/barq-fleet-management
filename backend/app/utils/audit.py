"""Audit Logging Utility

Centralized utility for creating audit log entries throughout the application.
Provides consistent audit logging for all admin actions.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog, AuditAction
from app.models.user import User


class AuditLogger:
    """Audit logging utility class"""

    @staticmethod
    def log(
        db: Session,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[int] = None,
        description: str = "",
        user: Optional[User] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            db: Database session
            action: Action performed (from AuditAction enum)
            resource_type: Type of resource (e.g., "user", "role", "backup")
            resource_id: ID of the affected resource
            description: Human-readable description
            user: User who performed the action
            ip_address: IP address of the request
            user_agent: User agent string
            old_values: Previous values (for updates)
            new_values: New values (for updates/creates)
            metadata: Additional metadata

        Returns:
            Created AuditLog instance
        """
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            user_id=user.id if user else None,
            username=user.email if user else None,
            ip_address=ip_address,
            user_agent=user_agent,
            old_values=old_values or {},
            new_values=new_values or {},
            metadata=metadata or {},
        )

        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)

        return audit_log

    @staticmethod
    def log_create(
        db: Session,
        resource_type: str,
        resource_id: int,
        user: User,
        description: Optional[str] = None,
        new_values: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditLog:
        """Log a CREATE action"""
        desc = description or f"Created {resource_type} with ID {resource_id}"
        return AuditLogger.log(
            db=db,
            action=AuditAction.CREATE,
            resource_type=resource_type,
            resource_id=resource_id,
            description=desc,
            user=user,
            new_values=new_values,
            **kwargs
        )

    @staticmethod
    def log_update(
        db: Session,
        resource_type: str,
        resource_id: int,
        user: User,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditLog:
        """Log an UPDATE action"""
        desc = description or f"Updated {resource_type} with ID {resource_id}"
        return AuditLogger.log(
            db=db,
            action=AuditAction.UPDATE,
            resource_type=resource_type,
            resource_id=resource_id,
            description=desc,
            user=user,
            old_values=old_values,
            new_values=new_values,
            **kwargs
        )

    @staticmethod
    def log_delete(
        db: Session,
        resource_type: str,
        resource_id: int,
        user: User,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditLog:
        """Log a DELETE action"""
        desc = description or f"Deleted {resource_type} with ID {resource_id}"
        return AuditLogger.log(
            db=db,
            action=AuditAction.DELETE,
            resource_type=resource_type,
            resource_id=resource_id,
            description=desc,
            user=user,
            old_values=old_values,
            **kwargs
        )

    @staticmethod
    def log_login(
        db: Session,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
    ) -> AuditLog:
        """Log a login attempt"""
        action = AuditAction.LOGIN if success else AuditAction.FAILED_LOGIN
        description = f"User {user.email} logged in successfully" if success else f"Failed login attempt for {user.email}"
        return AuditLogger.log(
            db=db,
            action=action,
            resource_type="user",
            resource_id=user.id,
            description=description,
            user=user if success else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def log_logout(
        db: Session,
        user: User,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Log a logout"""
        return AuditLogger.log(
            db=db,
            action=AuditAction.LOGOUT,
            resource_type="user",
            resource_id=user.id,
            description=f"User {user.email} logged out",
            user=user,
            ip_address=ip_address,
        )

    @staticmethod
    def log_access(
        db: Session,
        resource_type: str,
        resource_id: int,
        user: User,
        description: Optional[str] = None,
        **kwargs
    ) -> AuditLog:
        """Log an ACCESS/READ action"""
        desc = description or f"Accessed {resource_type} with ID {resource_id}"
        return AuditLogger.log(
            db=db,
            action=AuditAction.READ,
            resource_type=resource_type,
            resource_id=resource_id,
            description=desc,
            user=user,
            **kwargs
        )

    @staticmethod
    def log_permission_change(
        db: Session,
        user: User,
        target_user_id: int,
        old_permissions: list,
        new_permissions: list,
        **kwargs
    ) -> AuditLog:
        """Log a permission/role change"""
        return AuditLogger.log(
            db=db,
            action=AuditAction.PERMISSION_CHANGE,
            resource_type="user",
            resource_id=target_user_id,
            description=f"Changed permissions for user ID {target_user_id}",
            user=user,
            old_values={"permissions": old_permissions},
            new_values={"permissions": new_permissions},
            **kwargs
        )

    @staticmethod
    def log_system_action(
        db: Session,
        action_type: str,
        description: str,
        user: Optional[User] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditLog:
        """Log a system-level action (backup, integration test, etc.)"""
        return AuditLogger.log(
            db=db,
            action=AuditAction.SYSTEM,
            resource_type="system",
            description=description,
            user=user,
            metadata={**(metadata or {}), "action_type": action_type},
            **kwargs
        )


# Convenience function for quick audit logging
def log_audit(
    db: Session,
    action: AuditAction,
    resource_type: str,
    user: User,
    **kwargs
) -> AuditLog:
    """
    Quick audit log helper.

    Usage:
        log_audit(db, AuditAction.CREATE, "backup", user, resource_id=backup.id)
    """
    return AuditLogger.log(
        db=db,
        action=action,
        resource_type=resource_type,
        user=user,
        **kwargs
    )
