from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

from app.models.fleet import AssignmentStatus, AssignmentType


class AssignmentBase(BaseModel):
    """Base assignment schema"""
    courier_id: int
    vehicle_id: int
    assignment_type: AssignmentType = AssignmentType.PERMANENT
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    start_date: date
    end_date: Optional[date] = None
    start_mileage: Optional[int] = Field(None, ge=0)
    end_mileage: Optional[int] = Field(None, ge=0)
    assigned_by: Optional[str] = Field(None, max_length=200)
    assignment_reason: Optional[str] = None
    termination_reason: Optional[str] = None
    notes: Optional[str] = None


class AssignmentCreate(AssignmentBase):
    """Schema for creating assignment"""
    pass


class AssignmentUpdate(BaseModel):
    """Schema for updating assignment"""
    status: Optional[AssignmentStatus] = None
    end_date: Optional[date] = None
    end_mileage: Optional[int] = Field(None, ge=0)
    termination_reason: Optional[str] = None
    notes: Optional[str] = None


class AssignmentResponse(AssignmentBase):
    """Schema for assignment response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = False
    duration_days: int = 0
    mileage_used: int = 0

    class Config:
        from_attributes = True


class AssignmentList(BaseModel):
    """Minimal schema for list views"""
    id: int
    courier_id: int
    vehicle_id: int
    status: AssignmentStatus
    start_date: date
    end_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True
