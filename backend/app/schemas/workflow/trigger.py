from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TriggerType(str, Enum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    API = "api"
    WEBHOOK = "webhook"


class TriggerEventType(str, Enum):
    # Record events
    RECORD_CREATED = "record_created"
    RECORD_UPDATED = "record_updated"
    RECORD_DELETED = "record_deleted"
    # Workflow events
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    # Approval events
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_APPROVED = "approval_approved"
    APPROVAL_REJECTED = "approval_rejected"
    # SLA events
    SLA_WARNING = "sla_warning"
    SLA_BREACHED = "sla_breached"
    # Custom events
    CUSTOM = "custom"


# Workflow Trigger Schemas
class WorkflowTriggerBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    workflow_template_id: int
    trigger_type: TriggerType
    event_type: Optional[TriggerEventType] = None
    entity_type: Optional[str] = None
    field_conditions: Optional[Dict[str, Any]] = None
    schedule_cron: Optional[str] = None
    schedule_timezone: str = "UTC"
    conditions: Optional[List[Dict[str, Any]]] = None
    condition_logic: str = Field(default="AND", pattern="^(AND|OR)$")
    is_active: bool = True
    priority: int = Field(default=0, ge=0)
    deduplicate: bool = False
    deduplicate_key: Optional[str] = None
    deduplicate_window: Optional[int] = Field(None, ge=1, description="Deduplication window in seconds")
    rate_limit: Optional[int] = Field(None, ge=1, description="Max executions per hour")
    rate_limit_window: int = Field(default=3600, ge=1, description="Rate limit window in seconds")
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None


class WorkflowTriggerCreate(WorkflowTriggerBase):
    pass


class WorkflowTriggerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    trigger_type: Optional[TriggerType] = None
    event_type: Optional[TriggerEventType] = None
    entity_type: Optional[str] = None
    field_conditions: Optional[Dict[str, Any]] = None
    schedule_cron: Optional[str] = None
    schedule_timezone: Optional[str] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    condition_logic: Optional[str] = Field(None, pattern="^(AND|OR)$")
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)
    deduplicate: Optional[bool] = None
    deduplicate_key: Optional[str] = None
    deduplicate_window: Optional[int] = Field(None, ge=1)
    rate_limit: Optional[int] = Field(None, ge=1)
    rate_limit_window: Optional[int] = Field(None, ge=1)
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None


class WorkflowTriggerResponse(WorkflowTriggerBase):
    id: int
    last_triggered_at: Optional[datetime] = None
    next_trigger_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Trigger Execution Schemas
class TriggerExecutionBase(BaseModel):
    trigger_id: int
    workflow_instance_id: Optional[int] = None
    triggered_at: datetime
    trigger_data: Optional[Dict[str, Any]] = None
    status: str
    workflow_created: bool = False
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None


class TriggerExecutionCreate(TriggerExecutionBase):
    pass


class TriggerExecutionResponse(TriggerExecutionBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Action Schemas
class TriggerTestRequest(BaseModel):
    """Test trigger configuration"""
    test_data: Optional[Dict[str, Any]] = None
    dry_run: bool = True


class TriggerExecuteRequest(BaseModel):
    """Manually execute a trigger"""
    trigger_data: Optional[Dict[str, Any]] = None
