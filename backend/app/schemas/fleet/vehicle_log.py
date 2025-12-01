from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime, time
from decimal import Decimal

from app.models.fleet import LogType, FuelProvider


class VehicleLogBase(BaseModel):
    """Base vehicle log schema"""
    vehicle_id: int
    courier_id: Optional[int] = None
    log_type: LogType = LogType.DAILY_LOG
    log_date: date
    log_time: Optional[time] = None

    start_mileage: Optional[Decimal] = Field(None, ge=0)
    end_mileage: Optional[Decimal] = Field(None, ge=0)
    distance_covered: Optional[Decimal] = Field(None, ge=0)

    start_location: Optional[str] = Field(None, max_length=300)
    end_location: Optional[str] = Field(None, max_length=300)
    route_description: Optional[str] = None

    fuel_refilled: Optional[Decimal] = Field(None, ge=0)
    fuel_cost: Optional[Decimal] = Field(None, ge=0)
    fuel_provider: Optional[FuelProvider] = None
    fuel_station_location: Optional[str] = Field(None, max_length=300)
    fuel_receipt_number: Optional[str] = Field(None, max_length=100)

    number_of_deliveries: int = Field(default=0, ge=0)
    number_of_orders: int = Field(default=0, ge=0)
    revenue_generated: Decimal = Field(default=0.0, ge=0)

    vehicle_condition: Optional[str] = Field(None, max_length=50)
    issues_reported: Optional[str] = None
    has_issues: bool = False

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    working_hours: Optional[Decimal] = Field(None, ge=0)

    weather_conditions: Optional[str] = Field(None, max_length=100)
    traffic_conditions: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    recorded_by: Optional[str] = Field(None, max_length=200)

    receipt_image_url: Optional[str] = Field(None, max_length=500)
    log_photo_urls: Optional[str] = None


class VehicleLogCreate(VehicleLogBase):
    """Schema for creating vehicle log"""
    pass


class VehicleLogUpdate(BaseModel):
    """Schema for updating vehicle log"""
    log_type: Optional[LogType] = None
    log_time: Optional[time] = None
    end_mileage: Optional[Decimal] = Field(None, ge=0)
    distance_covered: Optional[Decimal] = Field(None, ge=0)
    fuel_refilled: Optional[Decimal] = Field(None, ge=0)
    fuel_cost: Optional[Decimal] = Field(None, ge=0)
    number_of_deliveries: Optional[int] = Field(None, ge=0)
    revenue_generated: Optional[Decimal] = Field(None, ge=0)
    vehicle_condition: Optional[str] = None
    issues_reported: Optional[str] = None
    has_issues: Optional[bool] = None
    notes: Optional[str] = None


class VehicleLogResponse(VehicleLogBase):
    """Schema for vehicle log response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    fuel_efficiency: float = 0.0
    cost_per_km: float = 0.0
    revenue_per_delivery: float = 0.0

    class Config:
        from_attributes = True


class VehicleLogList(BaseModel):
    """Minimal schema for list views"""
    id: int
    vehicle_id: int
    log_type: LogType
    log_date: date
    distance_covered: Optional[Decimal] = None
    fuel_refilled: Optional[Decimal] = None
    number_of_deliveries: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
