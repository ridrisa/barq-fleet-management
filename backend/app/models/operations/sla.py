from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum as SQLEnum, Text, Numeric, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum


class SLAType(str, enum.Enum):
    """Type of SLA"""
    DELIVERY_TIME = "delivery_time"
    RESPONSE_TIME = "response_time"
    PICKUP_TIME = "pickup_time"
    RESOLUTION_TIME = "resolution_time"
    UPTIME = "uptime"
    QUALITY_SCORE = "quality_score"


class SLAPriority(str, enum.Enum):
    """SLA priority level"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SLAStatus(str, enum.Enum):
    """SLA tracking status"""
    ACTIVE = "active"
    BREACHED = "breached"
    AT_RISK = "at_risk"
    MET = "met"
    EXPIRED = "expired"


class SLADefinition(BaseModel):
    """Service Level Agreement definitions and targets"""

    __tablename__ = "sla_definitions"

    # SLA Identification
    sla_code = Column(String(50), unique=True, nullable=False, index=True)
    sla_name = Column(String(200), nullable=False)
    sla_type = Column(SQLEnum(SLAType), nullable=False, index=True)
    description = Column(Text)

    # Targets
    target_value = Column(Numeric(10, 2), nullable=False, comment="Target value to meet")
    unit_of_measure = Column(String(50), comment="minutes, hours, %, count")

    # Thresholds
    warning_threshold = Column(Numeric(10, 2), comment="Warning level (e.g., 80% of target)")
    critical_threshold = Column(Numeric(10, 2), comment="Critical level")

    # Priority
    priority = Column(SQLEnum(SLAPriority), default=SLAPriority.MEDIUM)

    # Applicability
    applies_to_zone_id = Column(Integer, ForeignKey("zones.id", ondelete="CASCADE"), index=True)
    applies_to_service_type = Column(String(50), comment="express, standard, economy")
    applies_to_customer_tier = Column(String(50), comment="premium, standard, basic")

    # Penalties
    penalty_per_breach = Column(Numeric(10, 2), default=0.0, comment="Financial penalty")
    escalation_required = Column(Boolean, default=False)

    # Measurement
    measurement_period = Column(String(50), default="daily", comment="daily, weekly, monthly")
    calculation_method = Column(Text, comment="How to calculate compliance")

    # Status
    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime)
    effective_until = Column(DateTime)

    # Relationships
    zone = relationship("Zone")

    def __repr__(self):
        return f"<SLADefinition {self.sla_code}: {self.sla_name}>"


class SLATracking(BaseModel):
    """SLA compliance tracking and breach monitoring"""

    __tablename__ = "sla_tracking"

    # Reference
    sla_definition_id = Column(Integer, ForeignKey("sla_definitions.id", ondelete="CASCADE"), nullable=False, index=True)
    tracking_number = Column(String(50), unique=True, nullable=False, index=True)

    # Subject
    delivery_id = Column(Integer, ForeignKey("deliveries.id", ondelete="CASCADE"), index=True)
    route_id = Column(Integer, ForeignKey("routes.id", ondelete="CASCADE"), index=True)
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="CASCADE"), index=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), index=True)

    # Timing
    start_time = Column(DateTime, nullable=False)
    target_completion_time = Column(DateTime, nullable=False, index=True)
    warning_time = Column(DateTime, comment="When warning threshold is reached")
    actual_completion_time = Column(DateTime)

    # Status
    status = Column(SQLEnum(SLAStatus), default=SLAStatus.ACTIVE, index=True)

    # Measurements
    target_value = Column(Numeric(10, 2), nullable=False)
    actual_value = Column(Numeric(10, 2))
    variance = Column(Numeric(10, 2), comment="Difference from target")
    variance_percentage = Column(Numeric(5, 2), comment="Percentage variance")

    # Breach Information
    is_breached = Column(Boolean, default=False, index=True)
    breach_time = Column(DateTime)
    breach_duration_minutes = Column(Integer, comment="How long breached")
    breach_severity = Column(String(20), comment="minor, major, critical")

    # Impact
    customer_notified = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime)
    penalty_applied = Column(Numeric(10, 2), default=0.0)

    # Resolution
    breach_reason = Column(Text, comment="Reason for SLA breach")
    corrective_action = Column(Text)
    resolution_notes = Column(Text)

    # Escalation
    escalated = Column(Boolean, default=False)
    escalated_to_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    escalated_at = Column(DateTime)

    # Performance Tracking
    compliance_score = Column(Numeric(5, 2), comment="Compliance percentage 0-100")

    # Relationships
    sla_definition = relationship("SLADefinition")
    delivery = relationship("Delivery")
    route = relationship("Route")
    courier = relationship("Courier")
    incident = relationship("Incident")

    def __repr__(self):
        return f"<SLATracking {self.tracking_number}: {self.status.value}>"

    @property
    def is_at_risk(self) -> bool:
        """Check if SLA is at risk of being breached"""
        return self.status == SLAStatus.AT_RISK

    @property
    def is_breached_status(self) -> bool:
        """Check if SLA has been breached"""
        return self.is_breached or self.status == SLAStatus.BREACHED

    @property
    def is_met(self) -> bool:
        """Check if SLA was successfully met"""
        return self.status == SLAStatus.MET
