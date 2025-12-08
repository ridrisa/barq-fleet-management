from sqlalchemy import Column, Date, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class Salary(TenantMixin, BaseModel):
    __tablename__ = "salaries"
    __table_args__ = (
        UniqueConstraint('courier_id', 'year', 'month', 'organization_id', name='uq_salary_courier_period'),
        Index('ix_salary_courier_period', 'courier_id', 'year', 'month'),
        {'extend_existing': True}
    )

    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="RESTRICT"), nullable=False, index=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    base_salary = Column(Numeric(10, 2), nullable=False)
    allowances = Column(Numeric(10, 2), default=0)
    deductions = Column(Numeric(10, 2), default=0)
    loan_deduction = Column(Numeric(10, 2), default=0)
    gosi_employee = Column(Numeric(10, 2), default=0)
    gross_salary = Column(Numeric(10, 2), nullable=False)
    net_salary = Column(Numeric(10, 2), nullable=False)
    payment_date = Column(Date, nullable=True)
    notes = Column(String)

    # Relationships
    courier = relationship("Courier", back_populates="salaries")
