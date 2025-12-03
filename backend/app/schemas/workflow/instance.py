from datetime import date
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WorkflowInstanceBase(BaseModel):
    template_id: int = Field(..., description="Workflow template ID")
    initiated_by: int = Field(..., description="User ID who initiated the workflow")
    current_step: int = Field(default=0, ge=0)
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Workflow execution data"
    )
    notes: Optional[str] = None


class WorkflowInstanceCreate(WorkflowInstanceBase):
    pass


class WorkflowInstanceUpdate(BaseModel):
    current_step: Optional[int] = Field(None, ge=0)
    status: Optional[WorkflowStatus] = None
    data: Optional[Dict[str, Any]] = None
    started_at: Optional[date] = None
    completed_at: Optional[date] = None
    notes: Optional[str] = None


class WorkflowInstanceResponse(WorkflowInstanceBase):
    id: int
    status: WorkflowStatus
    started_at: Optional[date] = None
    completed_at: Optional[date] = None
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
