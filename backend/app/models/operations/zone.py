from sqlalchemy import Column, String, Integer, Boolean, Float, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class ZoneStatus(str, enum.Enum):
    """Zone operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class Zone(TenantMixin, BaseModel):
    """Delivery zones for service area coverage"""

    __tablename__ = "zones"

    # Basic Information
    zone_code = Column(String(50), unique=True, nullable=False, index=True, comment="Unique zone identifier")
    zone_name = Column(String(200), nullable=False, index=True)
    description = Column(Text)

    # Geographic Data
    city = Column(String(100), nullable=False, index=True)
    district = Column(String(100))
    postal_code = Column(String(20))

    # Boundaries (GeoJSON format)
    boundaries = Column(JSON, comment="GeoJSON polygon defining zone boundaries")
    center_latitude = Column(Float)
    center_longitude = Column(Float)

    # Coverage Metrics
    coverage_area_km2 = Column(Float, comment="Area in square kilometers")
    estimated_population = Column(Integer)
    business_density = Column(String(20), comment="low, medium, high")

    # Operational Details
    status = Column(SQLEnum(ZoneStatus), default=ZoneStatus.ACTIVE, nullable=False, index=True)
    priority_level = Column(Integer, default=1, comment="1=lowest, 5=highest")
    max_couriers = Column(Integer, default=10, comment="Maximum couriers allowed in zone")
    current_couriers = Column(Integer, default=0, comment="Current active couriers")

    # Performance Metrics (cached)
    avg_delivery_time_minutes = Column(Float, default=0.0)
    total_deliveries_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0, comment="Percentage 0-100")

    # Configuration
    service_fee = Column(Float, default=0.0, comment="Base service fee for zone")
    peak_hour_multiplier = Column(Float, default=1.0)
    minimum_order_value = Column(Float, default=0.0)

    # Notes
    notes = Column(Text)
    special_instructions = Column(Text)

    def __repr__(self):
        return f"<Zone {self.zone_code}: {self.zone_name} ({self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Check if zone is actively operational"""
        return self.status == ZoneStatus.ACTIVE

    @property
    def is_at_capacity(self) -> bool:
        """Check if zone has reached maximum courier capacity"""
        return self.current_couriers >= self.max_couriers

    @property
    def utilization_rate(self) -> float:
        """Calculate courier utilization rate"""
        if self.max_couriers == 0:
            return 0.0
        return (self.current_couriers / self.max_couriers) * 100
