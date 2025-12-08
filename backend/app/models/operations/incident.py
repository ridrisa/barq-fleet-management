import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


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


class Incident(TenantMixin, BaseModel):
    __tablename__ = "incidents"

    incident_type = Column(
        Enum(IncidentType, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)
    incident_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(
        Enum(IncidentStatus, values_callable=lambda x: [e.value for e in x]),
        default=IncidentStatus.REPORTED,
    )
    resolution = Column(Text)
    cost = Column(Numeric(10, 2), default=0)

    courier = relationship("Courier", back_populates="incidents")
    vehicle = relationship("Vehicle", back_populates="incidents")
