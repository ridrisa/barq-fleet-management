from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin

class Salary(TenantMixin, BaseModel):
    __tablename__ = "salaries"

    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=False)
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
