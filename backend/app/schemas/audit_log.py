"""Audit Log Schemas"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.models.audit_log import AuditAction


class AuditLogBase(BaseModel):
    """Base schema for audit log"""

    user_id: Optional[int] = None
    username: Optional[str] = None
    action: AuditAction
    resource_type: str = Field(..., max_length=100)
    resource_id: Optional[int] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    user_agent: Optional[str] = None
    endpoint: Optional[str] = Field(None, max_length=255)
    http_method: Optional[str] = Field(None, max_length=10)
    metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log"""

    pass


class AuditLogResponse(AuditLogBase):
    """Schema for audit log response"""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs"""

    user_id: Optional[int] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    ip_address: Optional[str] = None
    search: Optional[str] = None


class AuditLogSummary(BaseModel):
    """Summary statistics for audit logs"""

    total_logs: int
    actions_breakdown: Dict[str, int]
    resources_breakdown: Dict[str, int]
    top_users: list[Dict[str, Any]]
    recent_activities: list[AuditLogResponse]
