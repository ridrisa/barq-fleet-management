from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class IncidentType(str, enum.Enum):
    ACCIDENT = "accident"
    THEFT = "theft"
    DAMAGE = "damage"
    VIOLATION = "violation"
    OTHER = "other"

class IncidentStatus(str, enum.Enum):
    REPORTED = "reported"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

class Incident(BaseModel):
    __tablename__ = "incidents"

    incident_type = Column(Enum(IncidentType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    incident_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(IncidentStatus, values_callable=lambda x: [e.value for e in x]), default=IncidentStatus.REPORTED)
    resolution = Column(Text)
    cost = Column(Integer, default=0)

    courier = relationship("Courier")
    vehicle = relationship("Vehicle")
