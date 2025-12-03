import enum

from sqlalchemy import Boolean, Column, Date, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class QualityMetricType(str, enum.Enum):
    """Type of quality metric"""

    DELIVERY_QUALITY = "delivery_quality"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    VEHICLE_CONDITION = "vehicle_condition"
    COURIER_PERFORMANCE = "courier_performance"
    PACKAGE_HANDLING = "package_handling"
    TIMELINESS = "timeliness"
    COMPLIANCE = "compliance"


class InspectionStatus(str, enum.Enum):
    """Quality inspection status"""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PASSED = "passed"


class QualityMetric(TenantMixin, BaseModel):
    """Quality control metrics and measurements"""

    __tablename__ = "quality_metrics"

    # Metric Identification
    metric_code = Column(String(50), unique=True, nullable=False, index=True)
    metric_name = Column(String(200), nullable=False)
    metric_type = Column(SQLEnum(QualityMetricType), nullable=False, index=True)
    description = Column(Text)

    # Target Values
    target_value = Column(Numeric(10, 2), nullable=False, comment="Target/threshold value")
    unit_of_measure = Column(String(50), comment="%, minutes, count, etc.")

    # Thresholds
    min_acceptable = Column(Numeric(10, 2), comment="Minimum acceptable value")
    max_acceptable = Column(Numeric(10, 2), comment="Maximum acceptable value")

    # Weighting
    weight = Column(Numeric(5, 2), default=1.0, comment="Weight in overall quality score")
    is_critical = Column(Boolean, default=False, comment="Critical quality metric")

    # Status
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<QualityMetric {self.metric_code}: {self.metric_name}>"


class QualityInspection(TenantMixin, BaseModel):
    """Quality inspections for couriers, vehicles, and operations"""

    __tablename__ = "quality_inspections"

    # Inspection Details
    inspection_number = Column(String(50), unique=True, nullable=False, index=True)
    inspection_type = Column(SQLEnum(QualityMetricType), nullable=False, index=True)
    status = Column(SQLEnum(InspectionStatus), default=InspectionStatus.SCHEDULED, index=True)

    # Subject of Inspection
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), index=True)

    # Timing
    scheduled_date = Column(Date, nullable=False, index=True)
    inspection_date = Column(DateTime)
    completed_date = Column(DateTime)

    # Inspector
    inspector_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    inspector_notes = Column(Text)

    # Results
    overall_score = Column(Numeric(5, 2), comment="Overall quality score 0-100")
    passed = Column(Boolean)

    # Findings
    findings = Column(Text, comment="JSON array of inspection findings")
    violations_count = Column(Integer, default=0)
    recommendations = Column(Text)

    # Follow-up
    requires_followup = Column(Boolean, default=False)
    followup_date = Column(Date)
    followup_completed = Column(Boolean, default=False)

    # Corrective Actions
    corrective_actions = Column(Text, comment="Required corrective actions")
    actions_completed = Column(Boolean, default=False)
    completion_verified_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    # Documentation
    photos = Column(Text, comment="Comma-separated photo URLs")
    attachments = Column(Text, comment="Comma-separated document URLs")

    # Relationships
    courier = relationship("Courier")
    vehicle = relationship("Vehicle")
    delivery = relationship("Delivery")

    def __repr__(self):
        return f"<QualityInspection {self.inspection_number}: {self.inspection_type.value} ({self.status.value})>"

    @property
    def is_completed(self) -> bool:
        """Check if inspection is completed"""
        return self.status in [
            InspectionStatus.COMPLETED,
            InspectionStatus.PASSED,
            InspectionStatus.FAILED,
        ]

    @property
    def needs_attention(self) -> bool:
        """Check if inspection requires attention"""
        return not self.passed or self.requires_followup
