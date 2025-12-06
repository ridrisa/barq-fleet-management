import enum

from sqlalchemy import Boolean, Column, Date, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text, Time
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class LogType(str, enum.Enum):
    """Type of vehicle log entry"""

    DAILY_LOG = "daily_log"
    FUEL_REFILL = "fuel_refill"
    TRIP = "trip"
    DELIVERY = "delivery"


class FuelProvider(str, enum.Enum):
    """Fuel station provider"""

    ARAMCO = "aramco"
    ADNOC = "adnoc"
    PETROL = "petrol"
    OTHER = "other"


class VehicleLog(TenantMixin, BaseModel):
    """Daily vehicle operation logs and trip records"""

    __tablename__ = "vehicle_logs"

    # Foreign Keys
    vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    courier_id = Column(
        Integer, ForeignKey("couriers.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Log Details
    log_type = Column(SQLEnum(LogType, values_callable=lambda e: [m.value for m in e]), default=LogType.DAILY_LOG, nullable=False, index=True)
    log_date = Column(Date, nullable=False, index=True)
    log_time = Column(Time)

    # Mileage & Distance
    start_mileage = Column(Numeric(10, 2))
    end_mileage = Column(Numeric(10, 2))
    distance_covered = Column(Numeric(10, 2))  # Calculated: end - start

    # Location
    start_location = Column(String(300))
    end_location = Column(String(300))
    route_description = Column(Text)

    # Fuel Information
    fuel_refilled = Column(Numeric(8, 2))  # Liters
    fuel_cost = Column(Numeric(10, 2))  # SAR
    fuel_provider = Column(SQLEnum(FuelProvider, values_callable=lambda e: [m.value for m in e]), nullable=True)
    fuel_station_location = Column(String(300))
    fuel_receipt_number = Column(String(100))

    # Performance Metrics
    number_of_deliveries = Column(Integer, default=0)
    number_of_orders = Column(Integer, default=0)
    revenue_generated = Column(Numeric(10, 2), default=0.0)

    # Condition & Issues
    vehicle_condition = Column(String(50))  # Good, Fair, Needs Attention
    issues_reported = Column(Text)
    has_issues = Column(Boolean, default=False)

    # Time Tracking
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    working_hours = Column(Numeric(5, 2))  # Decimal hours

    # Additional Information
    weather_conditions = Column(String(100))
    traffic_conditions = Column(String(100))
    notes = Column(Text)
    recorded_by = Column(String(200))  # Who recorded this log

    # Attachments
    receipt_image_url = Column(String(500))  # Fuel receipt
    log_photo_urls = Column(Text)  # JSON array of photo URLs

    # Relationships
    vehicle = relationship("Vehicle", back_populates="vehicle_logs")
    courier = relationship("Courier", back_populates="vehicle_logs")

    def __repr__(self):
        return (
            f"<VehicleLog: Vehicle #{self.vehicle_id} on {self.log_date} ({self.log_type.value})>"
        )

    @property
    def fuel_efficiency(self) -> float:
        """Calculate fuel efficiency (km per liter)"""
        if self.distance_covered and self.fuel_refilled and self.fuel_refilled > 0:
            return float(self.distance_covered / self.fuel_refilled)
        return 0.0

    @property
    def cost_per_km(self) -> float:
        """Calculate cost per kilometer"""
        if self.distance_covered and self.fuel_cost and self.distance_covered > 0:
            return float(self.fuel_cost / self.distance_covered)
        return 0.0

    @property
    def revenue_per_delivery(self) -> float:
        """Calculate average revenue per delivery"""
        if self.number_of_deliveries and self.revenue_generated and self.number_of_deliveries > 0:
            return float(self.revenue_generated / self.number_of_deliveries)
        return 0.0

    def calculate_distance(self):
        """Auto-calculate distance if start/end mileage provided"""
        if self.start_mileage and self.end_mileage:
            self.distance_covered = self.end_mileage - self.start_mileage
