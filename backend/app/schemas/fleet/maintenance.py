from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

from app.models.fleet import MaintenanceType, MaintenanceStatus, ServiceProvider


class MaintenanceBase(BaseModel):
    """Base maintenance schema"""
    vehicle_id: int
    maintenance_type: MaintenanceType
    status: MaintenanceStatus = MaintenanceStatus.SCHEDULED
    service_provider: ServiceProvider = ServiceProvider.THIRD_PARTY

    scheduled_date: Optional[date] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None

    mileage_at_service: Optional[Decimal] = Field(None, ge=0)

    service_description: str = Field(..., min_length=1)
    work_performed: Optional[str] = None
    parts_replaced: Optional[str] = None
    parts_list_json: Optional[str] = None

    service_center_name: Optional[str] = Field(None, max_length=300)
    service_center_location: Optional[str] = Field(None, max_length=300)
    technician_name: Optional[str] = Field(None, max_length=200)
    technician_phone: Optional[str] = Field(None, max_length=20)

    labor_cost: Decimal = Field(default=0.0, ge=0)
    parts_cost: Decimal = Field(default=0.0, ge=0)
    total_cost: Decimal = Field(..., ge=0)
    tax_amount: Decimal = Field(default=0.0, ge=0)
    discount_amount: Decimal = Field(default=0.0, ge=0)

    payment_method: Optional[str] = Field(None, max_length=50)
    invoice_number: Optional[str] = Field(None, max_length=100)
    invoice_date: Optional[date] = None
    payment_status: str = Field(default="pending", max_length=50)

    has_warranty: bool = False
    warranty_expiry_date: Optional[date] = None
    warranty_details: Optional[str] = None

    next_service_date: Optional[date] = None
    next_service_mileage: Optional[Decimal] = Field(None, ge=0)

    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    approved_by: Optional[str] = Field(None, max_length=200)
    approval_date: Optional[date] = None

    issues_found: Optional[str] = None
    recommendations: Optional[str] = None
    notes: Optional[str] = None

    invoice_image_url: Optional[str] = Field(None, max_length=500)
    report_file_url: Optional[str] = Field(None, max_length=500)
    photos_json: Optional[str] = None

    vehicle_downtime_hours: Optional[Decimal] = Field(None, ge=0)


class MaintenanceCreate(MaintenanceBase):
    """Schema for creating maintenance record"""
    pass


class MaintenanceUpdate(BaseModel):
    """Schema for updating maintenance record"""
    status: Optional[MaintenanceStatus] = None
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    work_performed: Optional[str] = None
    parts_replaced: Optional[str] = None
    total_cost: Optional[Decimal] = Field(None, ge=0)
    payment_status: Optional[str] = None
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None


class MaintenanceResponse(MaintenanceBase):
    """Schema for maintenance response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_completed: bool = False
    is_overdue: bool = False
    total_with_tax: float = 0.0
    net_cost: float = 0.0
    duration_days: int = 0

    class Config:
        from_attributes = True


class MaintenanceList(BaseModel):
    """Minimal schema for list views"""
    id: int
    vehicle_id: int
    maintenance_type: MaintenanceType
    status: MaintenanceStatus
    scheduled_date: Optional[date] = None
    total_cost: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
