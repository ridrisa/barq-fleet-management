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
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"
    RETIRED = "retired"
    REPAIR = "repair"


@strawberry.enum
class VehicleType(Enum):
    MOTORCYCLE = "motorcycle"
    CAR = "car"
    VAN = "van"
    TRUCK = "truck"
    BICYCLE = "bicycle"


@strawberry.enum
class FuelType(Enum):
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"


@strawberry.enum
class OwnershipType(Enum):
    OWNED = "owned"
    LEASED = "leased"
    RENTED = "rented"


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
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    ONBOARDING = "onboarding"
    SUSPENDED = "suspended"


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
    base_salary: float
    allowances: float
    deductions: float
    loan_deduction: float
    gosi_employee: float
    gross_salary: float
    net_salary: float
    payment_date: Optional[date]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


@strawberry.type
class BonusType:
    id: int
    courier_id: int
    amount: float
    bonus_type: str
    reason: Optional[str]
    bonus_date: date
    created_at: datetime


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
