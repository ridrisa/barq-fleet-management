from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.workflow.attachment import AttachmentType


class WorkflowAttachmentBase(BaseModel):
    """Base schema for workflow attachments"""
    file_name: str = Field(..., min_length=1, max_length=255)
    file_path: str
    file_size: Optional[int] = Field(None, ge=0)
    file_type: Optional[str] = None
    attachment_type: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)
    is_public: bool = False


class WorkflowAttachmentCreate(WorkflowAttachmentBase):
    """Schema for creating a workflow attachment"""
    workflow_instance_id: int
    uploaded_by_id: int


class WorkflowAttachmentUpdate(BaseModel):
    """Schema for updating a workflow attachment"""
    file_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_public: Optional[bool] = None


class WorkflowAttachmentResponse(WorkflowAttachmentBase):
    """Schema for workflow attachment response"""
    id: int
    workflow_instance_id: int
    uploaded_by_id: int
    download_count: int
    is_scanned: bool
    scan_result: Optional[str] = None
    scan_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowAttachmentWithUploader(WorkflowAttachmentResponse):
    """Extended schema with uploader details"""
    uploader_name: Optional[str] = None
    uploader_email: Optional[str] = None


class AttachmentUploadRequest(BaseModel):
    """Schema for file upload request"""
    workflow_instance_id: int
    description: Optional[str] = None
    is_public: bool = False


class AttachmentDownloadResponse(BaseModel):
    """Schema for download response"""
    file_url: str
    file_name: str
    file_size: int
    expires_at: datetime
