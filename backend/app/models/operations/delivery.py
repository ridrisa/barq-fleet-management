import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class Delivery(TenantMixin, BaseModel):
    __tablename__ = "deliveries"

    tracking_number = Column(String, unique=True, nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"), nullable=True)
    pickup_address = Column(Text, nullable=False)
    delivery_address = Column(Text, nullable=False)
    status = Column(
        Enum(DeliveryStatus, values_callable=lambda x: [e.value for e in x]),
        default=DeliveryStatus.PENDING,
    )
    pickup_time = Column(DateTime)
    delivery_time = Column(DateTime)
    cod_amount = Column(Numeric(10, 2), default=0)
    notes = Column(Text)

    courier = relationship("Courier", back_populates="deliveries")
