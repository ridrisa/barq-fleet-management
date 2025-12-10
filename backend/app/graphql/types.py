"""
GraphQL Type Definitions for BARQ Fleet
Maps SQLAlchemy models to Strawberry GraphQL types
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

import strawberry

# ============================================
# ENUMS
# ============================================


@strawberry.enum
class LoanStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@strawberry.enum
class BonusTypeEnum(Enum):
    """Type of bonus"""
    PERFORMANCE = "performance"
    ATTENDANCE = "attendance"
    SEASONAL = "seasonal"
    SPECIAL = "special"


@strawberry.enum
class PaymentStatus(Enum):
    """Payment status for bonuses"""
    PENDING = "pending"
    APPROVED = "approved"
    PAID = "paid"


@strawberry.enum
class LeaveType(Enum):
    ANNUAL = "annual"
    SICK = "sick"
    EMERGENCY = "emergency"
    UNPAID = "unpaid"


@strawberry.enum
class LeaveStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@strawberry.enum
class VehicleStatus(Enum):
    # Values match PostgreSQL enum (uppercase)
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    INACTIVE = "INACTIVE"
    RETIRED = "RETIRED"
    REPAIR = "REPAIR"


@strawberry.enum
class VehicleType(Enum):
    # Values match PostgreSQL enum (uppercase)
    MOTORCYCLE = "MOTORCYCLE"
    CAR = "CAR"
    VAN = "VAN"
    TRUCK = "TRUCK"
    BICYCLE = "BICYCLE"


@strawberry.enum
class FuelType(Enum):
    # Values match PostgreSQL enum (uppercase)
    GASOLINE = "GASOLINE"
    DIESEL = "DIESEL"
    ELECTRIC = "ELECTRIC"
    HYBRID = "HYBRID"


@strawberry.enum
class OwnershipType(Enum):
    # Values match PostgreSQL enum (uppercase)
    OWNED = "OWNED"
    LEASED = "LEASED"
    RENTED = "RENTED"


@strawberry.enum
class AssignmentType(Enum):
    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    TRIAL = "trial"


@strawberry.enum
class AssignmentStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@strawberry.enum
class CourierStatus(Enum):
    # Values match PostgreSQL enum (uppercase)
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"
    ONBOARDING = "ONBOARDING"
    SUSPENDED = "SUSPENDED"


@strawberry.enum
class RoomStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    MAINTENANCE = "maintenance"


# ============================================
# HR TYPES
# ============================================


@strawberry.type
class LoanType:
    id: int
    courier_id: int
    amount: float
    outstanding_balance: float
    monthly_deduction: float
    start_date: date
    end_date: Optional[date]
    status: LoanStatus
    approved_by: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class LeaveTypeGQL:
    id: int
    courier_id: int
    leave_type: LeaveType
    start_date: date
    end_date: date
    days: int
    reason: Optional[str]
    status: LeaveStatus
    approved_by: Optional[int]
    approved_at: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class SalaryType:
    id: int
    courier_id: int
    month: int
    year: int
    # Category-based payroll fields
    category: Optional[str]
    period_start: Optional[date]
    period_end: Optional[date]
    # Performance metrics (from BigQuery)
    total_orders: Optional[int]
    total_revenue: Optional[float]
    gas_usage: Optional[float]
    # Target and calculation
    target: Optional[float]
    daily_target: Optional[float]
    days_since_joining: Optional[int]
    # Salary components
    base_salary: float
    bonus_amount: Optional[float]
    # Gas/Fuel components
    gas_deserved: Optional[float]
    gas_difference: Optional[float]
    # Legacy fields
    allowances: float
    deductions: float
    loan_deduction: float
    gosi_employee: float
    # Calculated totals
    gross_salary: float
    net_salary: float
    # Payment tracking
    payment_date: Optional[date]
    is_paid: Optional[int]
    # Audit fields
    notes: Optional[str]
    calculation_details: Optional[str]
    generated_date: Optional[date]
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class BonusTypeGQL:
    """Bonus/penalty record from HR dashboard"""
    id: int
    courier_id: int
    bonus_type: BonusTypeEnum
    amount: float
    bonus_date: date
    payment_status: PaymentStatus
    approved_by: Optional[int]
    approval_date: Optional[date]
    description: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    @strawberry.field
    def is_penalty(self) -> bool:
        """Returns True if amount is negative (penalty)"""
        return self.amount < 0


# ============================================
# FLEET TYPES
# ============================================


@strawberry.type
class VehicleTypeGQL:
    id: int
    plate_number: str
    vehicle_type: VehicleType
    make: str
    model: str
    year: int
    color: Optional[str]
    status: VehicleStatus
    ownership_type: OwnershipType
    registration_number: Optional[str]
    registration_expiry_date: Optional[date]
    insurance_company: Optional[str]
    insurance_policy_number: Optional[str]
    insurance_expiry_date: Optional[date]
    vin_number: Optional[str]
    engine_number: Optional[str]
    fuel_type: FuelType
    current_mileage: float
    total_trips: int
    total_distance: float
    is_available: bool
    is_service_due: bool
    is_document_expired: bool
    age_years: int
    next_service_due_date: Optional[date]
    last_service_date: Optional[date]
    gps_device_id: Optional[str]
    is_gps_active: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class VehicleAssignmentType:
    id: int
    courier_id: int
    vehicle_id: int
    assignment_type: AssignmentType
    status: AssignmentStatus
    start_date: date
    end_date: Optional[date]
    start_mileage: Optional[int]
    end_mileage: Optional[int]
    assigned_by: Optional[str]
    assignment_reason: Optional[str]
    termination_reason: Optional[str]
    notes: Optional[str]
    is_active: bool
    duration_days: int
    mileage_used: int
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class CourierType:
    id: int
    barq_id: str
    full_name: str
    email: Optional[str]
    mobile_number: str
    employee_id: Optional[str]
    status: CourierStatus
    city: Optional[str]
    joining_date: Optional[date]
    national_id: Optional[str]
    nationality: Optional[str]
    iqama_number: Optional[str]
    iqama_expiry_date: Optional[date]
    license_number: Optional[str]
    license_expiry_date: Optional[date]
    current_vehicle_id: Optional[int]
    accommodation_building_id: Optional[int]
    accommodation_room_id: Optional[int]
    performance_score: float
    total_deliveries: int
    is_active: bool
    has_vehicle: bool
    is_document_expired: bool
    created_at: datetime
    updated_at: Optional[datetime]


# ============================================
# ACCOMMODATION TYPES
# ============================================


@strawberry.type
class BuildingType:
    id: int
    name: str
    address: str
    total_rooms: int
    total_capacity: int
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class RoomType:
    id: int
    building_id: int
    room_number: str
    capacity: int
    occupied: int
    status: RoomStatus
    created_at: datetime
    updated_at: Optional[datetime]

    @strawberry.field
    def available_beds(self) -> int:
        return self.capacity - self.occupied


# ============================================
# INPUT TYPES
# ============================================


@strawberry.input
class LeaveRequestInput:
    leave_type: LeaveType
    start_date: date
    end_date: date
    days: int
    reason: Optional[str] = None


@strawberry.input
class LoanRequestInput:
    amount: float
    monthly_deduction: float
    start_date: date
    reason: Optional[str] = None


# ============================================
# RESPONSE TYPES
# ============================================


@strawberry.type
class MutationResponse:
    success: bool
    message: str
    id: Optional[int] = None


@strawberry.type
class CourierDashboard:
    """Aggregated data for courier dashboard"""

    courier: CourierType
    current_vehicle: Optional[VehicleTypeGQL]
    active_loans: List[LoanType]
    pending_leaves: List[LeaveTypeGQL]
    recent_salaries: List[SalaryType]
    accommodation: Optional[RoomType]


# ============================================
# AUTHENTICATION TYPES (for driver-app)
# ============================================


@strawberry.type
class CityType:
    """City information"""
    name: str
    id: Optional[int] = None


@strawberry.type
class CourierAuthType:
    """Courier profile for authentication response - matches driver-app expectations"""
    id: str
    barq_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: Optional[str] = None
    mobile_number: str
    email: Optional[str] = None
    status: str
    project: Optional[str] = None
    city: Optional[CityType] = None
    rating: Optional[float] = None
    total_deliveries: Optional[int] = None
    completed_orders: Optional[int] = None


@strawberry.type
class AuthResponse:
    """Authentication response matching driver-app expectations"""
    success: bool
    token: Optional[str] = None
    refresh_token: Optional[str] = None
    courier: Optional[CourierAuthType] = None
    error: Optional[str] = None


# ============================================
# DELIVERY TYPES (for driver-app)
# ============================================


@strawberry.enum
class DeliveryStatusGQL(Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    PICKUP_STARTED = "PICKUP_STARTED"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"


@strawberry.enum
class ServiceLevel(Enum):
    BARQ = "BARQ"  # Standard delivery
    BULLET = "BULLET"  # Express delivery


@strawberry.type
class LocationType:
    """GPS location"""
    lat: float
    lng: float
    address: Optional[str] = None


@strawberry.type
class RecipientType:
    """Delivery recipient information"""
    name: str
    phone: str
    address: str
    location: Optional[LocationType] = None


@strawberry.type
class DeliveryTypeGQL:
    """Delivery/Order information for driver app"""
    id: str
    tracking_number: str
    status: DeliveryStatusGQL
    service_level: ServiceLevel
    recipient: RecipientType
    pickup_location: Optional[LocationType] = None
    dropoff_location: Optional[LocationType] = None
    courier_id: Optional[int] = None
    cod_amount: Optional[float] = None
    is_cod: bool
    notes: Optional[str] = None
    estimated_delivery: Optional[datetime] = None
    pickup_time: Optional[datetime] = None
    delivery_time: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


@strawberry.type
class DeliveryListResponse:
    """Paginated list of deliveries"""
    items: List[DeliveryTypeGQL]
    total: int
    has_more: bool


# ============================================
# PERFORMANCE & POINTS TYPES (for driver-app)
# ============================================


@strawberry.type
class PointsSummary:
    """Driver points summary"""
    total_points: int
    weekly_points: int
    monthly_points: int
    daily_points: int
    weekly_target: int
    monthly_target: int
    daily_target: int
    streak: int
    level: int
    level_name: str
    next_level_points: int
    rank: int
    total_drivers: int


@strawberry.type
class PerformanceMetrics:
    """Driver performance metrics"""
    deliveries_completed: int
    deliveries_failed: int
    deliveries_cancelled: int
    on_time_rate: float
    average_rating: float
    total_distance: float
    period: str  # daily, weekly, monthly


@strawberry.type
class LeaderboardEntry:
    """Leaderboard entry"""
    rank: int
    driver_id: str
    name: str
    points: int
    avatar: Optional[str] = None


@strawberry.type
class LeaderboardResponse:
    """Leaderboard response"""
    entries: List[LeaderboardEntry]
    driver_rank: int
    period: str  # weekly, monthly, all_time


# ============================================
# LOCATION TRACKING TYPES
# ============================================


@strawberry.input
class LocationInput:
    """Location update input"""
    lat: float
    lng: float
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None
    timestamp: Optional[datetime] = None


@strawberry.type
class LocationUpdateResponse:
    """Response for location update"""
    success: bool
    message: str


# ============================================
# AUTHENTICATION INPUT TYPES
# ============================================


@strawberry.input
class CourierSigninInput:
    """Input for courier signin - supports phone-based auth"""
    phone: str
    password: str
    device_id: Optional[str] = None
    push_token: Optional[str] = None


@strawberry.input
class RefreshTokenInput:
    """Input for token refresh"""
    refresh_token: str


# ============================================
# DELIVERY MUTATION INPUT TYPES
# ============================================


@strawberry.input
class UpdateDeliveryStatusInput:
    """Input for updating delivery status"""
    status: DeliveryStatusGQL
    location: Optional[LocationInput] = None
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None


@strawberry.type
class DeliveryUpdateResponse:
    """Response for delivery status update"""
    success: bool
    message: str
    delivery_id: Optional[str] = None
    status: Optional[DeliveryStatusGQL] = None


# ============================================
# COURIER MUTATION INPUT TYPES
# ============================================


@strawberry.input
class CourierCreateInput:
    """Input for creating/ensuring a courier exists from driver app login"""
    barq_id: str  # The BARQ ID from login
    full_name: str
    mobile_number: str
    email: Optional[str] = None
    city: Optional[str] = None


@strawberry.type
class EnsureCourierResponse:
    """Response for ensure courier mutation"""
    success: bool
    message: str
    courier_id: Optional[int] = None
    created: bool = False  # True if courier was created, False if already existed
