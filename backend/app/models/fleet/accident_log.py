from sqlalchemy import Column, String, Integer, Date, DateTime, Time, ForeignKey, Text, Numeric, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class AccidentSeverity(str, enum.Enum):
    """Severity level of accident"""
    MINOR = "minor"  # Cosmetic damage only
    MODERATE = "moderate"  # Moderate damage, vehicle driveable
    MAJOR = "major"  # Significant damage, vehicle undriveable
    TOTAL_LOSS = "total_loss"  # Vehicle is a total loss


class AccidentType(str, enum.Enum):
    """Type of accident"""
    COLLISION = "collision"  # With another vehicle
    SINGLE_VEHICLE = "single_vehicle"  # Single vehicle accident
    PEDESTRIAN = "pedestrian"  # Involving pedestrian
    PROPERTY_DAMAGE = "property_damage"  # Hit property/structure
    ROLLOVER = "rollover"
    OTHER = "other"


class FaultStatus(str, enum.Enum):
    """Who is at fault"""
    OUR_FAULT = "our_fault"
    OTHER_PARTY = "other_party"
    SHARED = "shared"
    NO_FAULT = "no_fault"
    PENDING = "pending"


class AccidentStatus(str, enum.Enum):
    """Case status"""
    REPORTED = "reported"
    UNDER_INVESTIGATION = "under_investigation"
    INSURANCE_CLAIM_FILED = "insurance_claim_filed"
    IN_REPAIR = "in_repair"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AccidentLog(TenantMixin, BaseModel):
    """Accident and incident reporting for fleet vehicles"""

    __tablename__ = "accident_logs"

    # Foreign Keys
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    courier_id = Column(Integer, ForeignKey("couriers.id", ondelete="SET NULL"), nullable=True, index=True)

    # Accident Details
    accident_date = Column(Date, nullable=False, index=True)
    accident_time = Column(Time)
    accident_type = Column(SQLEnum(AccidentType), nullable=False)
    severity = Column(SQLEnum(AccidentSeverity), nullable=False, index=True)
    status = Column(SQLEnum(AccidentStatus), default=AccidentStatus.REPORTED, nullable=False, index=True)

    # Location
    location_description = Column(Text, nullable=False)
    city = Column(String(100), index=True)
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    street_address = Column(String(500))

    # Weather & Conditions
    weather_conditions = Column(String(100))
    road_conditions = Column(String(100))
    visibility = Column(String(50))
    traffic_conditions = Column(String(100))

    # Fault & Liability
    fault_status = Column(SQLEnum(FaultStatus), default=FaultStatus.PENDING, index=True)
    our_vehicle_at_fault = Column(Boolean, default=False)

    # Description
    accident_description = Column(Text, nullable=False)
    courier_statement = Column(Text)
    witness_statements = Column(Text)

    # Other Party Information
    other_party_name = Column(String(200))
    other_party_phone = Column(String(20))
    other_party_insurance = Column(String(200))
    other_party_policy_number = Column(String(100))
    other_party_vehicle_plate = Column(String(20))
    other_party_vehicle_details = Column(Text)

    # Casualties & Injuries
    any_injuries = Column(Boolean, default=False)
    injury_details = Column(Text)
    casualties_count = Column(Integer, default=0)
    hospitalization_required = Column(Boolean, default=False)
    hospital_name = Column(String(300))

    # Police Report
    police_notified = Column(Boolean, default=False)
    police_report_number = Column(String(100))
    police_station = Column(String(200))
    police_officer_name = Column(String(200))
    police_officer_badge = Column(String(50))

    # Damage Assessment
    vehicle_damage_description = Column(Text)
    estimated_repair_cost = Column(Numeric(10, 2))
    actual_repair_cost = Column(Numeric(10, 2))
    vehicle_towed = Column(Boolean, default=False)
    tow_company = Column(String(200))
    tow_cost = Column(Numeric(10, 2))

    # Insurance Claim
    insurance_claim_filed = Column(Boolean, default=False)
    insurance_claim_number = Column(String(100), unique=True)
    insurance_claim_amount = Column(Numeric(10, 2))
    insurance_approved_amount = Column(Numeric(10, 2))
    insurance_claim_status = Column(String(50))
    claim_filed_date = Column(Date)
    claim_settlement_date = Column(Date)

    # Repair Information
    repair_start_date = Column(Date)
    repair_completion_date = Column(Date)
    repair_shop_name = Column(String(300))
    repair_shop_location = Column(String(300))

    # Financial Impact
    total_cost = Column(Numeric(10, 2), default=0.0)
    insurance_covered = Column(Numeric(10, 2), default=0.0)
    out_of_pocket_cost = Column(Numeric(10, 2), default=0.0)
    lost_revenue = Column(Numeric(10, 2), default=0.0)  # Revenue lost during downtime

    # Downtime
    vehicle_downtime_days = Column(Integer, default=0)
    vehicle_available_date = Column(Date)

    # Investigation
    investigated_by = Column(String(200))
    investigation_date = Column(Date)
    investigation_findings = Column(Text)
    corrective_actions = Column(Text)

    # Courier Accountability
    courier_action_taken = Column(String(100))  # Warning, Suspension, Training, etc.
    courier_notes = Column(Text)

    # Attachments
    accident_photos_json = Column(Text)  # JSON array of photo URLs
    police_report_url = Column(String(500))
    insurance_documents_json = Column(Text)  # JSON array of document URLs
    repair_invoices_json = Column(Text)  # JSON array of invoice URLs

    # Follow-up
    requires_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    follow_up_notes = Column(Text)

    # Additional Information
    reported_by = Column(String(200))
    reported_date = Column(DateTime)
    notes = Column(Text)

    # Legal
    legal_action_required = Column(Boolean, default=False)
    legal_case_number = Column(String(100))
    legal_status = Column(String(100))

    # Relationships
    vehicle = relationship("Vehicle", back_populates="accident_logs")
    courier = relationship("Courier", back_populates="accident_logs")

    def __repr__(self):
        return f"<AccidentLog: Vehicle #{self.vehicle_id} on {self.accident_date} - {self.severity.value}>"

    @property
    def is_resolved(self) -> bool:
        """Check if accident case is resolved"""
        return self.status in [AccidentStatus.RESOLVED, AccidentStatus.CLOSED]

    @property
    def is_major_accident(self) -> bool:
        """Check if this is a major accident"""
        return self.severity in [AccidentSeverity.MAJOR, AccidentSeverity.TOTAL_LOSS]

    @property
    def involves_injury(self) -> bool:
        """Check if accident involves injuries"""
        return self.any_injuries or self.casualties_count > 0

    @property
    def financial_impact(self) -> float:
        """Calculate total financial impact"""
        return float(
            (self.total_cost or 0) +
            (self.lost_revenue or 0) -
            (self.insurance_covered or 0)
        )

    @property
    def repair_duration_days(self) -> int:
        """Calculate repair duration in days"""
        if self.repair_start_date and self.repair_completion_date:
            return (self.repair_completion_date - self.repair_start_date).days
        return 0

    def calculate_total_cost(self):
        """Calculate total cost of accident"""
        repair = self.actual_repair_cost or self.estimated_repair_cost or 0
        tow = self.tow_cost or 0
        self.total_cost = repair + tow
        self.out_of_pocket_cost = self.total_cost - (self.insurance_covered or 0)
