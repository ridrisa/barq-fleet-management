from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from decimal import Decimal
from enum import Enum

class CODStatus(str, Enum):
    PENDING = "pending"
    COLLECTED = "collected"
    DEPOSITED = "deposited"
    RECONCILED = "reconciled"

class CODBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    collection_date: date
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class CODCreate(CODBase):
    pass

class CODUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, ge=0)
    collection_date: Optional[date] = None
    deposit_date: Optional[date] = None
    status: Optional[CODStatus] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class CODResponse(CODBase):
    id: int
    deposit_date: Optional[date] = None
    status: CODStatus
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
