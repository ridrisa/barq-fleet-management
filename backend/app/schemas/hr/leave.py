from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from enum import Enum

class LeaveType(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    EMERGENCY = "emergency"
    UNPAID = "unpaid"

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class LeaveBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    leave_type: LeaveType
    start_date: date
    end_date: date
    days: int = Field(..., ge=1)
    reason: Optional[str] = None

class LeaveCreate(LeaveBase):
    pass

class LeaveUpdate(BaseModel):
    leave_type: Optional[LeaveType] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    days: Optional[int] = Field(None, ge=1)
    reason: Optional[str] = None
    status: Optional[LeaveStatus] = None
    approved_by: Optional[int] = None

class LeaveResponse(LeaveBase):
    id: int
    status: LeaveStatus
    approved_by: Optional[int] = None
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
