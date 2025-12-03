"""Audit Log Model"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class AuditAction(str, enum.Enum):
    """Audit action types"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    LOGIN = "login"
    LOGOUT = "logout"
    APPROVE = "approve"
    REJECT = "reject"
    EXPORT = "export"


class AuditLog(BaseModel):
    """
    Audit log model for tracking all system changes and actions

    Tracks:
    - Who performed the action (user_id)
    - What action was performed (action)
    - What resource was affected (resource_type, resource_id)
    - When it happened (timestamp via BaseModel)
    - Where it happened (ip_address)
    - What changed (old_values, new_values)
    - Additional context (metadata)
    """

    __tablename__ = "audit_logs"

    # Who
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="audit_logs")
    username = Column(String(255), nullable=True)  # Cached for performance

    # What
    action = Column(Enum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # e.g., "courier", "vehicle"
    resource_id = Column(Integer, nullable=True, index=True)  # ID of the affected resource

    # Changes
    old_values = Column(JSON, nullable=True)  # Previous state (for updates/deletes)
    new_values = Column(JSON, nullable=True)  # New state (for creates/updates)

    # Context
    ip_address = Column(String(45), nullable=True)  # Supports IPv6
    user_agent = Column(Text, nullable=True)  # Browser/client info
    endpoint = Column(String(255), nullable=True)  # API endpoint accessed
    http_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE

    # Additional metadata
    extra_metadata = Column(JSON, nullable=True)  # Any extra contextual information
    description = Column(Text, nullable=True)  # Human-readable description

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, user_id={self.user_id}, "
            f"action={self.action}, resource_type={self.resource_type}, "
            f"resource_id={self.resource_id})>"
        )
