from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum

class BedStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"

class Bed(TenantMixin, BaseModel):
    __tablename__ = "beds"

    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    bed_number = Column(Integer, nullable=False)
    status = Column(Enum(BedStatus), default=BedStatus.AVAILABLE)

    room = relationship("Room", back_populates="beds")
    allocation = relationship("Allocation", back_populates="bed", uselist=False)
