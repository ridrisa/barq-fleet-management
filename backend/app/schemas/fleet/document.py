from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.fleet.document import DocumentEntity, DocumentType


class DocumentBase(BaseModel):
    """Base document schema"""

    entity_type: DocumentEntity
    entity_id: int
    document_type: DocumentType
    document_number: Optional[str] = Field(None, max_length=100)
    document_name: str = Field(..., max_length=200)
    file_url: str = Field(..., max_length=500)
    file_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)


class DocumentCreate(DocumentBase):
    """Schema for creating document"""

    pass


class DocumentUpdate(BaseModel):
    """Schema for updating document"""

    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = Field(None, max_length=100)
    document_name: Optional[str] = Field(None, max_length=200)
    file_url: Optional[str] = Field(None, max_length=500)
    file_type: Optional[str] = Field(None, max_length=50)
    file_size: Optional[int] = None
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    issuing_authority: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)


class DocumentResponse(DocumentBase):
    """Schema for document response"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
