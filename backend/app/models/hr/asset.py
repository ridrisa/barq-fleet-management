from sqlalchemy import Column, String, Integer, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum

class AssetType(str, enum.Enum):
    UNIFORM = "uniform"
    MOBILE_DEVICE = "mobile_device"
    EQUIPMENT = "equipment"
    TOOLS = "tools"

class AssetStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    RETURNED = "returned"
    DAMAGED = "damaged"
    LOST = "lost"

class Asset(TenantMixin, BaseModel):
    __tablename__ = "assets"

    asset_type = Column(Enum(AssetType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    courier_id = Column(Integer, ForeignKey("couriers.id"), nullable=False)
    issue_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    condition = Column(String, default="good")
    status = Column(Enum(AssetStatus, values_callable=lambda x: [e.value for e in x]), default=AssetStatus.ASSIGNED)
    notes = Column(String)

    # Relationships
    courier = relationship("Courier", back_populates="assets")
