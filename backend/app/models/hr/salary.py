from sqlalchemy import Column, Date, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class Salary(TenantMixin, BaseModel):
    """
    Salary record for a courier for a specific month/year.

    Extended to support category-based payroll calculation from salary.md spec.
    """
    __tablename__ = "salaries"
    __table_args__ = (
        UniqueConstraint('courier_id', 'year', 'month', 'organization_id', name='uq_salary_courier_period'),
        Index('ix_salary_courier_period', 'courier_id', 'year', 'month'),
        {'extend_existing': True}
    )

    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="RESTRICT"), nullable=False, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    # Category-based payroll fields (stored as string to match DB VARCHAR)
    category = Column(String(50), nullable=True, comment="Payroll category used for calculation")

    # Period dates (25th to 24th calculation period)
    period_start = Column(Date, nullable=True, comment="Calculation period start date")
    period_end = Column(Date, nullable=True, comment="Calculation period end date")

    # Performance metrics (from BigQuery)
    total_orders = Column(Integer, default=0, comment="Total orders in period")
    total_revenue = Column(Numeric(12, 2), default=0, comment="Total revenue in period")
    gas_usage = Column(Numeric(10, 2), default=0, comment="Actual gas usage (without VAT)")

    # Target and calculation
    target = Column(Numeric(10, 2), default=0, comment="Final calculated target")
    daily_target = Column(Numeric(10, 2), default=0, comment="Daily target from config")
    days_since_joining = Column(Integer, default=0, comment="Days since joining as of period end")

    # Salary components (category-based)
    base_salary = Column(Numeric(10, 2), nullable=False)
    bonus_amount = Column(Numeric(10, 2), default=0, comment="Performance bonus (can be negative = penalty)")

    # Gas/Fuel components
    gas_deserved = Column(Numeric(10, 2), default=0, comment="Calculated gas allowance")
    gas_difference = Column(Numeric(10, 2), default=0, comment="gas_deserved - gas_usage")

    # Legacy fields (for backward compatibility and additional deductions)
    allowances = Column(Numeric(10, 2), default=0)
    deductions = Column(Numeric(10, 2), default=0)
    loan_deduction = Column(Numeric(10, 2), default=0)
    gosi_employee = Column(Numeric(10, 2), default=0)

    # Calculated totals
    gross_salary = Column(Numeric(10, 2), nullable=False)
    net_salary = Column(Numeric(10, 2), nullable=False)

    # Payment tracking
    payment_date = Column(Date, nullable=True)
    is_paid = Column(Integer, default=0)  # Boolean-like

    # Audit fields
    notes = Column(Text, nullable=True)
    calculation_details = Column(Text, nullable=True, comment="JSON with detailed calculation breakdown")
    generated_date = Column(Date, nullable=True, comment="When salary was calculated")

    # Relationships
    courier = relationship("Courier", back_populates="salaries")

    @property
    def total_salary(self) -> float:
        """Alias for net_salary for compatibility with salary.md output format"""
        return float(self.net_salary or 0)
