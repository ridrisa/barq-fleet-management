"""
Payroll Category Models and Configuration

Defines courier payroll categories and their calculation parameters
based on the salary.md specification.
"""

import enum
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column, Date, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class PayrollCategory(str, enum.Enum):
    """
    Courier payroll categories for salary calculation.

    Maps to salary.md categories:
    - Motorcycle: Motorcycle delivery couriers
    - Food Trial: Food couriers in trial period
    - Food In-House New: Food couriers (in-house, newer employees)
    - Food In-House Old: Food couriers (in-house, senior employees)
    - Ecommerce WH: E-commerce warehouse couriers
    - Ecommerce: E-commerce delivery couriers
    - Ajeer: External/contracted couriers (excluded from calculation)
    """
    MOTORCYCLE = "Motorcycle"
    FOOD_TRIAL = "Food Trial"
    FOOD_INHOUSE_NEW = "Food In-House New"
    FOOD_INHOUSE_OLD = "Food In-House Old"
    ECOMMERCE_WH = "Ecommerce WH"
    ECOMMERCE = "Ecommerce"
    AJEER = "Ajeer"


class CourierTarget(TenantMixin, BaseModel):
    """
    Courier performance targets for salary calculation.

    Stores the TARGET value from master_saned.targets table
    for each courier in a given period.
    """
    __tablename__ = "courier_targets"
    __table_args__ = (
        UniqueConstraint('courier_id', 'month', 'year', 'organization_id', name='uq_courier_target_period'),
        {'extend_existing': True}
    )

    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # Target value (daily target from targets table)
    daily_target = Column(Numeric(10, 2), nullable=False, default=0)

    # Category for this period (may change over time)
    category = Column(SQLEnum(PayrollCategory, values_callable=lambda e: [m.value for m in e]), nullable=True)

    notes = Column(Text, nullable=True)

    # Relationships
    courier = relationship("Courier", backref="targets")


class PayrollParameters(TenantMixin, BaseModel):
    """
    Configurable salary calculation parameters per category.

    Stores the rates, caps, and coefficients from salary.md section 4.
    Allows organization-level customization of salary formulas.
    """
    __tablename__ = "payroll_parameters"
    __table_args__ = (
        UniqueConstraint('category', 'organization_id', name='uq_payroll_params_category'),
        {'extend_existing': True}
    )

    category = Column(
        SQLEnum(PayrollCategory, values_callable=lambda e: [m.value for m in e]),
        nullable=False
    )

    # Common rates
    basic_salary_rate = Column(Numeric(12, 6), nullable=False, default=0)
    bonus_rate = Column(Numeric(10, 2), nullable=True)  # Per order above target
    penalty_rate = Column(Numeric(10, 2), nullable=True, default=10)  # Per order below target
    gas_rate = Column(Numeric(10, 6), nullable=True)  # Per order or coefficient
    gas_cap = Column(Numeric(10, 2), nullable=True)  # Maximum gas reimbursement

    # Ecommerce-specific
    revenue_coefficient = Column(Numeric(12, 10), nullable=True)  # For revenue-based calculation

    # Daily order divisor for target calculation
    daily_order_divisor = Column(Numeric(10, 6), nullable=True)  # e.g., 13.333 for Motorcycle

    # Tiered bonus thresholds (for Food In-House Old)
    tier_threshold = Column(Integer, nullable=True)  # e.g., 199 for tier change
    tier_1_rate = Column(Numeric(10, 2), nullable=True)  # Rate below threshold
    tier_2_rate = Column(Numeric(10, 2), nullable=True)  # Rate above threshold

    # Ecommerce bonus thresholds
    bonus_revenue_threshold = Column(Numeric(10, 2), nullable=True)  # e.g., 4000 SAR
    bonus_rate_below_threshold = Column(Numeric(10, 4), nullable=True)  # e.g., 0.55
    bonus_rate_above_threshold = Column(Numeric(10, 4), nullable=True)  # e.g., 0.5

    # Fuel calculation coefficients for Ecommerce
    fuel_revenue_coefficient = Column(Numeric(10, 6), nullable=True)  # e.g., 0.068
    fuel_target_coefficient = Column(Numeric(10, 6), nullable=True)  # e.g., 15.06

    description = Column(Text, nullable=True)
    is_active = Column(Integer, default=1)  # Boolean-like for SQLite compatibility


# Default parameters from salary.md section 4
DEFAULT_PAYROLL_PARAMETERS = {
    PayrollCategory.MOTORCYCLE: {
        "basic_salary_rate": Decimal("53.33333"),
        "bonus_rate": Decimal("6"),
        "penalty_rate": Decimal("10"),
        "gas_rate": Decimal("0.65"),
        "gas_cap": Decimal("261"),
        "daily_order_divisor": Decimal("13.333"),
    },
    PayrollCategory.FOOD_TRIAL: {
        "basic_salary_rate": Decimal("66.66666667"),
        "bonus_rate": Decimal("7"),
        "penalty_rate": Decimal("10"),
        "gas_rate": Decimal("2.11"),
        "gas_cap": Decimal("826"),
        "daily_order_divisor": Decimal("13"),
    },
    PayrollCategory.FOOD_INHOUSE_NEW: {
        "basic_salary_rate": Decimal("66.66666667"),
        "bonus_rate": Decimal("7"),
        "penalty_rate": Decimal("10"),
        "gas_rate": Decimal("1.739"),
        "gas_cap": Decimal("826"),
        "daily_order_divisor": Decimal("15.83333333"),
    },
    PayrollCategory.FOOD_INHOUSE_OLD: {
        "basic_salary_rate": Decimal("66.66666667"),
        "penalty_rate": Decimal("10"),
        "gas_rate": Decimal("2.065"),
        "gas_cap": Decimal("826"),
        "daily_order_divisor": Decimal("15.83333333"),
        "tier_threshold": 199,
        "tier_1_rate": Decimal("6"),
        "tier_2_rate": Decimal("9"),
    },
    PayrollCategory.ECOMMERCE_WH: {
        "basic_salary_rate": Decimal("66.666667"),
        "bonus_rate": Decimal("8"),
        "penalty_rate": Decimal("10"),
        "gas_rate": Decimal("15.03"),
        "gas_cap": Decimal("452"),
        "daily_order_divisor": Decimal("16.6666667"),
    },
    PayrollCategory.ECOMMERCE: {
        "basic_salary_rate": Decimal("66.66666667"),
        "revenue_coefficient": Decimal("0.3016591252"),
        "gas_cap": Decimal("452"),
        "daily_order_divisor": Decimal("221"),
        "bonus_revenue_threshold": Decimal("4000"),
        "bonus_rate_below_threshold": Decimal("0.55"),
        "bonus_rate_above_threshold": Decimal("0.5"),
        "fuel_revenue_coefficient": Decimal("0.068"),
        "fuel_target_coefficient": Decimal("15.06"),
    },
}
