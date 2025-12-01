from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
from decimal import Decimal
from enum import Enum

class LoanStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class LoanBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    amount: Decimal = Field(..., ge=0, decimal_places=2)
    monthly_deduction: Decimal = Field(..., ge=0, decimal_places=2)
    start_date: date

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, ge=0)
    outstanding_balance: Optional[Decimal] = Field(None, ge=0)
    monthly_deduction: Optional[Decimal] = Field(None, ge=0)
    status: Optional[LoanStatus] = None

class LoanResponse(LoanBase):
    id: int
    outstanding_balance: Decimal
    status: LoanStatus
    created_at: date
    updated_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)
