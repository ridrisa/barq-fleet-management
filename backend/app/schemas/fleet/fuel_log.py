from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class FuelLogBase(BaseModel):
    """Base fuel log schema"""
    vehicle_id: int
    courier_id: Optional[int] = None
    fuel_date: date
    odometer_reading: Decimal = Field(ge=0)
    fuel_quantity: Decimal = Field(ge=0)  # Liters
    fuel_cost: Decimal = Field(ge=0)
    cost_per_liter: Decimal = Field(ge=0)
    fuel_station: Optional[str] = Field(None, max_length=200)
    fuel_type: Optional[str] = Field(None, max_length=50)
    receipt_number: Optional[str] = Field(None, max_length=100)
    receipt_image_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)


class FuelLogCreate(FuelLogBase):
    """Schema for creating fuel log"""
    pass


class FuelLogUpdate(BaseModel):
    """Schema for updating fuel log"""
    fuel_date: Optional[date] = None
    odometer_reading: Optional[Decimal] = Field(None, ge=0)
    fuel_quantity: Optional[Decimal] = Field(None, ge=0)
    fuel_cost: Optional[Decimal] = Field(None, ge=0)
    cost_per_liter: Optional[Decimal] = Field(None, ge=0)
    fuel_station: Optional[str] = Field(None, max_length=200)
    fuel_type: Optional[str] = Field(None, max_length=50)
    receipt_number: Optional[str] = Field(None, max_length=100)
    receipt_image_url: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)


class FuelLogResponse(FuelLogBase):
    """Schema for fuel log response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FuelLogSummary(BaseModel):
    """Fuel consumption summary"""
    total_fuel_quantity: Decimal
    total_fuel_cost: Decimal
    average_cost_per_liter: Decimal
    total_distance: Decimal
    average_consumption: Decimal  # km per liter
    log_count: int
