from datetime import date, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"


class AttendanceBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    date: date
    status: AttendanceStatus
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    hours_worked: int = Field(default=0, ge=0, le=24)
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    hours_worked: Optional[int] = Field(None, ge=0, le=24)
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    id: int
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
