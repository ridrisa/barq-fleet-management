"""
Payroll Calculation Schemas

Pydantic schemas for category-based salary calculation based on salary.md spec.
"""

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PayrollCategoryEnum(str, Enum):
    """Payroll category enumeration for API schemas"""
    MOTORCYCLE = "Motorcycle"
    FOOD_TRIAL = "Food Trial"
    FOOD_INHOUSE_NEW = "Food In-House New"
    FOOD_INHOUSE_OLD = "Food In-House Old"
    ECOMMERCE_WH = "Ecommerce WH"
    ECOMMERCE = "Ecommerce"
    AJEER = "Ajeer"


class CourierPayrollInput(BaseModel):
    """
    Input data for courier payroll calculation.

    Maps to salary.md section 2 required inputs.
    """
    # Courier identification
    barq_id: str = Field(..., description="BARQ ID")
    courier_id: Optional[int] = Field(None, description="Database courier ID")
    iban: Optional[str] = Field(None, description="Bank IBAN")
    id_number: Optional[str] = Field(None, description="National/Iqama ID")
    name: str = Field(..., description="Courier name")

    # Status
    status: str = Field(..., description="Employment status")
    sponsorship_status: Optional[str] = Field(None, description="Sponsorship type")
    project: Optional[str] = Field(None, description="Project/vertical assignment")
    supervisor: Optional[str] = Field(None, description="Supervisor name")

    # Dates
    joining_date: date = Field(..., description="Employment start date")

    # Performance metrics (from BigQuery for the period)
    total_orders: int = Field(0, ge=0, description="Total orders in period")
    total_revenue: Decimal = Field(Decimal("0"), ge=0, description="Total revenue in period")
    gas_usage: Decimal = Field(Decimal("0"), ge=0, description="Gas usage without VAT")

    # Target
    target: Decimal = Field(Decimal("0"), ge=0, description="Daily target from targets table")

    # Category (can be auto-determined or specified)
    category: Optional[PayrollCategoryEnum] = Field(None, description="Payroll category")


class PeriodInput(BaseModel):
    """Period specification for payroll calculation"""
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    year: int = Field(..., ge=2000, le=2100, description="Year")

    @property
    def start_date(self) -> date:
        """
        Calculate period start date per salary.md section 2.1

        For month M, year Y:
        - If month == 1: start = (year-1)-12-25
        - Else: start = year-(month-1)-25
        """
        if self.month == 1:
            return date(self.year - 1, 12, 25)
        else:
            return date(self.year, self.month - 1, 25)

    @property
    def end_date(self) -> date:
        """
        Calculate period end date per salary.md section 2.1

        For month M, year Y:
        - end = year-month-24
        """
        return date(self.year, self.month, 24)


class PayrollCalculationResult(BaseModel):
    """
    Result of payroll calculation per salary.md section 6.

    Complete output structure for a courier's calculated salary.
    """
    # Courier identification
    barq_id: str
    courier_id: Optional[int] = None
    iban: Optional[str] = None
    id_number: Optional[str] = None
    name: str
    status: str
    sponsorship_status: Optional[str] = None
    project: Optional[str] = None
    supervisor: Optional[str] = None

    # Performance metrics
    total_orders: int = 0
    total_revenue: Decimal = Decimal("0")
    gas_usage: Decimal = Decimal("0")

    # Calculated salary components
    basic_salary: Decimal = Field(Decimal("0"), description="Calculated base salary")
    bonus_amount: Decimal = Field(Decimal("0"), description="Bonus/penalty amount")
    gas_deserved: Decimal = Field(Decimal("0"), description="Calculated gas allowance")
    gas_difference: Decimal = Field(Decimal("0"), description="Gas deserved - gas usage")
    total_salary: Decimal = Field(Decimal("0"), description="Final total salary")

    # Target info
    target: Decimal = Field(Decimal("0"), description="Final calculated target")
    days_since_joining: int = Field(0, description="Days since joining")

    # Period info
    period: Dict[str, str] = Field(default_factory=dict, description="Period start/end dates")
    generated_date: str = Field("", description="Calculation date")

    # Category used
    category: PayrollCategoryEnum

    # Additional breakdown (optional)
    calculation_details: Optional[Dict[str, Any]] = Field(
        None, description="Detailed calculation breakdown"
    )

    model_config = ConfigDict(from_attributes=True)


class BatchPayrollRequest(BaseModel):
    """Request for batch payroll calculation"""
    period: PeriodInput
    courier_ids: Optional[List[int]] = Field(None, description="Specific courier IDs to calculate")
    categories: Optional[List[PayrollCategoryEnum]] = Field(
        None, description="Filter by categories"
    )
    include_inactive: bool = Field(False, description="Include inactive couriers")


class BatchPayrollResponse(BaseModel):
    """Response for batch payroll calculation"""
    period: Dict[str, str]
    total_couriers: int
    successful: int
    failed: int
    skipped: int  # e.g., Ajeer category
    results: List[PayrollCalculationResult]
    errors: List[Dict[str, str]] = Field(default_factory=list)

    # Summary statistics
    total_basic_salary: Decimal = Decimal("0")
    total_bonus: Decimal = Decimal("0")
    total_gas_deserved: Decimal = Decimal("0")
    total_payroll: Decimal = Decimal("0")


class CourierTargetCreate(BaseModel):
    """Schema for creating courier target"""
    courier_id: int
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=2100)
    daily_target: Decimal = Field(..., ge=0)
    category: Optional[PayrollCategoryEnum] = None
    notes: Optional[str] = None


class CourierTargetResponse(CourierTargetCreate):
    """Schema for courier target response"""
    id: int
    organization_id: int

    model_config = ConfigDict(from_attributes=True)


class PayrollParametersCreate(BaseModel):
    """Schema for creating/updating payroll parameters"""
    category: PayrollCategoryEnum
    basic_salary_rate: Decimal
    bonus_rate: Optional[Decimal] = None
    penalty_rate: Optional[Decimal] = Decimal("10")
    gas_rate: Optional[Decimal] = None
    gas_cap: Optional[Decimal] = None
    revenue_coefficient: Optional[Decimal] = None
    daily_order_divisor: Optional[Decimal] = None
    tier_threshold: Optional[int] = None
    tier_1_rate: Optional[Decimal] = None
    tier_2_rate: Optional[Decimal] = None
    bonus_revenue_threshold: Optional[Decimal] = None
    bonus_rate_below_threshold: Optional[Decimal] = None
    bonus_rate_above_threshold: Optional[Decimal] = None
    fuel_revenue_coefficient: Optional[Decimal] = None
    fuel_target_coefficient: Optional[Decimal] = None
    description: Optional[str] = None


class PayrollParametersResponse(PayrollParametersCreate):
    """Schema for payroll parameters response"""
    id: int
    organization_id: int
    is_active: int

    model_config = ConfigDict(from_attributes=True)


class SalaryExtendedResponse(BaseModel):
    """Extended salary response with category-based fields"""
    id: int
    courier_id: int
    month: int
    year: int

    # Category info
    category: Optional[PayrollCategoryEnum] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None

    # Performance metrics
    total_orders: int = 0
    total_revenue: Decimal = Decimal("0")
    gas_usage: Decimal = Decimal("0")

    # Targets
    target: Decimal = Decimal("0")
    daily_target: Decimal = Decimal("0")
    days_since_joining: int = 0

    # Calculated components
    base_salary: Decimal
    bonus_amount: Decimal = Decimal("0")
    gas_deserved: Decimal = Decimal("0")
    gas_difference: Decimal = Decimal("0")

    # Legacy components
    allowances: Decimal = Decimal("0")
    deductions: Decimal = Decimal("0")
    loan_deduction: Decimal = Decimal("0")
    gosi_employee: Decimal = Decimal("0")

    # Totals
    gross_salary: Decimal
    net_salary: Decimal

    # Payment
    payment_date: Optional[date] = None
    is_paid: int = 0

    # Audit
    notes: Optional[str] = None
    calculation_details: Optional[str] = None
    generated_date: Optional[date] = None

    # Courier info (optional join)
    courier_name: Optional[str] = None
    courier_barq_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PayrollSummary(BaseModel):
    """Summary statistics for payroll period"""
    period: Dict[str, str]
    total_couriers: int
    by_category: Dict[str, int]

    total_base_salary: Decimal
    total_bonus: Decimal
    total_penalties: Decimal  # Negative bonus amounts
    total_gas_deserved: Decimal
    total_gas_difference: Decimal
    total_payroll: Decimal

    paid_count: int
    unpaid_count: int
    average_salary: Decimal
