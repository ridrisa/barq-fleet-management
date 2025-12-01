from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from decimal import Decimal


class DispatchStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DispatchPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DispatchAlgorithm(str, Enum):
    NEAREST = "nearest"
    LOAD_BALANCED = "load_balanced"
    PRIORITY_BASED = "priority_based"
    MANUAL = "manual"
    AI_OPTIMIZED = "ai_optimized"


class DispatchAssignmentBase(BaseModel):
    delivery_id: int
    priority: DispatchPriority = DispatchPriority.NORMAL
    zone_id: Optional[int] = None


class DispatchAssignmentCreate(DispatchAssignmentBase):
    courier_id: Optional[int] = None
    assignment_algorithm: DispatchAlgorithm = DispatchAlgorithm.LOAD_BALANCED
    assignment_notes: Optional[str] = None


class DispatchAssignmentUpdate(BaseModel):
    courier_id: Optional[int] = None
    status: Optional[DispatchStatus] = None
    priority: Optional[DispatchPriority] = None
    rejection_reason: Optional[str] = None
    current_latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    current_longitude: Optional[Decimal] = Field(None, ge=-180, le=180)


class DispatchReassignment(BaseModel):
    """Schema for reassigning delivery to different courier"""
    new_courier_id: int
    reassignment_reason: str = Field(..., min_length=10)
    priority: Optional[DispatchPriority] = None


class DispatchAcceptance(BaseModel):
    """Schema for courier accepting/rejecting assignment"""
    accepted: bool
    rejection_reason: Optional[str] = None
    estimated_arrival_minutes: Optional[int] = Field(None, ge=0, le=300)


class DispatchAssignmentResponse(DispatchAssignmentBase):
    id: int
    assignment_number: str
    status: DispatchStatus
    courier_id: Optional[int] = None
    created_at_time: datetime
    assigned_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assignment_algorithm: str
    distance_to_pickup_km: Optional[Decimal] = None
    estimated_time_minutes: Optional[int] = None
    courier_current_load: int
    courier_max_capacity: int
    courier_rating: Optional[Decimal] = None
    rejection_reason: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_count: int
    is_reassignment: bool
    previous_courier_id: Optional[int] = None
    reassignment_reason: Optional[str] = None
    actual_completion_time_minutes: Optional[int] = None
    performance_variance: Optional[int] = None
    assigned_by_id: Optional[int] = None
    assignment_notes: Optional[str] = None
    last_location_update: Optional[datetime] = None
    current_latitude: Optional[Decimal] = None
    current_longitude: Optional[Decimal] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CourierAvailability(BaseModel):
    """Courier availability for dispatch"""
    courier_id: int
    courier_name: str
    is_available: bool
    current_location_lat: Optional[float] = None
    current_location_lng: Optional[float] = None
    distance_to_pickup_km: Optional[float] = None
    current_load: int
    max_capacity: int
    rating: Optional[Decimal] = None
    estimated_arrival_minutes: Optional[int] = None
    zone_id: Optional[int] = None


class DispatchRecommendation(BaseModel):
    """AI-powered dispatch recommendation"""
    recommended_courier_id: int
    courier_name: str
    confidence_score: float = Field(..., ge=0, le=1)
    distance_km: float
    estimated_time_minutes: int
    courier_current_load: int
    courier_rating: Decimal
    reasoning: str
    alternative_couriers: List[CourierAvailability] = []


class DispatchMetrics(BaseModel):
    """Dispatch performance metrics"""
    period: str
    total_assignments: int
    successful_assignments: int
    rejected_assignments: int
    avg_assignment_time_seconds: float
    avg_acceptance_time_seconds: float
    reassignment_rate: float
    avg_courier_load: float
    zone_coverage_rate: float

    model_config = ConfigDict(from_attributes=True)
