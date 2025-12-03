from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class QualityMetricType(str, Enum):
    DELIVERY_QUALITY = "delivery_quality"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    VEHICLE_CONDITION = "vehicle_condition"
    COURIER_PERFORMANCE = "courier_performance"
    PACKAGE_HANDLING = "package_handling"
    TIMELINESS = "timeliness"
    COMPLIANCE = "compliance"


class InspectionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PASSED = "passed"


# Quality Metric Schemas
class QualityMetricBase(BaseModel):
    metric_code: str = Field(..., min_length=2, max_length=50)
    metric_name: str = Field(..., min_length=3, max_length=200)
    metric_type: QualityMetricType
    description: Optional[str] = None
    target_value: Decimal = Field(..., description="Target value")
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    min_acceptable: Optional[Decimal] = None
    max_acceptable: Optional[Decimal] = None
    weight: Decimal = Field(Decimal("1.0"), ge=0, le=10)
    is_critical: bool = False


class QualityMetricCreate(QualityMetricBase):
    is_active: bool = True


class QualityMetricUpdate(BaseModel):
    metric_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    target_value: Optional[Decimal] = None
    unit_of_measure: Optional[str] = None
    min_acceptable: Optional[Decimal] = None
    max_acceptable: Optional[Decimal] = None
    weight: Optional[Decimal] = Field(None, ge=0, le=10)
    is_critical: Optional[bool] = None
    is_active: Optional[bool] = None


class QualityMetricResponse(QualityMetricBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Quality Inspection Schemas
class QualityInspectionBase(BaseModel):
    inspection_type: QualityMetricType
    courier_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    delivery_id: Optional[int] = None
    scheduled_date: date
    inspector_notes: Optional[str] = None


class QualityInspectionCreate(QualityInspectionBase):
    inspector_id: Optional[int] = None


class QualityInspectionUpdate(BaseModel):
    status: Optional[InspectionStatus] = None
    inspection_date: Optional[datetime] = None
    inspector_notes: Optional[str] = None
    overall_score: Optional[Decimal] = Field(None, ge=0, le=100)
    passed: Optional[bool] = None
    findings: Optional[str] = None
    violations_count: Optional[int] = Field(None, ge=0)
    recommendations: Optional[str] = None
    requires_followup: Optional[bool] = None
    followup_date: Optional[date] = None
    corrective_actions: Optional[str] = None
    photos: Optional[str] = None
    attachments: Optional[str] = None


class QualityInspectionComplete(BaseModel):
    """Schema for completing an inspection"""

    overall_score: Decimal = Field(..., ge=0, le=100)
    passed: bool
    findings: str
    violations_count: int = Field(0, ge=0)
    recommendations: Optional[str] = None
    requires_followup: bool = False
    followup_date: Optional[date] = None
    corrective_actions: Optional[str] = None
    photos: Optional[str] = None
    attachments: Optional[str] = None
    inspector_notes: Optional[str] = None


class QualityInspectionResponse(QualityInspectionBase):
    id: int
    inspection_number: str
    status: InspectionStatus
    inspection_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    inspector_id: Optional[int] = None
    overall_score: Optional[Decimal] = None
    passed: Optional[bool] = None
    findings: Optional[str] = None
    violations_count: int
    recommendations: Optional[str] = None
    requires_followup: bool
    followup_date: Optional[date] = None
    followup_completed: bool
    corrective_actions: Optional[str] = None
    actions_completed: bool
    completion_verified_by: Optional[int] = None
    photos: Optional[str] = None
    attachments: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class QualityReport(BaseModel):
    """Quality control report"""

    period: str
    total_inspections: int
    passed_inspections: int
    failed_inspections: int
    pass_rate: float
    avg_overall_score: float
    critical_violations: int
    pending_followups: int
    top_violations: List[Dict[str, Any]]

    model_config = ConfigDict(from_attributes=True)
