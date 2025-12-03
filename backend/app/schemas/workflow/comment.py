from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class WorkflowCommentBase(BaseModel):
    """Base schema for workflow comments"""

    comment: str = Field(..., min_length=1, max_length=5000)
    is_internal: bool = False
    parent_comment_id: Optional[int] = None


class WorkflowCommentCreate(WorkflowCommentBase):
    """Schema for creating a workflow comment"""

    workflow_instance_id: int
    user_id: int


class WorkflowCommentUpdate(BaseModel):
    """Schema for updating a workflow comment"""

    comment: Optional[str] = Field(None, min_length=1, max_length=5000)
    is_internal: Optional[bool] = None


class WorkflowCommentResponse(WorkflowCommentBase):
    """Schema for workflow comment response"""

    id: int
    workflow_instance_id: int
    user_id: int
    is_edited: bool
    edited_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: Optional[List["WorkflowCommentResponse"]] = []

    model_config = ConfigDict(from_attributes=True)


class WorkflowCommentWithUser(WorkflowCommentResponse):
    """Extended schema with user details"""

    user_name: Optional[str] = None
    user_email: Optional[str] = None


# Allow forward reference resolution
WorkflowCommentResponse.model_rebuild()
