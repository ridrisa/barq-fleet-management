"""Audit Log Service

Service for creating and querying audit logs.
Provides comprehensive audit trail for compliance and security.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.models.audit_log import AuditAction, AuditLog
from app.schemas.audit_log import AuditLogCreate, AuditLogFilter
from app.services.base import CRUDBase


class AuditLogService(CRUDBase[AuditLog, AuditLogCreate, AuditLogCreate]):
    """
    Service for audit log management

    Provides methods for:
    - Creating audit log entries
    - Querying audit logs with filters
    - Generating audit reports
    - Tracking user activity
    """

    def create_log(
        self,
        db: Session,
        *,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[int] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        http_method: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
    ) -> AuditLog:
        """
        Create a new audit log entry

        Args:
            db: Database session
            user_id: ID of user who performed the action
            username: Username (cached for performance)
            action: Type of action performed
            resource_type: Type of resource affected (e.g., "courier", "vehicle")
            resource_id: ID of the affected resource
            old_values: Previous state (for updates/deletes)
            new_values: New state (for creates/updates)
            ip_address: IP address of the client
            user_agent: User agent string
            endpoint: API endpoint accessed
            http_method: HTTP method used
            metadata: Additional context
            description: Human-readable description

        Returns:
            Created AuditLog instance
        """
        log_data = AuditLogCreate(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            http_method=http_method,
            metadata=metadata,
            description=description,
        )

        return self.create(db, obj_in=log_data)

    def get_by_filter(
        self, db: Session, *, filter_params: AuditLogFilter, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """
        Get audit logs with filtering

        Args:
            db: Database session
            filter_params: Filter parameters
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AuditLog instances
        """
        query = db.query(self.model)

        # Apply filters
        if filter_params.user_id:
            query = query.filter(self.model.user_id == filter_params.user_id)

        if filter_params.action:
            query = query.filter(self.model.action == filter_params.action)

        if filter_params.resource_type:
            query = query.filter(self.model.resource_type == filter_params.resource_type)

        if filter_params.resource_id:
            query = query.filter(self.model.resource_id == filter_params.resource_id)

        if filter_params.start_date:
            query = query.filter(self.model.created_at >= filter_params.start_date)

        if filter_params.end_date:
            query = query.filter(self.model.created_at <= filter_params.end_date)

        if filter_params.ip_address:
            query = query.filter(self.model.ip_address == filter_params.ip_address)

        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.filter(
                or_(
                    self.model.username.ilike(search_term),
                    self.model.resource_type.ilike(search_term),
                    self.model.description.ilike(search_term),
                )
            )

        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def get_user_activity(
        self, db: Session, *, user_id: int, days: int = 30, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """
        Get activity logs for a specific user

        Args:
            db: Database session
            user_id: User ID
            days: Number of days to look back
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AuditLog instances
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        return (
            db.query(self.model)
            .filter(and_(self.model.user_id == user_id, self.model.created_at >= start_date))
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_resource_history(
        self, db: Session, *, resource_type: str, resource_id: int, skip: int = 0, limit: int = 100
    ) -> List[AuditLog]:
        """
        Get complete history for a specific resource

        Args:
            db: Database session
            resource_type: Type of resource (e.g., "courier")
            resource_id: ID of the resource
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of AuditLog instances showing all changes to the resource
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.resource_type == resource_type, self.model.resource_id == resource_id
                )
            )
            .order_by(desc(self.model.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_summary(self, db: Session, *, days: int = 30) -> Dict[str, Any]:
        """
        Get audit log summary statistics

        Args:
            db: Database session
            days: Number of days to include in summary

        Returns:
            Dictionary with summary statistics
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Total logs
        total = (
            db.query(func.count(self.model.id)).filter(self.model.created_at >= start_date).scalar()
        )

        # Actions breakdown
        actions_breakdown = {}
        action_stats = (
            db.query(self.model.action, func.count(self.model.id))
            .filter(self.model.created_at >= start_date)
            .group_by(self.model.action)
            .all()
        )
        for action, count in action_stats:
            actions_breakdown[action.value] = count

        # Resources breakdown
        resources_breakdown = {}
        resource_stats = (
            db.query(self.model.resource_type, func.count(self.model.id))
            .filter(self.model.created_at >= start_date)
            .group_by(self.model.resource_type)
            .all()
        )
        for resource_type, count in resource_stats:
            resources_breakdown[resource_type] = count

        # Top users
        top_users = (
            db.query(
                self.model.user_id,
                self.model.username,
                func.count(self.model.id).label("activity_count"),
            )
            .filter(and_(self.model.created_at >= start_date, self.model.user_id.isnot(None)))
            .group_by(self.model.user_id, self.model.username)
            .order_by(desc("activity_count"))
            .limit(10)
            .all()
        )

        top_users_list = [
            {"user_id": user_id, "username": username, "activity_count": count}
            for user_id, username, count in top_users
        ]

        # Recent activities
        recent = (
            db.query(self.model)
            .filter(self.model.created_at >= start_date)
            .order_by(desc(self.model.created_at))
            .limit(20)
            .all()
        )

        return {
            "period_days": days,
            "total_logs": total,
            "actions_breakdown": actions_breakdown,
            "resources_breakdown": resources_breakdown,
            "top_users": top_users_list,
            "recent_activities": recent,
        }

    def clean_old_logs(self, db: Session, *, days_to_keep: int = 365) -> int:
        """
        Clean up old audit logs (for maintenance)

        Args:
            db: Database session
            days_to_keep: Number of days of logs to keep

        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        deleted_count = db.query(self.model).filter(self.model.created_at < cutoff_date).delete()

        db.commit()
        return deleted_count


# Singleton instance
audit_log_service = AuditLogService(AuditLog)
