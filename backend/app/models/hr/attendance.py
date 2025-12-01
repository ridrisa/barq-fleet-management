from sqlalchemy import Column, String, Integer, Date, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"

class Attendance(BaseModel):
    __tablename__ = "attendance"

    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(Time, nullable=True)
    check_out = Column(Time, nullable=True)
    status = Column(Enum(AttendanceStatus, values_callable=lambda x: [e.value for e in x]), nullable=False)
    hours_worked = Column(Integer, default=0)
    notes = Column(String)

    # Relationships
    courier = relationship("Courier", back_populates="attendance_records")
