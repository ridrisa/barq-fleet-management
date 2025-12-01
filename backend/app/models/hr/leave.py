from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class LeaveType(str, enum.Enum):
    ANNUAL = "annual"
    SICK = "sick"
    EMERGENCY = "emergency"
    UNPAID = "unpaid"

class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class Leave(BaseModel):
    __tablename__ = "leaves"

    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=False)
    leave_type = Column(Enum(LeaveType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(Integer, nullable=False)
    status = Column(Enum(LeaveStatus, values_callable=lambda x: [e.value for e in x]), default=LeaveStatus.PENDING)
    reason = Column(Text)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(Date, nullable=True)
    notes = Column(Text)

    # Relationships
    courier = relationship("Courier", back_populates="leaves")
    approver = relationship("User", foreign_keys=[approved_by])
