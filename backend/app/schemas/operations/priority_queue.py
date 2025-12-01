from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class QueuePriority(str, Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class QueueStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    ASSIGNED = "assigned"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class PriorityQueueEntryBase(BaseModel):
    delivery_id: int
    priority: QueuePriority
    sla_deadline: datetime
    sla_buffer_minutes: int = Field(30, ge=0, le=120)
    customer_tier: Optional[str] = Field(None, pattern="^(premium|vip|standard|basic)$")
    is_vip_customer: bool = False
    customer_special_instructions: Optional[str] = None
    required_zone_id: Optional[int] = None
    required_vehicle_type: Optional[str] = Field(None, pattern="^(bike|car|van)$")
    required_skills: Optional[str] = None
    preferred_courier_id: Optional[int] = None
    delivery_window_start: Optional[datetime] = None
    delivery_window_end: Optional[datetime] = None


class PriorityQueueEntryCreate(PriorityQueueEntryBase):
    base_priority_score: int = Field(..., ge=1, le=100)
    time_factor_score: int = Field(0, ge=0, le=50)
    customer_tier_score: int = Field(0, ge=0, le=30)
    sla_factor_score: int = Field(0, ge=0, le=20)


class PriorityQueueEntryUpdate(BaseModel):
    priority: Optional[QueuePriority] = None
    status: Optional[QueueStatus] = None
    sla_deadline: Optional[datetime] = None
    preferred_courier_id: Optional[int] = None
    customer_special_instructions: Optional[str] = None
    excluded_courier_ids: Optional[str] = None
    min_courier_rating: Optional[Decimal] = Field(None, ge=0, le=5)


class PriorityQueueEntryEscalate(BaseModel):
    """Schema for escalating queue entry"""
    escalation_reason: str = Field(..., min_length=10)
    escalated_to_id: int
    new_priority: Optional[QueuePriority] = None


class PriorityQueueEntryResponse(PriorityQueueEntryBase):
    id: int
    queue_number: str
    status: QueueStatus
    base_priority_score: int
    time_factor_score: int
    customer_tier_score: int
    sla_factor_score: int
    total_priority_score: int
    warning_threshold: Optional[datetime] = None
    queued_at: datetime
    assigned_at: Optional[datetime] = None
    processing_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    queue_position: Optional[int] = None
    estimated_wait_time_minutes: Optional[int] = None
    excluded_courier_ids: Optional[str] = None
    min_courier_rating: Optional[Decimal] = None
    max_assignment_attempts: int
    assignment_attempts: int
    is_escalated: bool
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    escalated_to_id: Optional[int] = None
    time_in_queue_minutes: Optional[int] = None
    was_sla_met: Optional[bool] = None
    sla_breach_minutes: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class QueueMetrics(BaseModel):
    """Priority queue metrics"""
    total_entries: int
    queued_entries: int
    processing_entries: int
    assigned_entries: int
    completed_entries: int
    expired_entries: int
    avg_wait_time_minutes: float
    avg_processing_time_minutes: float
    sla_compliance_rate: float
    escalation_rate: float
    entries_by_priority: dict


class QueuePosition(BaseModel):
    """Current position in queue"""
    delivery_id: int
    queue_number: str
    current_position: int
    total_in_queue: int
    estimated_wait_minutes: int
    priority: QueuePriority
    is_at_risk: bool
