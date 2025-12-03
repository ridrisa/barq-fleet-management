from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HandoverStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class HandoverType(str, Enum):
    SHIFT_START = "shift_start"
    SHIFT_END = "shift_end"
    VEHICLE_SWAP = "vehicle_swap"
    EMERGENCY = "emergency"
    MAINTENANCE = "maintenance"


class HandoverBase(BaseModel):
    handover_type: HandoverType
    from_courier_id: int = Field(..., description="Courier handing over")
    to_courier_id: int = Field(..., description="Courier receiving")
    vehicle_id: Optional[int] = None
    vehicle_mileage_start: Optional[int] = Field(None, ge=0)
    vehicle_fuel_level: Optional[Decimal] = Field(None, ge=0, le=100)
    vehicle_condition: Optional[str] = None
    pending_deliveries_count: int = Field(0, ge=0)
    pending_cod_amount: Decimal = Field(Decimal("0.0"), ge=0)
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    special_instructions: Optional[str] = None

    @field_validator("from_courier_id", "to_courier_id")
    @classmethod
    def validate_courier_ids(cls, v):
        if v <= 0:
            raise ValueError("Courier ID must be positive")
        return v


class HandoverCreate(HandoverBase):
    pass


class HandoverUpdate(BaseModel):
    status: Optional[HandoverStatus] = None
    vehicle_mileage_start: Optional[int] = Field(None, ge=0)
    vehicle_fuel_level: Optional[Decimal] = Field(None, ge=0, le=100)
    vehicle_condition: Optional[str] = None
    pending_deliveries_count: Optional[int] = Field(None, ge=0)
    pending_cod_amount: Optional[Decimal] = Field(None, ge=0)
    from_courier_signature: Optional[str] = None
    to_courier_signature: Optional[str] = None
    witness_id: Optional[int] = None
    photos: Optional[str] = None
    notes: Optional[str] = None
    discrepancies_reported: Optional[str] = None


class HandoverApproval(BaseModel):
    """Schema for approving/rejecting handover"""

    approved: bool
    rejection_reason: Optional[str] = None
    notes: Optional[str] = None


class HandoverCompletion(BaseModel):
    """Schema for completing handover"""

    from_courier_signature: str = Field(..., min_length=1)
    to_courier_signature: str = Field(..., min_length=1)
    vehicle_mileage_start: int = Field(..., ge=0)
    vehicle_fuel_level: Decimal = Field(..., ge=0, le=100)
    vehicle_condition: str
    discrepancies_reported: Optional[str] = None
    photos: Optional[str] = None
    notes: Optional[str] = None


class HandoverResponse(HandoverBase):
    id: int
    handover_number: str
    status: HandoverStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    from_courier_signature: Optional[str] = None
    to_courier_signature: Optional[str] = None
    witness_id: Optional[int] = None
    approved_by_id: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    photos: Optional[str] = None
    discrepancies_reported: Optional[str] = None
    discrepancy_resolved: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class HandoverHistory(BaseModel):
    """Handover history for courier or vehicle"""

    handovers: List[HandoverResponse]
    total_handovers: int
    pending_handovers: int
    completed_handovers: int

    model_config = ConfigDict(from_attributes=True)
