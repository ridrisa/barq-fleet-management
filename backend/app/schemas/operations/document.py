"""
Operations Document Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.operations.document import DocumentCategory


class OperationsDocumentBase(BaseModel):
    """Base schema for operations documents"""
    doc_name: str = Field(..., max_length=255, description="Document title")
    category: Optional[DocumentCategory] = DocumentCategory.OTHER
    file_name: Optional[str] = Field(None, max_length=255)
    file_url: str = Field(..., max_length=500, description="Storage URL")
    file_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = Field(0, ge=0)
    version: Optional[str] = Field("1.0", max_length=20)
    description: Optional[str] = None
    is_public: Optional[str] = "false"
    department: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)


class OperationsDocumentCreate(OperationsDocumentBase):
    """Schema for creating operations document"""
    uploaded_by: Optional[str] = Field(None, max_length=200)
    uploader_email: Optional[str] = Field(None, max_length=200)


class OperationsDocumentUpdate(BaseModel):
    """Schema for updating operations document"""
    doc_name: Optional[str] = Field(None, max_length=255)
    category: Optional[DocumentCategory] = None
    file_name: Optional[str] = Field(None, max_length=255)
    file_url: Optional[str] = Field(None, max_length=500)
    file_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = Field(None, ge=0)
    version: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    is_public: Optional[str] = None
    department: Optional[str] = Field(None, max_length=100)
    tags: Optional[str] = Field(None, max_length=500)


class OperationsDocumentResponse(OperationsDocumentBase):
    """Schema for operations document response"""
    id: int
    doc_number: Optional[str] = None
    uploaded_by: Optional[str] = None
    uploader_email: Optional[str] = None
    uploaded_by_id: Optional[int] = None
    view_count: int = 0
    download_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
