from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SLAStatus(str, Enum):
    ACTIVE = "active"
    WARNING = "warning"
    BREACHED = "breached"
    PAUSED = "paused"
    COMPLETED = "completed"


class SLAPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Workflow SLA Schemas
class WorkflowSLABase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    workflow_template_id: Optional[int] = None
    priority: SLAPriority = SLAPriority.MEDIUM
    response_time: Optional[int] = Field(None, ge=1, description="Response time in minutes")
    resolution_time: int = Field(..., ge=1, description="Resolution time in minutes")
    warning_threshold: Optional[int] = Field(
        None, ge=1, le=100, description="Warning threshold percentage"
    )
    use_business_hours: bool = False
    business_hours_start: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    business_hours_end: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")
    business_days: Optional[List[str]] = None
    escalate_on_warning: bool = False
    escalate_on_breach: bool = True
    escalation_chain: Optional[List[Dict[str, Any]]] = None
    is_active: bool = True


class WorkflowSLACreate(WorkflowSLABase):
    pass


class WorkflowSLAUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    priority: Optional[SLAPriority] = None
    response_time: Optional[int] = Field(None, ge=1)
    resolution_time: Optional[int] = Field(None, ge=1)
    warning_threshold: Optional[int] = Field(None, ge=1, le=100)
    use_business_hours: Optional[bool] = None
    business_hours_start: Optional[str] = None
    business_hours_end: Optional[str] = None
    business_days: Optional[List[str]] = None
    escalate_on_warning: Optional[bool] = None
    escalate_on_breach: Optional[bool] = None
    escalation_chain: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class WorkflowSLAResponse(WorkflowSLABase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Workflow SLA Instance Schemas
class WorkflowSLAInstanceBase(BaseModel):
    workflow_instance_id: int
    sla_id: int
    started_at: datetime
    resolution_due_at: datetime
    response_due_at: Optional[datetime] = None
    warning_at: Optional[datetime] = None


class WorkflowSLAInstanceCreate(WorkflowSLAInstanceBase):
    pass


class WorkflowSLAInstanceUpdate(BaseModel):
    status: Optional[SLAStatus] = None
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    breached_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    pause_duration: Optional[int] = Field(None, ge=0)
    response_time_minutes: Optional[int] = None
    resolution_time_minutes: Optional[int] = None
    breach_time_minutes: Optional[int] = None
    warning_sent: Optional[bool] = None
    escalation_sent: Optional[bool] = None
    escalation_level: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None


class WorkflowSLAInstanceResponse(WorkflowSLAInstanceBase):
    id: int
    status: SLAStatus
    first_response_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    breached_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    pause_duration: int = 0
    response_time_minutes: Optional[int] = None
    resolution_time_minutes: Optional[int] = None
    breach_time_minutes: Optional[int] = None
    warning_sent: bool = False
    escalation_sent: bool = False
    escalation_level: int = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# SLA Event Schemas
class SLAEventBase(BaseModel):
    sla_instance_id: int
    event_type: str
    event_time: datetime
    triggered_by_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class SLAEventCreate(SLAEventBase):
    pass


class SLAEventResponse(SLAEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Action Schemas
class SLAActionRequest(BaseModel):
    """Request to pause/resume SLA"""

    action: str = Field(..., pattern="^(pause|resume)$")
    notes: Optional[str] = None
