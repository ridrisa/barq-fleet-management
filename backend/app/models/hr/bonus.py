import enum

from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class BonusType(str, enum.Enum):
    PERFORMANCE = "performance"
    ATTENDANCE = "attendance"
    SEASONAL = "seasonal"
    SPECIAL = "special"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"


class Bonus(TenantMixin, BaseModel):
    __tablename__ = "bonuses"

    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), nullable=False)
    bonus_type = Column(
        Enum(BonusType, values_callable=lambda x: [e.value for e in x]), nullable=False
    )
    amount = Column(Numeric(10, 2), nullable=False)
    bonus_date = Column(Date, nullable=False)
    payment_status = Column(
        Enum(PaymentStatus, values_callable=lambda x: [e.value for e in x]),
        default=PaymentStatus.PENDING,
    )
    approved_by = Column(Integer, ForeignKey("users.id"))
    approval_date = Column(Date, nullable=True)
    description = Column(String)
    notes = Column(String)

    # Relationships
    courier = relationship("Courier", back_populates="bonuses")
    approver = relationship("User", foreign_keys=[approved_by])
