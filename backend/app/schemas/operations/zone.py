from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ZoneStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class ZoneBase(BaseModel):
    zone_code: str = Field(..., min_length=2, max_length=50, description="Unique zone code")
    zone_name: str = Field(..., min_length=3, max_length=200, description="Zone name")
    description: Optional[str] = None
    city: str = Field(..., min_length=2, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    boundaries: Optional[Dict[str, Any]] = Field(None, description="GeoJSON polygon")
    center_latitude: Optional[float] = Field(None, ge=-90, le=90)
    center_longitude: Optional[float] = Field(None, ge=-180, le=180)
    coverage_area_km2: Optional[float] = Field(None, ge=0)
    estimated_population: Optional[int] = Field(None, ge=0)
    business_density: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    priority_level: int = Field(1, ge=1, le=5, description="Priority level 1-5")
    max_couriers: int = Field(10, ge=1, le=100, description="Maximum couriers")
    service_fee: float = Field(0.0, ge=0)
    peak_hour_multiplier: float = Field(1.0, ge=1.0, le=3.0)
    minimum_order_value: float = Field(0.0, ge=0)
    notes: Optional[str] = None
    special_instructions: Optional[str] = None


class ZoneCreate(ZoneBase):
    status: ZoneStatus = ZoneStatus.ACTIVE


class ZoneUpdate(BaseModel):
    zone_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    district: Optional[str] = None
    postal_code: Optional[str] = None
    boundaries: Optional[Dict[str, Any]] = None
    center_latitude: Optional[float] = Field(None, ge=-90, le=90)
    center_longitude: Optional[float] = Field(None, ge=-180, le=180)
    coverage_area_km2: Optional[float] = Field(None, ge=0)
    estimated_population: Optional[int] = Field(None, ge=0)
    business_density: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    status: Optional[ZoneStatus] = None
    priority_level: Optional[int] = Field(None, ge=1, le=5)
    max_couriers: Optional[int] = Field(None, ge=1, le=100)
    service_fee: Optional[float] = Field(None, ge=0)
    peak_hour_multiplier: Optional[float] = Field(None, ge=1.0, le=3.0)
    minimum_order_value: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    special_instructions: Optional[str] = None


class ZoneResponse(ZoneBase):
    id: int
    status: ZoneStatus
    current_couriers: int
    avg_delivery_time_minutes: float
    total_deliveries_completed: int
    success_rate: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ZoneMetrics(BaseModel):
    """Zone performance metrics"""
    zone_id: int
    zone_code: str
    zone_name: str
    current_couriers: int
    max_couriers: int
    utilization_rate: float
    avg_delivery_time_minutes: float
    total_deliveries_today: int
    success_rate: float
    is_at_capacity: bool

    model_config = ConfigDict(from_attributes=True)
