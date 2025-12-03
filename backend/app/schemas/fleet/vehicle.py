from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.models.fleet import FuelType, OwnershipType, VehicleStatus, VehicleType


# Base schema
class VehicleBase(BaseModel):
    """Base vehicle schema with common fields"""

    plate_number: str = Field(..., min_length=1, max_length=20, description="License plate number")
    vehicle_type: VehicleType
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1990, le=2030)
    color: Optional[str] = Field(None, max_length=50)

    status: VehicleStatus = VehicleStatus.ACTIVE
    ownership_type: OwnershipType = OwnershipType.OWNED

    registration_number: Optional[str] = Field(None, max_length=50)
    registration_expiry_date: Optional[date] = None
    insurance_company: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[date] = None

    vin_number: Optional[str] = Field(None, max_length=50)
    engine_number: Optional[str] = Field(None, max_length=50)
    engine_capacity: Optional[str] = Field(None, max_length=20)
    transmission: Optional[str] = Field(None, max_length=20)

    fuel_type: FuelType = FuelType.GASOLINE
    current_mileage: Decimal = Field(default=0.0, ge=0)
    fuel_capacity: Optional[Decimal] = Field(None, ge=0)

    purchase_price: Optional[Decimal] = Field(None, ge=0)
    purchase_date: Optional[date] = None
    monthly_lease_cost: Optional[Decimal] = Field(None, ge=0)
    depreciation_rate: Decimal = Field(default=20.0, ge=0, le=100)

    last_service_date: Optional[date] = None
    last_service_mileage: Optional[Decimal] = Field(None, ge=0)
    next_service_due_date: Optional[date] = None
    next_service_due_mileage: Optional[Decimal] = Field(None, ge=0)

    gps_device_id: Optional[str] = Field(None, max_length=100)
    gps_device_imei: Optional[str] = Field(None, max_length=50)
    is_gps_active: bool = False

    assigned_to_city: Optional[str] = Field(None, max_length=100)
    assigned_to_project: Optional[str] = Field(None, max_length=100)

    notes: Optional[str] = None
    is_pool_vehicle: bool = False

    # FMS Integration fields
    fms_asset_id: Optional[int] = None
    fms_tracking_unit_id: Optional[int] = None
    fms_last_sync: Optional[datetime] = None


# Schema for creating a vehicle
class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle"""

    pass


# Schema for updating a vehicle
class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle - all fields optional"""

    plate_number: Optional[str] = Field(None, min_length=1, max_length=20)
    vehicle_type: Optional[VehicleType] = None
    make: Optional[str] = Field(None, min_length=1, max_length=100)
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    year: Optional[int] = Field(None, ge=1990, le=2030)
    color: Optional[str] = Field(None, max_length=50)

    status: Optional[VehicleStatus] = None
    ownership_type: Optional[OwnershipType] = None

    registration_number: Optional[str] = Field(None, max_length=50)
    registration_expiry_date: Optional[date] = None
    insurance_company: Optional[str] = Field(None, max_length=200)
    insurance_policy_number: Optional[str] = Field(None, max_length=100)
    insurance_expiry_date: Optional[date] = None

    vin_number: Optional[str] = Field(None, max_length=50)
    engine_number: Optional[str] = Field(None, max_length=50)
    engine_capacity: Optional[str] = Field(None, max_length=20)
    transmission: Optional[str] = Field(None, max_length=20)

    fuel_type: Optional[FuelType] = None
    current_mileage: Optional[Decimal] = Field(None, ge=0)
    fuel_capacity: Optional[Decimal] = Field(None, ge=0)

    purchase_price: Optional[Decimal] = Field(None, ge=0)
    purchase_date: Optional[date] = None
    monthly_lease_cost: Optional[Decimal] = Field(None, ge=0)
    depreciation_rate: Optional[Decimal] = Field(None, ge=0, le=100)

    last_service_date: Optional[date] = None
    last_service_mileage: Optional[Decimal] = Field(None, ge=0)
    next_service_due_date: Optional[date] = None
    next_service_due_mileage: Optional[Decimal] = Field(None, ge=0)

    gps_device_id: Optional[str] = Field(None, max_length=100)
    gps_device_imei: Optional[str] = Field(None, max_length=50)
    is_gps_active: Optional[bool] = None

    assigned_to_city: Optional[str] = Field(None, max_length=100)
    assigned_to_project: Optional[str] = Field(None, max_length=100)

    notes: Optional[str] = None
    is_pool_vehicle: Optional[bool] = None

    total_trips: Optional[int] = Field(None, ge=0)
    total_distance: Optional[Decimal] = Field(None, ge=0)
    avg_fuel_consumption: Optional[Decimal] = Field(None, ge=0)

    # FMS Integration fields
    fms_asset_id: Optional[int] = None
    fms_tracking_unit_id: Optional[int] = None
    fms_last_sync: Optional[datetime] = None


# Schema for vehicle response
class VehicleResponse(VehicleBase):
    """Schema for vehicle response with database fields"""

    id: int
    total_trips: int = 0
    total_distance: Decimal = 0.0
    avg_fuel_consumption: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Computed properties
    is_available: bool = Field(
        default=True, description="Whether vehicle is available for assignment"
    )
    is_service_due: bool = Field(default=False, description="Whether service is due")
    is_document_expired: bool = Field(default=False, description="Whether any document is expired")
    age_years: int = Field(default=0, description="Vehicle age in years")

    class Config:
        from_attributes = True


# Schema for vehicle list
class VehicleList(BaseModel):
    """Minimal vehicle schema for list views"""

    id: int
    plate_number: str
    vehicle_type: VehicleType
    make: str
    model: str
    year: int
    status: VehicleStatus
    current_mileage: Decimal
    assigned_to_city: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Schema for vehicle dropdown/select
class VehicleOption(BaseModel):
    """Minimal schema for dropdown selections"""

    id: int
    plate_number: str
    vehicle_type: VehicleType
    make: str
    model: str
    status: VehicleStatus

    class Config:
        from_attributes = True


# Schema for vehicle statistics
class VehicleStats(BaseModel):
    """Statistics for a vehicle"""

    vehicle_id: int
    plate_number: str
    total_trips: int = 0
    total_distance_km: Decimal = 0.0
    total_fuel_liters: Decimal = 0.0
    total_fuel_cost: Decimal = 0.0
    avg_fuel_efficiency: Decimal = 0.0
    maintenance_count: int = 0
    maintenance_cost: Decimal = 0.0
    accident_count: int = 0
    downtime_days: int = 0


# Schema for vehicle document status
class VehicleDocumentStatus(BaseModel):
    """Document expiry status for a vehicle"""

    vehicle_id: int
    plate_number: str
    registration_expiry_date: Optional[date] = None
    registration_expired: bool = False
    registration_expires_soon: bool = False
    insurance_expiry_date: Optional[date] = None
    insurance_expired: bool = False
    insurance_expires_soon: bool = False
    any_expired: bool = False
    any_expires_soon: bool = False

    class Config:
        from_attributes = True


# Schema for bulk operations
class VehicleBulkUpdate(BaseModel):
    """Schema for bulk updating multiple vehicles"""

    vehicle_ids: list[int] = Field(..., min_items=1)
    status: Optional[VehicleStatus] = None
    assigned_to_city: Optional[str] = None
    assigned_to_project: Optional[str] = None
