import enum

from sqlalchemy import Boolean, Column, Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class CourierStatus(str, enum.Enum):
    """Courier employment status"""
    # Values match PostgreSQL enum (uppercase)
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"
    ONBOARDING = "ONBOARDING"
    SUSPENDED = "SUSPENDED"


class SponsorshipStatus(str, enum.Enum):
    """Sponsorship type"""
    # Values match PostgreSQL enum (uppercase)
    AJEER = "AJEER"
    INHOUSE = "INHOUSE"
    TRIAL = "TRIAL"
    FREELANCER = "FREELANCER"


class ProjectType(str, enum.Enum):
    """Project/vertical assignment"""
    # Values match PostgreSQL enum (uppercase)
    ECOMMERCE = "ECOMMERCE"
    FOOD = "FOOD"
    WAREHOUSE = "WAREHOUSE"
    BARQ = "BARQ"
    MIXED = "MIXED"


class Courier(TenantMixin, BaseModel):
    """Courier/Driver model - Core entity for fleet management"""

    __tablename__ = "couriers"

    # Basic Information
    barq_id = Column(
        String(50), unique=True, nullable=False, index=True, comment="Unique BARQ identifier"
    )
    full_name = Column(String(200), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True)
    mobile_number = Column(String(20), nullable=False)

    # Employment Details
    employee_id = Column(String(50), unique=True, index=True)
    status = Column(
        SQLEnum(CourierStatus, values_callable=lambda e: [m.value for m in e]), default=CourierStatus.ONBOARDING, nullable=False, index=True
    )
    sponsorship_status = Column(SQLEnum(SponsorshipStatus, values_callable=lambda e: [m.value for m in e]), default=SponsorshipStatus.INHOUSE)
    project_type = Column(SQLEnum(ProjectType, values_callable=lambda e: [m.value for m in e]), default=ProjectType.BARQ)
    position = Column(String(100), default="Courier")
    city = Column(String(100), index=True)

    # Dates
    joining_date = Column(Date)
    last_working_day = Column(Date, nullable=True)
    date_of_birth = Column(Date)

    # Identification Documents
    national_id = Column(String(50), unique=True)
    nationality = Column(String(100))
    iqama_number = Column(String(50), unique=True)
    iqama_expiry_date = Column(Date)
    passport_number = Column(String(50), unique=True)
    passport_expiry_date = Column(Date)

    # Driver's License
    license_number = Column(String(50))
    license_expiry_date = Column(Date)
    license_type = Column(String(20))  # Motorcycle, Car, etc.

    # Banking Information
    bank_account_number = Column(String(50))
    bank_name = Column(String(100))
    iban = Column(String(50))

    # Platform IDs (Integration with delivery platforms)
    jahez_driver_id = Column(String(50))
    hunger_rider_id = Column(String(50))
    mrsool_courier_id = Column(String(50))

    # FMS Integration (machinestalk GPS tracking)
    fms_asset_id = Column(
        Integer, unique=True, nullable=True, index=True, comment="FMS Asset ID for GPS tracking"
    )
    fms_driver_id = Column(Integer, nullable=True, comment="FMS Driver ID")
    fms_last_sync = Column(String(50), nullable=True, comment="Last FMS sync timestamp")

    # Assignment
    current_vehicle_id = Column(
        Integer, ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )
    supervisor_name = Column(String(200))

    # Accommodation - Current assigned location
    accommodation_building_id = Column(
        Integer, ForeignKey("buildings.id", ondelete="SET NULL"), nullable=True,
        comment="Current building assignment (use allocations for history)"
    )
    accommodation_room_id = Column(
        Integer, ForeignKey("rooms.id", ondelete="SET NULL"), nullable=True,
        comment="Current room assignment (use allocations for history)"
    )

    # Additional Information
    notes = Column(Text)
    emergency_contact_name = Column(String(200))
    emergency_contact_phone = Column(String(20))

    # Performance Metrics (cached from analytics)
    performance_score = Column(Numeric(5, 2), default=0.0)
    total_deliveries = Column(Integer, default=0)

    # Relationships
    current_vehicle = relationship(
        "Vehicle", foreign_keys=[current_vehicle_id], back_populates="assigned_couriers"
    )
    vehicle_assignments = relationship(
        "CourierVehicleAssignment", back_populates="courier", cascade="all, delete-orphan"
    )
    vehicle_logs = relationship(
        "VehicleLog", back_populates="courier", cascade="all, delete-orphan"
    )
    accident_logs = relationship(
        "AccidentLog", back_populates="courier", cascade="all, delete-orphan"
    )
    fuel_logs = relationship("FuelLog", back_populates="courier")

    # Accommodation relationships
    allocations = relationship("Allocation", back_populates="courier")

    # HR module relationships
    leaves = relationship("Leave", back_populates="courier")
    loans = relationship("Loan", back_populates="courier")
    attendance_records = relationship("Attendance", back_populates="courier")
    salaries = relationship("Salary", back_populates="courier")
    assets = relationship("Asset", back_populates="courier")
    bonuses = relationship("Bonus", back_populates="courier")

    # Operations relationships
    deliveries = relationship("Delivery", back_populates="courier")
    cod_transactions = relationship("COD", back_populates="courier")
    incidents = relationship("Incident", back_populates="courier")

    def __repr__(self):
        return f"<Courier {self.barq_id}: {self.full_name} ({self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Check if courier is actively working"""
        return self.status == CourierStatus.ACTIVE

    @property
    def has_vehicle(self) -> bool:
        """Check if courier has an assigned vehicle"""
        return self.current_vehicle_id is not None

    @property
    def is_document_expired(self) -> bool:
        """Check if any critical document is expired"""
        from datetime import date

        today = date.today()

        if self.iqama_expiry_date and self.iqama_expiry_date < today:
            return True
        if self.passport_expiry_date and self.passport_expiry_date < today:
            return True
        if self.license_expiry_date and self.license_expiry_date < today:
            return True

        return False
