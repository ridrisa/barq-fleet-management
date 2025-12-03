import enum

from sqlalchemy import Column, Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class DocumentType(str, enum.Enum):
    """Document types"""

    DRIVER_LICENSE = "driver_license"
    VEHICLE_REGISTRATION = "vehicle_registration"
    INSURANCE = "insurance"
    MULKIYA = "mulkiya"
    IQAMA = "iqama"
    PASSPORT = "passport"
    CONTRACT = "contract"
    OTHER = "other"


class DocumentEntity(str, enum.Enum):
    """Entity type that the document belongs to"""

    COURIER = "courier"
    VEHICLE = "vehicle"


class Document(TenantMixin, BaseModel):
    __tablename__ = "documents"

    # Entity reference
    entity_type = Column(SQLEnum(DocumentEntity), nullable=False)
    entity_id = Column(Integer, nullable=False)

    # Document details
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    document_number = Column(String(100))
    document_name = Column(String(200), nullable=False)

    # File reference
    file_url = Column(String(500), nullable=False)
    file_type = Column(String(50))  # pdf, jpg, png, etc.
    file_size = Column(Integer)  # Size in bytes

    # Dates
    issue_date = Column(Date)
    expiry_date = Column(Date)

    # Additional info
    issuing_authority = Column(String(200))
    notes = Column(String(500))

    # Relationships (polymorphic - can belong to either courier or vehicle)
    # We don't create FK constraints since entity_id can point to different tables
    # Instead we handle this at application level
