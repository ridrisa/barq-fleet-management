from sqlalchemy import Column, String, Integer, Date, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class AssignmentStatus(str, enum.Enum):
    """Assignment status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssignmentType(str, enum.Enum):
    """Type of vehicle assignment"""
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    TRIAL = "trial"


class CourierVehicleAssignment(TenantMixin, BaseModel):
    """Track courier-vehicle assignment history"""

    __tablename__ = "courier_vehicle_assignments"

    # Foreign Keys
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Assignment Details
    assignment_type = Column(SQLEnum(AssignmentType), default=AssignmentType.PERMANENT, nullable=False)
    status = Column(SQLEnum(AssignmentStatus), default=AssignmentStatus.ACTIVE, nullable=False, index=True)

    # Dates
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True)

    # Mileage at assignment
    start_mileage = Column(Integer)
    end_mileage = Column(Integer, nullable=True)

    # Assignment Details
    assigned_by = Column(String(200))  # Who assigned (manager/admin name)
    assignment_reason = Column(Text)
    termination_reason = Column(Text, nullable=True)

    # Additional Information
    notes = Column(Text)

    # Relationships
    courier = relationship("Courier", back_populates="vehicle_assignments")
    vehicle = relationship("Vehicle", back_populates="assignment_history")

    def __repr__(self):
        return f"<Assignment: Courier #{self.courier_id} -> Vehicle #{self.vehicle_id} ({self.status.value})>"

    @property
    def is_active(self) -> bool:
        """Check if assignment is currently active"""
        return self.status == AssignmentStatus.ACTIVE

    @property
    def duration_days(self) -> int:
        """Calculate assignment duration in days"""
        from datetime import date
        end = self.end_date or date.today()
        return (end - self.start_date).days

    @property
    def mileage_used(self) -> int:
        """Calculate mileage used during assignment"""
        if self.start_mileage and self.end_mileage:
            return self.end_mileage - self.start_mileage
        return 0
