from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum, Numeric
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.mixins import TenantMixin
import enum


class InspectionType(str, enum.Enum):
    """Type of vehicle inspection"""
    PRE_TRIP = "pre_trip"  # Before starting shift
    POST_TRIP = "post_trip"  # After shift
    PERIODIC = "periodic"  # Monthly/quarterly
    SAFETY = "safety"  # Safety inspection
    REGISTRATION = "registration"  # For vehicle registration
    ACCIDENT = "accident"  # Post-accident inspection


class InspectionStatus(str, enum.Enum):
    """Inspection result status"""
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"  # Pass with minor issues
    PENDING = "pending"


class VehicleCondition(str, enum.Enum):
    """Overall vehicle condition"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class Inspection(TenantMixin, BaseModel):
    """Vehicle inspection records for safety and compliance"""

    __tablename__ = "vehicle_inspections"

    # Foreign Keys
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    inspector_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Inspection Details
    inspection_type = Column(SQLEnum(InspectionType), nullable=False, index=True)
    inspection_date = Column(Date, nullable=False, index=True)
    inspection_time = Column(DateTime)

    # Results
    status = Column(SQLEnum(InspectionStatus), nullable=False, index=True)
    overall_condition = Column(SQLEnum(VehicleCondition), default=VehicleCondition.GOOD)

    # Mileage
    mileage_at_inspection = Column(Numeric(10, 2))

    # Inspection Checklist Results (True = OK, False = Issue)
    # Engine & Performance
    engine_condition = Column(Boolean, default=True)
    engine_oil_level = Column(Boolean, default=True)
    coolant_level = Column(Boolean, default=True)
    battery_condition = Column(Boolean, default=True)
    transmission = Column(Boolean, default=True)

    # Lights & Electrical
    headlights = Column(Boolean, default=True)
    taillights = Column(Boolean, default=True)
    indicators = Column(Boolean, default=True)
    brake_lights = Column(Boolean, default=True)
    horn = Column(Boolean, default=True)
    dashboard_lights = Column(Boolean, default=True)

    # Brakes
    brake_pads_front = Column(Boolean, default=True)
    brake_pads_rear = Column(Boolean, default=True)
    brake_fluid_level = Column(Boolean, default=True)
    handbrake = Column(Boolean, default=True)

    # Tires
    tire_front_left = Column(Boolean, default=True)
    tire_front_right = Column(Boolean, default=True)
    tire_rear_left = Column(Boolean, default=True)
    tire_rear_right = Column(Boolean, default=True)
    spare_tire = Column(Boolean, default=True)
    tire_pressure_ok = Column(Boolean, default=True)

    # Exterior
    body_condition = Column(Boolean, default=True)
    windshield = Column(Boolean, default=True)
    mirrors = Column(Boolean, default=True)
    wipers = Column(Boolean, default=True)
    doors = Column(Boolean, default=True)
    windows = Column(Boolean, default=True)

    # Interior
    seats = Column(Boolean, default=True)
    seatbelts = Column(Boolean, default=True)
    air_conditioning = Column(Boolean, default=True)
    steering = Column(Boolean, default=True)

    # Safety Equipment
    first_aid_kit = Column(Boolean, default=True)
    fire_extinguisher = Column(Boolean, default=True)
    warning_triangle = Column(Boolean, default=True)
    jack_and_tools = Column(Boolean, default=True)

    # Documents
    registration_document = Column(Boolean, default=True)
    insurance_document = Column(Boolean, default=True)

    # Issues & Recommendations
    issues_found = Column(Text)  # Detailed issues
    critical_issues = Column(Text)  # Issues that must be fixed immediately
    recommendations = Column(Text)
    required_repairs = Column(Text)

    # Follow-up
    requires_immediate_repair = Column(Boolean, default=False)
    requires_follow_up = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    repairs_completed = Column(Boolean, default=False)
    repairs_completion_date = Column(Date)

    # Inspector Information
    inspector_name = Column(String(200))
    inspector_signature = Column(String(500))  # Digital signature URL
    inspector_comments = Column(Text)

    # Additional Information
    weather_during_inspection = Column(String(100))
    location = Column(String(300))
    notes = Column(Text)

    # Attachments
    inspection_report_url = Column(String(500))
    photos_json = Column(Text)  # JSON array of photo URLs

    # Scoring
    inspection_score = Column(Integer)  # 0-100 score
    total_checks = Column(Integer)
    passed_checks = Column(Integer)
    failed_checks = Column(Integer)

    # Compliance
    meets_safety_standards = Column(Boolean, default=True)
    roadworthy = Column(Boolean, default=True)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="inspections")
    inspector = relationship("User", foreign_keys=[inspector_id])

    def __repr__(self):
        return f"<Inspection: Vehicle #{self.vehicle_id} on {self.inspection_date} - {self.status.value}>"

    @property
    def is_passed(self) -> bool:
        """Check if inspection passed"""
        return self.status == InspectionStatus.PASSED

    @property
    def needs_attention(self) -> bool:
        """Check if vehicle needs attention"""
        return self.status == InspectionStatus.FAILED or self.requires_immediate_repair

    @property
    def pass_percentage(self) -> float:
        """Calculate percentage of checks passed"""
        if self.total_checks and self.total_checks > 0:
            return (self.passed_checks / self.total_checks) * 100
        return 0.0

    def calculate_inspection_score(self):
        """Calculate inspection score based on checklist"""
        checklist_items = [
            self.engine_condition, self.engine_oil_level, self.coolant_level,
            self.battery_condition, self.transmission,
            self.headlights, self.taillights, self.indicators,
            self.brake_lights, self.horn, self.dashboard_lights,
            self.brake_pads_front, self.brake_pads_rear,
            self.brake_fluid_level, self.handbrake,
            self.tire_front_left, self.tire_front_right,
            self.tire_rear_left, self.tire_rear_right,
            self.spare_tire, self.tire_pressure_ok,
            self.body_condition, self.windshield, self.mirrors,
            self.wipers, self.doors, self.windows,
            self.seats, self.seatbelts, self.air_conditioning, self.steering,
            self.first_aid_kit, self.fire_extinguisher,
            self.warning_triangle, self.jack_and_tools,
            self.registration_document, self.insurance_document
        ]

        self.total_checks = len(checklist_items)
        self.passed_checks = sum(1 for item in checklist_items if item)
        self.failed_checks = self.total_checks - self.passed_checks

        if self.total_checks > 0:
            self.inspection_score = int((self.passed_checks / self.total_checks) * 100)
        else:
            self.inspection_score = 0

        # Determine overall status
        if self.inspection_score >= 95:
            self.status = InspectionStatus.PASSED
            self.roadworthy = True
        elif self.inspection_score >= 80:
            self.status = InspectionStatus.CONDITIONAL
            self.roadworthy = True
        else:
            self.status = InspectionStatus.FAILED
            self.roadworthy = False
