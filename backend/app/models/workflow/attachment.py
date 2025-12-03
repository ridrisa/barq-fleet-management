from sqlalchemy import Column, String, Integer, ForeignKey, Text, Boolean, BigInteger, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class AttachmentType(str, enum.Enum):
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    SPREADSHEET = "spreadsheet"
    PDF = "pdf"
    OTHER = "other"


class WorkflowAttachment(TenantMixin, BaseModel):
    """File attachments for workflow instances"""
    __tablename__ = "workflow_attachments"

    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # File information
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # S3 path or local path
    file_size = Column(BigInteger)  # Size in bytes
    file_type = Column(String)  # MIME type
    attachment_type = Column(String)  # document, image, etc.

    # Optional metadata
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    download_count = Column(Integer, default=0)

    # Virus scan status (for security)
    is_scanned = Column(Boolean, default=False)
    scan_result = Column(String)  # clean, infected, unknown
    scan_date = Column(DateTime)

    # Relationships
    workflow_instance = relationship("WorkflowInstance", back_populates="attachments")
    uploaded_by = relationship("User")
