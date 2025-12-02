"""
Operations Document Model
For storing operational procedures, policies, training materials, and reports.
"""
from sqlalchemy import Column, String, Integer, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class DocumentCategory(str, enum.Enum):
    """Document categories for operations"""
    PROCEDURES = "Procedures"
    POLICIES = "Policies"
    TRAINING = "Training"
    REPORTS = "Reports"
    TEMPLATES = "Templates"
    GUIDELINES = "Guidelines"
    OTHER = "Other"


class OperationsDocument(BaseModel):
    """Operations document model for procedures, policies, and training materials"""

    __tablename__ = "operations_documents"

    # Document identification
    doc_number = Column(String(50), unique=True, index=True, comment="Document number e.g. DOC-00001")
    doc_name = Column(String(255), nullable=False, comment="Document title/name")

    # Categorization
    category = Column(SQLEnum(DocumentCategory), default=DocumentCategory.OTHER, nullable=False)

    # File details
    file_name = Column(String(255), comment="Original file name")
    file_url = Column(String(500), nullable=False, comment="Storage URL or path")
    file_type = Column(String(50), comment="File extension (pdf, doc, docx, etc.)")
    file_size = Column(Integer, default=0, comment="File size in bytes")

    # Version control
    version = Column(String(20), default="1.0", comment="Document version")

    # Description
    description = Column(Text, comment="Document description or summary")

    # Access control
    is_public = Column(String(10), default="false", comment="Is document publicly accessible")
    department = Column(String(100), comment="Owning department")

    # Audit
    uploaded_by = Column(String(200), comment="Name of uploader")
    uploader_email = Column(String(200), comment="Email of uploader")
    uploaded_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # View tracking
    view_count = Column(Integer, default=0, comment="Number of times document was viewed")
    download_count = Column(Integer, default=0, comment="Number of times document was downloaded")

    # Tags for searchability
    tags = Column(String(500), comment="Comma-separated tags")

    def __repr__(self):
        return f"<OperationsDocument {self.doc_number or self.id}: {self.doc_name}>"

    @property
    def formatted_file_size(self) -> str:
        """Return human-readable file size"""
        if not self.file_size:
            return "0 Bytes"

        size = self.file_size
        for unit in ['Bytes', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
