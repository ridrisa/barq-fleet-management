from sqlalchemy import Column, String, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class RoomStatus(str, enum.Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"

class Room(BaseModel):
    __tablename__ = "rooms"

    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    room_number = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    occupied = Column(Integer, default=0)
    status = Column(Enum(RoomStatus), default=RoomStatus.AVAILABLE)

    building = relationship("Building", back_populates="rooms")
    beds = relationship("Bed", back_populates="room")
