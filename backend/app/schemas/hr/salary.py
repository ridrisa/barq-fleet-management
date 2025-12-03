from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SalaryBase(BaseModel):
    courier_id: int = Field(..., description="Courier ID")
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    base_salary: Decimal = Field(..., ge=0, decimal_places=2)
    allowances: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    deductions: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    loan_deduction: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)
    gosi_employee: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=2)


class SalaryCreate(SalaryBase):
    pass


class SalaryUpdate(BaseModel):
    base_salary: Optional[Decimal] = Field(None, ge=0)
    allowances: Optional[Decimal] = Field(None, ge=0)
    deductions: Optional[Decimal] = Field(None, ge=0)
    loan_deduction: Optional[Decimal] = Field(None, ge=0)
    gosi_employee: Optional[Decimal] = Field(None, ge=0)
    gross_salary: Optional[Decimal] = Field(None, ge=0)
    net_salary: Optional[Decimal] = Field(None, ge=0)


class SalaryResponse(SalaryBase):
    id: int
    gross_salary: Decimal
    net_salary: Decimal
    payment_date: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
