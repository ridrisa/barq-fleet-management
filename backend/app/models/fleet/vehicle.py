from sqlalchemy import Column, String, Integer, Boolean, Date, Numeric, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class VehicleStatus(str, enum.Enum):
    """Vehicle operational status"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    RETIRED = "retired"
    REPAIR = "repair"


class VehicleType(str, enum.Enum):
    """Vehicle category"""
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    TRUCK = "truck"
    BICYCLE = "bicycle"


class FuelType(str, enum.Enum):
    """Fuel type"""
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


class OwnershipType(str, enum.Enum):
    """Vehicle ownership"""
    OWNED = "owned"
    LEASED = "leased"
    RENTED = "rented"


class Vehicle(TenantMixin, BaseModel):
    """Vehicle model - Fleet asset tracking"""

    __tablename__ = "vehicles"

    # Basic Information
    plate_number = Column(String(20), unique=True, nullable=False, index=True, comment="License plate number")
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False, index=True)
    make = Column(String(100), nullable=False)  # Toyota, Honda, etc.
    model = Column(String(100), nullable=False)  # Corolla, Civic, etc.
    year = Column(Integer, nullable=False)
    color = Column(String(50))

    # Status
    status = Column(SQLEnum(VehicleStatus), default=VehicleStatus.ACTIVE, nullable=False, index=True)
    ownership_type = Column(SQLEnum(OwnershipType), default=OwnershipType.OWNED)

    # Registration & Documentation
    registration_number = Column(String(50), unique=True)
    registration_expiry_date = Column(Date)
    insurance_company = Column(String(200))
    insurance_policy_number = Column(String(100))
    insurance_expiry_date = Column(Date)

    # Technical Details
    vin_number = Column(String(50), unique=True, comment="Vehicle Identification Number")
    engine_number = Column(String(50))
    engine_capacity = Column(String(20))  # 1.6L, 2.0L, etc.
    transmission = Column(String(20))  # Manual, Automatic

    # Fuel & Mileage
    fuel_type = Column(SQLEnum(FuelType), default=FuelType.GASOLINE)
    current_mileage = Column(Numeric(10, 2), default=0.0)
    fuel_capacity = Column(Numeric(5, 2))  # Liters

    # Financial
    purchase_price = Column(Numeric(10, 2))
    purchase_date = Column(Date)
    monthly_lease_cost = Column(Numeric(10, 2), nullable=True)
    depreciation_rate = Column(Numeric(5, 2), default=20.0)  # Percentage per year

    # Maintenance
    last_service_date = Column(Date)
    last_service_mileage = Column(Numeric(10, 2))
    next_service_due_date = Column(Date)
    next_service_due_mileage = Column(Numeric(10, 2))

    # GPS & Tracking
    gps_device_id = Column(String(100))
    gps_device_imei = Column(String(50))
    is_gps_active = Column(Boolean, default=False)

    # FMS Integration (machinestalk GPS tracking)
    fms_asset_id = Column(Integer, unique=True, nullable=True, index=True, comment="FMS Asset ID")
    fms_tracking_unit_id = Column(Integer, nullable=True, comment="FMS Tracking Unit ID")
    fms_last_sync = Column(String(50), nullable=True, comment="Last FMS sync timestamp")

    # Assignment
    assigned_to_city = Column(String(100))
    assigned_to_project = Column(String(100))  # Which project/vertical uses this vehicle

    # Additional Information
    notes = Column(Text)
    is_pool_vehicle = Column(Boolean, default=False)  # Shared vehicle or dedicated

    # Performance & Usage Metrics (cached)
    total_trips = Column(Integer, default=0)
    total_distance = Column(Numeric(10, 2), default=0.0)
    avg_fuel_consumption = Column(Numeric(5, 2))  # km per liter

    # Relationships
    assigned_couriers = relationship("Courier", foreign_keys="Courier.current_vehicle_id", back_populates="current_vehicle")
    assignment_history = relationship("CourierVehicleAssignment", back_populates="vehicle", cascade="all, delete-orphan")
    vehicle_logs = relationship("VehicleLog", back_populates="vehicle", cascade="all, delete-orphan")
    maintenance_records = relationship("VehicleMaintenance", back_populates="vehicle", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="vehicle", cascade="all, delete-orphan")
    accident_logs = relationship("AccidentLog", back_populates="vehicle", cascade="all, delete-orphan")
    fuel_logs = relationship("FuelLog", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehicle {self.plate_number}: {self.make} {self.model} ({self.status.value})>"

    @property
    def is_available(self) -> bool:
        """Check if vehicle is available for assignment"""
        return self.status == VehicleStatus.ACTIVE and len(self.assigned_couriers) == 0

    @property
    def is_service_due(self) -> bool:
        """Check if vehicle is due for service"""
        from datetime import date
        today = date.today()

        if self.next_service_due_date and self.next_service_due_date <= today:
            return True
        if self.next_service_due_mileage and self.current_mileage >= self.next_service_due_mileage:
            return True

        return False

    @property
    def is_document_expired(self) -> bool:
        """Check if any vehicle document is expired"""
        from datetime import date
        today = date.today()

        if self.registration_expiry_date and self.registration_expiry_date < today:
            return True
        if self.insurance_expiry_date and self.insurance_expiry_date < today:
            return True

        return False

    @property
    def age_years(self) -> int:
        """Calculate vehicle age in years"""
        from datetime import date
        return date.today().year - self.year
