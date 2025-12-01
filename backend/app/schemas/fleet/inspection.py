from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

from app.models.fleet import InspectionType, InspectionStatus, VehicleCondition


class InspectionBase(BaseModel):
    """Base inspection schema"""
    vehicle_id: int
    inspector_id: Optional[int] = None
    inspection_type: InspectionType
    inspection_date: date
    inspection_time: Optional[datetime] = None

    status: InspectionStatus
    overall_condition: VehicleCondition = VehicleCondition.GOOD
    mileage_at_inspection: Optional[Decimal] = Field(None, ge=0)

    # Checklist items (all default True = passed)
    engine_condition: bool = True
    engine_oil_level: bool = True
    coolant_level: bool = True
    battery_condition: bool = True
    transmission: bool = True

    headlights: bool = True
    taillights: bool = True
    indicators: bool = True
    brake_lights: bool = True
    horn: bool = True
    dashboard_lights: bool = True

    brake_pads_front: bool = True
    brake_pads_rear: bool = True
    brake_fluid_level: bool = True
    handbrake: bool = True

    tire_front_left: bool = True
    tire_front_right: bool = True
    tire_rear_left: bool = True
    tire_rear_right: bool = True
    spare_tire: bool = True
    tire_pressure_ok: bool = True

    body_condition: bool = True
    windshield: bool = True
    mirrors: bool = True
    wipers: bool = True
    doors: bool = True
    windows: bool = True

    seats: bool = True
    seatbelts: bool = True
    air_conditioning: bool = True
    steering: bool = True

    first_aid_kit: bool = True
    fire_extinguisher: bool = True
    warning_triangle: bool = True
    jack_and_tools: bool = True

    registration_document: bool = True
    insurance_document: bool = True

    issues_found: Optional[str] = None
    critical_issues: Optional[str] = None
    recommendations: Optional[str] = None
    required_repairs: Optional[str] = None

    requires_immediate_repair: bool = False
    requires_follow_up: bool = False
    follow_up_date: Optional[date] = None
    repairs_completed: bool = False
    repairs_completion_date: Optional[date] = None

    inspector_name: Optional[str] = Field(None, max_length=200)
    inspector_signature: Optional[str] = Field(None, max_length=500)
    inspector_comments: Optional[str] = None

    weather_during_inspection: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=300)
    notes: Optional[str] = None

    inspection_report_url: Optional[str] = Field(None, max_length=500)
    photos_json: Optional[str] = None

    meets_safety_standards: bool = True
    roadworthy: bool = True


class InspectionCreate(InspectionBase):
    """Schema for creating inspection"""
    pass


class InspectionUpdate(BaseModel):
    """Schema for updating inspection"""
    status: Optional[InspectionStatus] = None
    overall_condition: Optional[VehicleCondition] = None
    issues_found: Optional[str] = None
    recommendations: Optional[str] = None
    repairs_completed: Optional[bool] = None
    repairs_completion_date: Optional[date] = None
    notes: Optional[str] = None


class InspectionResponse(InspectionBase):
    """Schema for inspection response"""
    id: int
    inspection_score: Optional[int] = None
    total_checks: Optional[int] = None
    passed_checks: Optional[int] = None
    failed_checks: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_passed: bool = False
    needs_attention: bool = False
    pass_percentage: float = 0.0

    class Config:
        from_attributes = True


class InspectionList(BaseModel):
    """Minimal schema for list views"""
    id: int
    vehicle_id: int
    inspection_type: InspectionType
    inspection_date: date
    status: InspectionStatus
    inspection_score: Optional[int] = None
    roadworthy: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
