from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin

class Building(TenantMixin, BaseModel):
    __tablename__ = "buildings"

    name = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    total_rooms = Column(Integer, default=0)
    total_capacity = Column(Integer, default=0)
    notes = Column(Text)

    rooms = relationship("Room", back_populates="building")
