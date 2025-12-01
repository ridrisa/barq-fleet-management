from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class MaintenanceType(str, enum.Enum):
    """Type of maintenance service"""
    ROUTINE = "routine"  # Regular scheduled service
    PREVENTIVE = "preventive"  # Preventive maintenance
    CORRECTIVE = "corrective"  # Fix an issue
    BREAKDOWN = "breakdown"  # Emergency repair
    UPGRADE = "upgrade"  # Upgrades/modifications


class MaintenanceStatus(str, enum.Enum):
    """Maintenance record status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ServiceProvider(str, enum.Enum):
    """Where maintenance was performed"""
    IN_HOUSE = "in_house"
    AUTHORIZED_DEALER = "authorized_dealer"
    THIRD_PARTY = "third_party"


class VehicleMaintenance(BaseModel):
    """Vehicle maintenance and service records"""

    __tablename__ = "vehicle_maintenance"

    # Foreign Key
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Maintenance Details
    maintenance_type = Column(SQLEnum(MaintenanceType), nullable=False, index=True)
    status = Column(SQLEnum(MaintenanceStatus), default=MaintenanceStatus.SCHEDULED, nullable=False, index=True)
    service_provider = Column(SQLEnum(ServiceProvider), default=ServiceProvider.THIRD_PARTY)

    # Dates
    scheduled_date = Column(Date, index=True)
    start_date = Column(Date)
    completion_date = Column(Date)

    # Mileage at service
    mileage_at_service = Column(Numeric(10, 2))

    # Service Details
    service_description = Column(Text, nullable=False)
    work_performed = Column(Text)  # Detailed work done
    parts_replaced = Column(Text)  # List of parts replaced
    parts_list_json = Column(Text)  # JSON array of parts with costs

    # Service Provider Information
    service_center_name = Column(String(300))
    service_center_location = Column(String(300))
    technician_name = Column(String(200))
    technician_phone = Column(String(20))

    # Financial
    labor_cost = Column(Numeric(10, 2), default=0.0)
    parts_cost = Column(Numeric(10, 2), default=0.0)
    total_cost = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), default=0.0)
    discount_amount = Column(Numeric(10, 2), default=0.0)

    # Payment
    payment_method = Column(String(50))  # Cash, Card, Bank Transfer
    invoice_number = Column(String(100), unique=True)
    invoice_date = Column(Date)
    payment_status = Column(String(50), default="pending")  # pending, paid, partially_paid

    # Warranty
    has_warranty = Column(Boolean, default=False)
    warranty_expiry_date = Column(Date)
    warranty_details = Column(Text)

    # Next Service
    next_service_date = Column(Date)
    next_service_mileage = Column(Numeric(10, 2))

    # Quality & Approval
    quality_rating = Column(Integer)  # 1-5 rating
    approved_by = Column(String(200))
    approval_date = Column(Date)

    # Issues & Notes
    issues_found = Column(Text)  # Issues discovered during service
    recommendations = Column(Text)  # Recommended future work
    notes = Column(Text)

    # Attachments
    invoice_image_url = Column(String(500))
    report_file_url = Column(String(500))
    photos_json = Column(Text)  # JSON array of photo URLs

    # Downtime
    vehicle_downtime_hours = Column(Numeric(6, 2))  # How long vehicle was out of service

    # Relationships
    vehicle = relationship("Vehicle", back_populates="maintenance_records")

    def __repr__(self):
        return f"<Maintenance: Vehicle #{self.vehicle_id} - {self.maintenance_type.value} ({self.status.value})>"

    @property
    def is_completed(self) -> bool:
        """Check if maintenance is completed"""
        return self.status == MaintenanceStatus.COMPLETED

    @property
    def is_overdue(self) -> bool:
        """Check if scheduled maintenance is overdue"""
        from datetime import date
        if self.status == MaintenanceStatus.SCHEDULED and self.scheduled_date:
            return self.scheduled_date < date.today()
        return False

    @property
    def total_with_tax(self) -> float:
        """Calculate total cost including tax"""
        return float(self.total_cost + (self.tax_amount or 0))

    @property
    def net_cost(self) -> float:
        """Calculate net cost after discount"""
        return float(self.total_cost - (self.discount_amount or 0))

    def calculate_total_cost(self):
        """Auto-calculate total cost from labor and parts"""
        labor = self.labor_cost or 0
        parts = self.parts_cost or 0
        self.total_cost = labor + parts

    @property
    def duration_days(self) -> int:
        """Calculate maintenance duration in days"""
        if self.start_date and self.completion_date:
            return (self.completion_date - self.start_date).days
        return 0
