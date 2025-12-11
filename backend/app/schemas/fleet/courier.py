from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

# Enums (matching SQLAlchemy enums)
from app.models.fleet import CourierStatus, ProjectType, SponsorshipStatus


# Base schema with common fields
class CourierBase(BaseModel):
    """Base courier schema with common fields"""

    barq_id: str = Field(..., min_length=1, max_length=50, description="Unique BARQ identifier")
    full_name: str = Field(..., min_length=2, max_length=200)
    email: Optional[str] = None  # Using str instead of EmailStr to handle legacy invalid emails
    mobile_number: str = Field(..., pattern=r"^\+?[0-9]{9,15}$")

    employee_id: Optional[str] = Field(None, max_length=50)
    status: CourierStatus = CourierStatus.ONBOARDING
    sponsorship_status: SponsorshipStatus = SponsorshipStatus.INHOUSE
    project_type: ProjectType = ProjectType.BARQ
    position: str = Field(default="Courier", max_length=100)
    city: Optional[str] = Field(None, max_length=100)

    joining_date: Optional[date] = None
    date_of_birth: Optional[date] = None

    national_id: Optional[str] = Field(None, max_length=50)
    nationality: Optional[str] = Field(None, max_length=100)
    iqama_number: Optional[str] = Field(None, max_length=50)
    iqama_expiry_date: Optional[date] = None
    passport_number: Optional[str] = Field(None, max_length=50)
    passport_expiry_date: Optional[date] = None

    license_number: Optional[str] = Field(None, max_length=50)
    license_expiry_date: Optional[date] = None
    license_type: Optional[str] = Field(None, max_length=20)

    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    iban: Optional[str] = Field(None, max_length=50)

    jahez_driver_id: Optional[str] = Field(None, max_length=50)
    hunger_rider_id: Optional[str] = Field(None, max_length=50)
    mrsool_courier_id: Optional[str] = Field(None, max_length=50)

    current_vehicle_id: Optional[int] = None
    supervisor_name: Optional[str] = Field(None, max_length=200)

    accommodation_building_id: Optional[int] = None
    accommodation_room_id: Optional[int] = None

    notes: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{9,15}$")

    # FMS Integration fields
    fms_asset_id: Optional[int] = None
    fms_driver_id: Optional[int] = None
    fms_last_sync: Optional[datetime] = None


# Schema for creating a new courier
class CourierCreate(CourierBase):
    """Schema for creating a new courier"""

    pass


# Schema for updating a courier
class CourierUpdate(BaseModel):
    """Schema for updating a courier - all fields optional"""

    barq_id: Optional[str] = Field(None, min_length=1, max_length=50)
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[str] = None  # Using str instead of EmailStr to handle legacy invalid emails
    mobile_number: Optional[str] = Field(None, pattern=r"^\+?[0-9]{9,15}$")

    employee_id: Optional[str] = Field(None, max_length=50)
    status: Optional[CourierStatus] = None
    sponsorship_status: Optional[SponsorshipStatus] = None
    project_type: Optional[ProjectType] = None
    position: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)

    joining_date: Optional[date] = None
    last_working_day: Optional[date] = None
    date_of_birth: Optional[date] = None

    national_id: Optional[str] = Field(None, max_length=50)
    nationality: Optional[str] = Field(None, max_length=100)
    iqama_number: Optional[str] = Field(None, max_length=50)
    iqama_expiry_date: Optional[date] = None
    passport_number: Optional[str] = Field(None, max_length=50)
    passport_expiry_date: Optional[date] = None

    license_number: Optional[str] = Field(None, max_length=50)
    license_expiry_date: Optional[date] = None
    license_type: Optional[str] = Field(None, max_length=20)

    bank_account_number: Optional[str] = Field(None, max_length=50)
    bank_name: Optional[str] = Field(None, max_length=100)
    iban: Optional[str] = Field(None, max_length=50)

    jahez_driver_id: Optional[str] = Field(None, max_length=50)
    hunger_rider_id: Optional[str] = Field(None, max_length=50)
    mrsool_courier_id: Optional[str] = Field(None, max_length=50)

    current_vehicle_id: Optional[int] = None
    supervisor_name: Optional[str] = Field(None, max_length=200)

    accommodation_building_id: Optional[int] = None
    accommodation_room_id: Optional[int] = None

    notes: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=200)
    emergency_contact_phone: Optional[str] = Field(None, pattern=r"^\+?[0-9]{9,15}$")

    performance_score: Optional[Decimal] = Field(None, ge=0, le=100)
    total_deliveries: Optional[int] = Field(None, ge=0)

    # FMS Integration fields
    fms_asset_id: Optional[int] = None
    fms_driver_id: Optional[int] = None
    fms_last_sync: Optional[datetime] = None


# Schema for courier response
class CourierResponse(CourierBase):
    """Schema for courier response with database fields"""

    id: int
    last_working_day: Optional[date] = None
    performance_score: Optional[Decimal] = Field(default=Decimal("0"))
    total_deliveries: Optional[int] = Field(default=0, ge=0)  # Made Optional to handle NULL values
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Override base fields to make them optional for legacy data with NULL values
    sponsorship_status: Optional[SponsorshipStatus] = None
    project_type: Optional[ProjectType] = None
    position: Optional[str] = Field(None, max_length=100)

    # Computed properties
    is_active: bool = Field(default=False, description="Whether courier is actively working")
    has_vehicle: bool = Field(default=False, description="Whether courier has assigned vehicle")
    is_document_expired: bool = Field(default=False, description="Whether any document is expired")

    @field_validator("total_deliveries", mode="before")
    @classmethod
    def default_total_deliveries(cls, v):
        return v if v is not None else 0

    class Config:
        from_attributes = True


# Schema for courier list (minimal fields)
class CourierList(BaseModel):
    """Minimal courier schema for list views"""

    id: int
    barq_id: str
    full_name: str
    email: Optional[str] = None  # Using str instead of EmailStr to handle legacy invalid emails
    mobile_number: str
    status: CourierStatus
    city: Optional[str] = None
    current_vehicle_id: Optional[int] = None
    performance_score: Optional[Decimal] = None
    created_at: datetime

    @field_validator("performance_score", mode="before")
    @classmethod
    def default_performance_score(cls, v):
        return v if v is not None else Decimal("0")

    class Config:
        from_attributes = True


# Schema for courier dropdown/select
class CourierOption(BaseModel):
    """Minimal schema for dropdown selections"""

    id: int
    barq_id: str
    full_name: str
    status: CourierStatus

    class Config:
        from_attributes = True


# Schema for bulk operations
class CourierBulkUpdate(BaseModel):
    """Schema for bulk updating multiple couriers"""

    courier_ids: list[int] = Field(..., min_items=1)
    status: Optional[CourierStatus] = None
    city: Optional[str] = None
    supervisor_name: Optional[str] = None
    project_type: Optional[ProjectType] = None


# Schema for courier statistics
class CourierStats(BaseModel):
    """Statistics for a courier"""

    courier_id: int
    total_deliveries: int = 0
    total_distance_km: Decimal = 0.0
    total_trips: int = 0
    avg_deliveries_per_day: Decimal = 0.0
    performance_score: Decimal = 0.0
    accidents_count: int = 0
    leaves_taken: int = 0


# Schema for document expiry check
class CourierDocumentStatus(BaseModel):
    """Document expiry status for a courier"""

    courier_id: int
    barq_id: str
    full_name: str
    iqama_expiry_date: Optional[date] = None
    iqama_expired: bool = False
    iqama_expires_soon: bool = False
    passport_expiry_date: Optional[date] = None
    passport_expired: bool = False
    passport_expires_soon: bool = False
    license_expiry_date: Optional[date] = None
    license_expired: bool = False
    license_expires_soon: bool = False
    any_expired: bool = False
    any_expires_soon: bool = False

    class Config:
        from_attributes = True
