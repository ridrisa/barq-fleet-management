from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BonusType(str, Enum):
    PERFORMANCE = "performance"
    ATTENDANCE = "attendance"
    SEASONAL = "seasonal"
    SPECIAL = "special"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"


class BonusBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    bonus_type: BonusType
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    bonus_date: date
    description: Optional[str] = None
    notes: Optional[str] = None


class BonusCreate(BonusBase):
    pass


class BonusUpdate(BaseModel):
    bonus_type: Optional[BonusType] = None
    amount: Optional[Decimal] = Field(None, ge=0)
    bonus_date: Optional[date] = None
    payment_status: Optional[PaymentStatus] = None
    approved_by: Optional[int] = None
    approval_date: Optional[date] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class BonusResponse(BonusBase):
    id: int
    payment_status: PaymentStatus
    approved_by: Optional[int] = None
    approval_date: Optional[date] = None
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
