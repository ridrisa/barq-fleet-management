from sqlalchemy import Column, String, Integer, Numeric, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum

class CODStatus(str, enum.Enum):
    PENDING = "pending"
    COLLECTED = "collected"
    DEPOSITED = "deposited"
    RECONCILED = "reconciled"

class COD(TenantMixin, BaseModel):
    __tablename__ = "cod_transactions"

    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    collection_date = Column(Date, nullable=False)
    deposit_date = Column(Date, nullable=True)
    status = Column(Enum(CODStatus, values_callable=lambda x: [e.value for e in x]), default=CODStatus.PENDING)
    reference_number = Column(String)
    notes = Column(String)

    courier = relationship("Courier")
