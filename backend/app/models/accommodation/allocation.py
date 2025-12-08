from sqlalchemy import Column, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class Allocation(TenantMixin, BaseModel):
    __tablename__ = "allocations"

    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), nullable=False)
    bed_id = Column(Integer, ForeignKey("beds.id", ondelete="CASCADE"), nullable=False)
    allocation_date = Column(Date, nullable=False)
    release_date = Column(Date, nullable=True)

    courier = relationship("Courier", back_populates="allocations")
    bed = relationship("Bed", back_populates="allocation")
