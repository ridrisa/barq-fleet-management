from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.workflow.history import WorkflowHistoryEventType


class WorkflowHistoryBase(BaseModel):
    """Base schema for workflow history"""

    event_type: WorkflowHistoryEventType
    description: str = Field(..., min_length=1, max_length=1000)
    actor_type: str = "user"
    previous_state: Optional[Dict[str, Any]] = None
    new_state: Optional[Dict[str, Any]] = None
    field_changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class WorkflowHistoryCreate(WorkflowHistoryBase):
    """Schema for creating a workflow history entry"""

    workflow_instance_id: int
    actor_id: Optional[int] = None
    event_time: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class WorkflowHistoryResponse(WorkflowHistoryBase):
    """Schema for workflow history response"""

    id: int
    workflow_instance_id: int
    actor_id: Optional[int] = None
    event_time: datetime
    ip_address: Optional[str] = None
    checksum: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowHistoryWithActor(WorkflowHistoryResponse):
    """Extended schema with actor details"""

    actor_name: Optional[str] = None
    actor_email: Optional[str] = None


class WorkflowStepHistoryBase(BaseModel):
    """Base schema for workflow step history"""

    step_index: int
    step_name: str
    status: str
    result: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class WorkflowStepHistoryCreate(WorkflowStepHistoryBase):
    """Schema for creating workflow step history"""

    workflow_instance_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    executed_by_id: Optional[int] = None
    duration_seconds: Optional[int] = None
    wait_time_seconds: Optional[int] = None


class WorkflowStepHistoryResponse(WorkflowStepHistoryBase):
    """Schema for workflow step history response"""

    id: int
    workflow_instance_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    executed_by_id: Optional[int] = None
    duration_seconds: Optional[int] = None
    wait_time_seconds: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowTimelineResponse(BaseModel):
    """Complete timeline view of workflow history"""

    workflow_instance_id: int
    workflow_name: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_minutes: Optional[int] = None
    events: List[WorkflowHistoryWithActor]
    steps: List[WorkflowStepHistoryResponse]

    model_config = ConfigDict(from_attributes=True)
