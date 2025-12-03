from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AutomationTriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    CONDITION = "condition"
    WEBHOOK = "webhook"


class AutomationActionType(str, Enum):
    CREATE_WORKFLOW = "create_workflow"
    UPDATE_WORKFLOW = "update_workflow"
    SEND_NOTIFICATION = "send_notification"
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    UPDATE_RECORD = "update_record"
    WEBHOOK_CALL = "webhook_call"
    CUSTOM_SCRIPT = "custom_script"


class AutomationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    ERROR = "error"


# Workflow Automation Schemas
class WorkflowAutomationBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    workflow_template_id: Optional[int] = None
    trigger_type: AutomationTriggerType
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    condition_logic: str = Field(default="AND", pattern="^(AND|OR)$")
    action_type: AutomationActionType
    action_config: Optional[Dict[str, Any]] = None
    is_active: bool = True
    run_order: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: int = Field(default=60, ge=1, description="Retry delay in seconds")
    timeout: int = Field(default=300, ge=1, description="Timeout in seconds")
    schedule_cron: Optional[str] = None
    schedule_timezone: str = "UTC"


class WorkflowAutomationCreate(WorkflowAutomationBase):
    pass


class WorkflowAutomationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    trigger_type: Optional[AutomationTriggerType] = None
    trigger_config: Optional[Dict[str, Any]] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    condition_logic: Optional[str] = Field(None, pattern="^(AND|OR)$")
    action_type: Optional[AutomationActionType] = None
    action_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    run_order: Optional[int] = Field(None, ge=0)
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    retry_delay: Optional[int] = Field(None, ge=1)
    timeout: Optional[int] = Field(None, ge=1)
    schedule_cron: Optional[str] = None
    schedule_timezone: Optional[str] = None
    status: Optional[AutomationStatus] = None


class WorkflowAutomationResponse(WorkflowAutomationBase):
    id: int
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    status: AutomationStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Automation Execution Log Schemas
class AutomationExecutionLogBase(BaseModel):
    automation_id: int
    workflow_instance_id: Optional[int] = None
    started_at: datetime
    trigger_data: Optional[Dict[str, Any]] = None


class AutomationExecutionLogCreate(AutomationExecutionLogBase):
    pass


class AutomationExecutionLogUpdate(BaseModel):
    completed_at: Optional[datetime] = None
    status: Optional[str] = None
    action_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = Field(None, ge=0)
    execution_time_ms: Optional[int] = None


class AutomationExecutionLogResponse(AutomationExecutionLogBase):
    id: int
    completed_at: Optional[datetime] = None
    status: str
    action_result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    execution_time_ms: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Action Schemas
class AutomationExecuteRequest(BaseModel):
    """Manual trigger for automation"""

    trigger_data: Optional[Dict[str, Any]] = None


class AutomationTestRequest(BaseModel):
    """Test automation configuration"""

    test_data: Optional[Dict[str, Any]] = None
    dry_run: bool = True
