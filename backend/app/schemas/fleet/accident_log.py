from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.fleet import AccidentSeverity, AccidentStatus, AccidentType, FaultStatus


class AccidentLogBase(BaseModel):
    """Base accident log schema"""

    vehicle_id: int
    courier_id: Optional[int] = None

    accident_date: date
    accident_time: Optional[time] = None
    accident_type: AccidentType
    severity: AccidentSeverity
    status: AccidentStatus = AccidentStatus.REPORTED

    location_description: str
    city: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    street_address: Optional[str] = Field(None, max_length=500)

    weather_conditions: Optional[str] = Field(None, max_length=100)
    road_conditions: Optional[str] = Field(None, max_length=100)
    visibility: Optional[str] = Field(None, max_length=50)
    traffic_conditions: Optional[str] = Field(None, max_length=100)

    fault_status: FaultStatus = FaultStatus.PENDING
    our_vehicle_at_fault: bool = False

    accident_description: str
    courier_statement: Optional[str] = None
    witness_statements: Optional[str] = None

    other_party_name: Optional[str] = Field(None, max_length=200)
    other_party_phone: Optional[str] = Field(None, max_length=20)
    other_party_insurance: Optional[str] = Field(None, max_length=200)
    other_party_policy_number: Optional[str] = Field(None, max_length=100)
    other_party_vehicle_plate: Optional[str] = Field(None, max_length=20)
    other_party_vehicle_details: Optional[str] = None

    any_injuries: bool = False
    injury_details: Optional[str] = None
    casualties_count: int = Field(default=0, ge=0)
    hospitalization_required: bool = False
    hospital_name: Optional[str] = Field(None, max_length=300)

    police_notified: bool = False
    police_report_number: Optional[str] = Field(None, max_length=100)
    police_station: Optional[str] = Field(None, max_length=200)
    police_officer_name: Optional[str] = Field(None, max_length=200)
    police_officer_badge: Optional[str] = Field(None, max_length=50)

    vehicle_damage_description: Optional[str] = None
    estimated_repair_cost: Optional[Decimal] = Field(None, ge=0)
    actual_repair_cost: Optional[Decimal] = Field(None, ge=0)
    vehicle_towed: bool = False
    tow_company: Optional[str] = Field(None, max_length=200)
    tow_cost: Optional[Decimal] = Field(None, ge=0)

    insurance_claim_filed: bool = False
    insurance_claim_number: Optional[str] = Field(None, max_length=100)
    insurance_claim_amount: Optional[Decimal] = Field(None, ge=0)
    insurance_approved_amount: Optional[Decimal] = Field(None, ge=0)
    insurance_claim_status: Optional[str] = Field(None, max_length=50)
    claim_filed_date: Optional[date] = None
    claim_settlement_date: Optional[date] = None

    repair_start_date: Optional[date] = None
    repair_completion_date: Optional[date] = None
    repair_shop_name: Optional[str] = Field(None, max_length=300)
    repair_shop_location: Optional[str] = Field(None, max_length=300)

    total_cost: Decimal = Field(default=0.0, ge=0)
    insurance_covered: Decimal = Field(default=0.0, ge=0)
    out_of_pocket_cost: Decimal = Field(default=0.0, ge=0)
    lost_revenue: Decimal = Field(default=0.0, ge=0)

    vehicle_downtime_days: int = Field(default=0, ge=0)
    vehicle_available_date: Optional[date] = None

    investigated_by: Optional[str] = Field(None, max_length=200)
    investigation_date: Optional[date] = None
    investigation_findings: Optional[str] = None
    corrective_actions: Optional[str] = None

    courier_action_taken: Optional[str] = Field(None, max_length=100)
    courier_notes: Optional[str] = None

    accident_photos_json: Optional[str] = None
    police_report_url: Optional[str] = Field(None, max_length=500)
    insurance_documents_json: Optional[str] = None
    repair_invoices_json: Optional[str] = None

    requires_follow_up: bool = False
    follow_up_date: Optional[date] = None
    follow_up_notes: Optional[str] = None

    reported_by: Optional[str] = Field(None, max_length=200)
    reported_date: Optional[datetime] = None
    notes: Optional[str] = None

    legal_action_required: bool = False
    legal_case_number: Optional[str] = Field(None, max_length=100)
    legal_status: Optional[str] = Field(None, max_length=100)


class AccidentLogCreate(AccidentLogBase):
    """Schema for creating accident log"""

    pass


class AccidentLogUpdate(BaseModel):
    """Schema for updating accident log"""

    status: Optional[AccidentStatus] = None
    fault_status: Optional[FaultStatus] = None
    actual_repair_cost: Optional[Decimal] = Field(None, ge=0)
    insurance_claim_status: Optional[str] = None
    insurance_approved_amount: Optional[Decimal] = Field(None, ge=0)
    repair_completion_date: Optional[date] = None
    investigation_findings: Optional[str] = None
    corrective_actions: Optional[str] = None
    courier_action_taken: Optional[str] = None
    notes: Optional[str] = None


class AccidentLogResponse(AccidentLogBase):
    """Schema for accident log response"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_resolved: bool = False
    is_major_accident: bool = False
    involves_injury: bool = False
    financial_impact: float = 0.0
    repair_duration_days: int = 0

    class Config:
        from_attributes = True


class AccidentLogList(BaseModel):
    """Minimal schema for list views"""

    id: int
    vehicle_id: int
    courier_id: Optional[int] = None
    accident_date: date
    accident_type: AccidentType
    severity: AccidentSeverity
    status: AccidentStatus
    total_cost: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
