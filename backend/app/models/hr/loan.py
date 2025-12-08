import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class LoanStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Loan(TenantMixin, BaseModel):
    __tablename__ = "loans"

    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    outstanding_balance = Column(Numeric(10, 2), nullable=False)
    monthly_deduction = Column(Numeric(10, 2), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(
        Enum(LoanStatus, values_callable=lambda x: [e.value for e in x]), default=LoanStatus.ACTIVE
    )
    approved_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(String)

    # Relationships
    courier = relationship("Courier", back_populates="loans")
    approver = relationship("User", foreign_keys=[approved_by])
