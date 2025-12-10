from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

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
    courier_name: Optional[str] = None
    vehicle_plate_number: Optional[str] = None
    status: AssignmentStatus
    start_date: date
    end_date: Optional[date] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CurrentAssignment(BaseModel):
    """Schema for current vehicle-courier assignments derived from couriers.current_vehicle_id"""

    courier_id: int
    courier_name: str
    courier_employee_id: Optional[str] = None
    courier_status: str
    vehicle_id: int
    vehicle_plate_number: str
    vehicle_make: str
    vehicle_model: str
    vehicle_status: str

    class Config:
        from_attributes = True
