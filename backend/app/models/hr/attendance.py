import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Index, Integer, String, Time, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"


class Attendance(TenantMixin, BaseModel):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint('courier_id', 'date', 'organization_id', name='uq_attendance_courier_date'),
        Index('ix_attendance_courier_date', 'courier_id', 'date'),
        {'extend_existing': True}
    )

    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    status = Column(
        Enum(AttendanceStatus, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    hours_worked = Column(Integer, default=0)
    notes = Column(String)

    # Relationships
    courier = relationship("Courier", back_populates="attendance_records")
