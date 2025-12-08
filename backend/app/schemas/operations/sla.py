from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class SLAType(str, Enum):
    DELIVERY_TIME = "DELIVERY_TIME"
    RESPONSE_TIME = "RESPONSE_TIME"
    PICKUP_TIME = "PICKUP_TIME"
    RESOLUTION_TIME = "RESOLUTION_TIME"
    UPTIME = "UPTIME"
    QUALITY_SCORE = "QUALITY_SCORE"


class SLAPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SLAStatus(str, Enum):
    ACTIVE = "ACTIVE"
    BREACHED = "BREACHED"
    AT_RISK = "AT_RISK"
    MET = "MET"
    EXPIRED = "EXPIRED"


# SLA Definition Schemas
class SLADefinitionBase(BaseModel):
    sla_code: str = Field(..., min_length=2, max_length=50)
    sla_name: str = Field(..., min_length=3, max_length=200)
    sla_type: SLAType
    description: Optional[str] = None
    target_value: Decimal = Field(..., description="Target value to meet")
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    priority: SLAPriority = SLAPriority.MEDIUM
    applies_to_zone_id: Optional[int] = None
    applies_to_service_type: Optional[str] = Field(None, pattern="^(express|standard|economy)$")
    applies_to_customer_tier: Optional[str] = Field(None, pattern="^(premium|standard|basic)$")
    penalty_per_breach: Decimal = Field(Decimal("0.0"), ge=0)
    escalation_required: bool = False
    measurement_period: str = Field("daily", pattern="^(daily|weekly|monthly)$")
    calculation_method: Optional[str] = None


class SLADefinitionCreate(SLADefinitionBase):
    is_active: bool = True
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None


class SLADefinitionUpdate(BaseModel):
    sla_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    target_value: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    priority: Optional[SLAPriority] = None
    applies_to_zone_id: Optional[int] = None
    applies_to_service_type: Optional[str] = None
    applies_to_customer_tier: Optional[str] = None
    penalty_per_breach: Optional[Decimal] = Field(None, ge=0)
    escalation_required: Optional[bool] = None
    measurement_period: Optional[str] = None
    calculation_method: Optional[str] = None
    is_active: Optional[bool] = None
    effective_until: Optional[datetime] = None


class SLADefinitionResponse(SLADefinitionBase):
    id: int
    is_active: bool
    effective_from: Optional[datetime] = None
    effective_until: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# SLA Tracking Schemas
class SLATrackingBase(BaseModel):
    sla_definition_id: int
    delivery_id: Optional[int] = None
    route_id: Optional[int] = None
    courier_id: Optional[int] = None
    incident_id: Optional[int] = None
    start_time: datetime
    target_completion_time: datetime
    target_value: Decimal


class SLATrackingCreate(SLATrackingBase):
    delivery_window_start: Optional[datetime] = None
    delivery_window_end: Optional[datetime] = None


class SLATrackingUpdate(BaseModel):
    actual_completion_time: Optional[datetime] = None
    actual_value: Optional[Decimal] = None
    status: Optional[SLAStatus] = None
    breach_reason: Optional[str] = None
    corrective_action: Optional[str] = None
    resolution_notes: Optional[str] = None
    customer_notified: Optional[bool] = None


class SLABreachReport(BaseModel):
    """Schema for reporting SLA breach"""

    breach_reason: str = Field(..., min_length=10)
    breach_severity: str = Field(..., pattern="^(minor|major|critical)$")
    corrective_action: Optional[str] = None
    escalate: bool = False
    escalated_to_id: Optional[int] = None


class SLATrackingResponse(SLATrackingBase):
    id: int
    tracking_number: str
    status: SLAStatus
    warning_time: Optional[datetime] = None
    actual_completion_time: Optional[datetime] = None
    actual_value: Optional[Decimal] = None
    variance: Optional[Decimal] = None
    variance_percentage: Optional[Decimal] = None
    is_breached: bool
    breach_time: Optional[datetime] = None
    breach_duration_minutes: Optional[int] = None
    breach_severity: Optional[str] = None
    customer_notified: bool
    notification_sent_at: Optional[datetime] = None
    penalty_applied: Decimal
    breach_reason: Optional[str] = None
    corrective_action: Optional[str] = None
    resolution_notes: Optional[str] = None
    escalated: bool
    escalated_to_id: Optional[int] = None
    escalated_at: Optional[datetime] = None
    compliance_score: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SLAComplianceReport(BaseModel):
    """SLA compliance report"""

    period: str
    sla_type: SLAType
    total_tracked: int
    total_met: int
    total_breached: int
    total_at_risk: int
    compliance_rate: float
    avg_variance_percentage: float
    total_penalties: Decimal
    top_breach_reasons: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
