"""
GraphQL Resolvers for BARQ Fleet
Handles database queries and mutations
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.graphql.types import (
    AssignmentStatus,
    AssignmentType,
    BonusType,
    BuildingType,
    CourierDashboard,
    CourierStatus,
    CourierType,
    FuelType,
    LeaveStatus,
)
from app.graphql.types import LeaveType as LeaveTypeEnum
from app.graphql.types import (
    LeaveTypeGQL,
    LoanStatus,
    LoanType,
    OwnershipType,
    RoomStatus,
    RoomType,
    SalaryType,
    VehicleAssignmentType,
    VehicleStatus,
)
from app.graphql.types import VehicleType as VehicleTypeEnum
from app.graphql.types import (
    VehicleTypeGQL,
)
from app.models.accommodation.building import Building
from app.models.accommodation.room import Room
from app.models.fleet.assignment import CourierVehicleAssignment
from app.models.fleet.courier import Courier
from app.models.fleet.vehicle import Vehicle
from app.models.hr.bonus import Bonus
from app.models.hr.leave import Leave
from app.models.hr.loan import Loan
from app.models.hr.salary import Salary

# ============================================
# CONVERTER FUNCTIONS
# ============================================


def convert_loan(loan: Loan) -> LoanType:
    """Convert SQLAlchemy Loan to GraphQL LoanType"""
    return LoanType(
        id=loan.id,
        courier_id=loan.courier_id,
        amount=float(loan.amount),
        outstanding_balance=float(loan.outstanding_balance),
        monthly_deduction=float(loan.monthly_deduction),
        start_date=loan.start_date,
        end_date=loan.end_date,
        status=LoanStatus(loan.status.value),
        approved_by=loan.approved_by,
        notes=loan.notes,
        created_at=loan.created_at,
        updated_at=loan.updated_at,
    )


def convert_leave(leave: Leave) -> LeaveTypeGQL:
    """Convert SQLAlchemy Leave to GraphQL LeaveTypeGQL"""
    return LeaveTypeGQL(
        id=leave.id,
        courier_id=leave.courier_id,
        leave_type=LeaveTypeEnum(leave.leave_type.value),
        start_date=leave.start_date,
        end_date=leave.end_date,
        days=leave.days,
        reason=leave.reason,
        status=LeaveStatus(leave.status.value),
        approved_by=leave.approved_by,
        approved_at=leave.approved_at,
        notes=leave.notes,
        created_at=leave.created_at,
        updated_at=leave.updated_at,
    )


def convert_salary(salary: Salary) -> SalaryType:
    """Convert SQLAlchemy Salary to GraphQL SalaryType"""
    return SalaryType(
        id=salary.id,
        courier_id=salary.courier_id,
        month=salary.month,
        year=salary.year,
        base_salary=float(salary.base_salary),
        allowances=float(salary.allowances or 0),
        deductions=float(salary.deductions or 0),
        loan_deduction=float(salary.loan_deduction or 0),
        gosi_employee=float(salary.gosi_employee or 0),
        gross_salary=float(salary.gross_salary),
        net_salary=float(salary.net_salary),
        payment_date=salary.payment_date,
        notes=salary.notes,
        created_at=salary.created_at,
        updated_at=salary.updated_at,
    )


def convert_vehicle(vehicle: Vehicle) -> VehicleTypeGQL:
    """Convert SQLAlchemy Vehicle to GraphQL VehicleTypeGQL"""
    return VehicleTypeGQL(
        id=vehicle.id,
        plate_number=vehicle.plate_number,
        vehicle_type=VehicleTypeEnum(vehicle.vehicle_type.value),
        make=vehicle.make,
        model=vehicle.model,
        year=vehicle.year,
        color=vehicle.color,
        status=VehicleStatus(vehicle.status.value),
        ownership_type=(
            OwnershipType(vehicle.ownership_type.value)
            if vehicle.ownership_type
            else OwnershipType.OWNED
        ),
        registration_number=vehicle.registration_number,
        registration_expiry_date=vehicle.registration_expiry_date,
        insurance_company=vehicle.insurance_company,
        insurance_policy_number=vehicle.insurance_policy_number,
        insurance_expiry_date=vehicle.insurance_expiry_date,
        vin_number=vehicle.vin_number,
        engine_number=vehicle.engine_number,
        fuel_type=FuelType(vehicle.fuel_type.value) if vehicle.fuel_type else FuelType.GASOLINE,
        current_mileage=float(vehicle.current_mileage or 0),
        total_trips=vehicle.total_trips or 0,
        total_distance=float(vehicle.total_distance or 0),
        is_available=vehicle.is_available,
        is_service_due=vehicle.is_service_due,
        is_document_expired=vehicle.is_document_expired,
        age_years=vehicle.age_years,
        next_service_due_date=vehicle.next_service_due_date,
        last_service_date=vehicle.last_service_date,
        gps_device_id=vehicle.gps_device_id,
        is_gps_active=vehicle.is_gps_active or False,
        notes=vehicle.notes,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at,
    )


def convert_assignment(assignment: CourierVehicleAssignment) -> VehicleAssignmentType:
    """Convert SQLAlchemy CourierVehicleAssignment to GraphQL VehicleAssignmentType"""
    return VehicleAssignmentType(
        id=assignment.id,
        courier_id=assignment.courier_id,
        vehicle_id=assignment.vehicle_id,
        assignment_type=AssignmentType(assignment.assignment_type.value),
        status=AssignmentStatus(assignment.status.value),
        start_date=assignment.start_date,
        end_date=assignment.end_date,
        start_mileage=assignment.start_mileage,
        end_mileage=assignment.end_mileage,
        assigned_by=assignment.assigned_by,
        assignment_reason=assignment.assignment_reason,
        termination_reason=assignment.termination_reason,
        notes=assignment.notes,
        is_active=assignment.is_active,
        duration_days=assignment.duration_days,
        mileage_used=assignment.mileage_used,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
    )


def convert_courier(courier: Courier) -> CourierType:
    """Convert SQLAlchemy Courier to GraphQL CourierType"""
    return CourierType(
        id=courier.id,
        barq_id=courier.barq_id,
        full_name=courier.full_name,
        email=courier.email,
        mobile_number=courier.mobile_number,
        employee_id=courier.employee_id,
        status=CourierStatus(courier.status.value),
        city=courier.city,
        joining_date=courier.joining_date,
        national_id=courier.national_id,
        nationality=courier.nationality,
        iqama_number=courier.iqama_number,
        iqama_expiry_date=courier.iqama_expiry_date,
        license_number=courier.license_number,
        license_expiry_date=courier.license_expiry_date,
        current_vehicle_id=courier.current_vehicle_id,
        accommodation_building_id=courier.accommodation_building_id,
        accommodation_room_id=courier.accommodation_room_id,
        performance_score=float(courier.performance_score or 0),
        total_deliveries=courier.total_deliveries or 0,
        is_active=courier.is_active,
        has_vehicle=courier.has_vehicle,
        is_document_expired=courier.is_document_expired,
        created_at=courier.created_at,
        updated_at=courier.updated_at,
    )


def convert_building(building: Building) -> BuildingType:
    """Convert SQLAlchemy Building to GraphQL BuildingType"""
    return BuildingType(
        id=building.id,
        name=building.name,
        address=building.address,
        total_rooms=building.total_rooms or 0,
        total_capacity=building.total_capacity or 0,
        notes=building.notes,
        created_at=building.created_at,
        updated_at=building.updated_at,
    )


def convert_room(room: Room) -> RoomType:
    """Convert SQLAlchemy Room to GraphQL RoomType"""
    return RoomType(
        id=room.id,
        building_id=room.building_id,
        room_number=room.room_number,
        capacity=room.capacity,
        occupied=room.occupied or 0,
        status=RoomStatus(room.status.value) if room.status else RoomStatus.AVAILABLE,
        created_at=room.created_at,
        updated_at=room.updated_at,
    )


# ============================================
# QUERY RESOLVERS
# ============================================


class QueryResolvers:
    """Query resolvers for GraphQL"""

    @staticmethod
    def get_courier(db: Session, courier_id: int) -> Optional[CourierType]:
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        return convert_courier(courier) if courier else None

    @staticmethod
    def get_courier_by_barq_id(db: Session, barq_id: str) -> Optional[CourierType]:
        courier = db.query(Courier).filter(Courier.barq_id == barq_id).first()
        return convert_courier(courier) if courier else None

    # HR Queries
    @staticmethod
    def get_courier_loans(db: Session, courier_id: int) -> List[LoanType]:
        loans = db.query(Loan).filter(Loan.courier_id == courier_id).all()
        return [convert_loan(loan) for loan in loans]

    @staticmethod
    def get_courier_active_loans(db: Session, courier_id: int) -> List[LoanType]:
        from app.models.hr.loan import LoanStatus as DBLoanStatus

        loans = (
            db.query(Loan)
            .filter(Loan.courier_id == courier_id, Loan.status == DBLoanStatus.ACTIVE)
            .all()
        )
        return [convert_loan(loan) for loan in loans]

    @staticmethod
    def get_courier_leaves(db: Session, courier_id: int) -> List[LeaveTypeGQL]:
        leaves = db.query(Leave).filter(Leave.courier_id == courier_id).all()
        return [convert_leave(leave) for leave in leaves]

    @staticmethod
    def get_courier_pending_leaves(db: Session, courier_id: int) -> List[LeaveTypeGQL]:
        from app.models.hr.leave import LeaveStatus as DBLeaveStatus

        leaves = (
            db.query(Leave)
            .filter(Leave.courier_id == courier_id, Leave.status == DBLeaveStatus.PENDING)
            .all()
        )
        return [convert_leave(leave) for leave in leaves]

    @staticmethod
    def get_courier_salaries(db: Session, courier_id: int, limit: int = 12) -> List[SalaryType]:
        salaries = (
            db.query(Salary)
            .filter(Salary.courier_id == courier_id)
            .order_by(Salary.year.desc(), Salary.month.desc())
            .limit(limit)
            .all()
        )
        return [convert_salary(salary) for salary in salaries]

    # Fleet Queries
    @staticmethod
    def get_courier_vehicle(db: Session, courier_id: int) -> Optional[VehicleTypeGQL]:
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        if courier and courier.current_vehicle:
            return convert_vehicle(courier.current_vehicle)
        return None

    @staticmethod
    def get_vehicle(db: Session, vehicle_id: int) -> Optional[VehicleTypeGQL]:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        return convert_vehicle(vehicle) if vehicle else None

    @staticmethod
    def get_courier_assignments(db: Session, courier_id: int) -> List[VehicleAssignmentType]:
        assignments = (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.courier_id == courier_id)
            .order_by(CourierVehicleAssignment.start_date.desc())
            .all()
        )
        return [convert_assignment(assignment) for assignment in assignments]

    @staticmethod
    def get_courier_active_assignment(
        db: Session, courier_id: int
    ) -> Optional[VehicleAssignmentType]:
        from app.models.fleet.assignment import AssignmentStatus as DBAssignmentStatus

        assignment = (
            db.query(CourierVehicleAssignment)
            .filter(
                CourierVehicleAssignment.courier_id == courier_id,
                CourierVehicleAssignment.status == DBAssignmentStatus.ACTIVE,
            )
            .first()
        )
        return convert_assignment(assignment) if assignment else None

    # Accommodation Queries
    @staticmethod
    def get_buildings(db: Session) -> List[BuildingType]:
        buildings = db.query(Building).all()
        return [convert_building(building) for building in buildings]

    @staticmethod
    def get_building(db: Session, building_id: int) -> Optional[BuildingType]:
        building = db.query(Building).filter(Building.id == building_id).first()
        return convert_building(building) if building else None

    @staticmethod
    def get_building_rooms(db: Session, building_id: int) -> List[RoomType]:
        rooms = db.query(Room).filter(Room.building_id == building_id).all()
        return [convert_room(room) for room in rooms]

    @staticmethod
    def get_room(db: Session, room_id: int) -> Optional[RoomType]:
        room = db.query(Room).filter(Room.id == room_id).first()
        return convert_room(room) if room else None

    @staticmethod
    def get_courier_accommodation(db: Session, courier_id: int) -> Optional[RoomType]:
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        if courier and courier.accommodation_room_id:
            room = db.query(Room).filter(Room.id == courier.accommodation_room_id).first()
            return convert_room(room) if room else None
        return None

    # Dashboard
    @staticmethod
    def get_courier_dashboard(db: Session, courier_id: int) -> Optional[CourierDashboard]:
        courier = db.query(Courier).filter(Courier.id == courier_id).first()
        if not courier:
            return None

        return CourierDashboard(
            courier=convert_courier(courier),
            current_vehicle=(
                convert_vehicle(courier.current_vehicle) if courier.current_vehicle else None
            ),
            active_loans=QueryResolvers.get_courier_active_loans(db, courier_id),
            pending_leaves=QueryResolvers.get_courier_pending_leaves(db, courier_id),
            recent_salaries=QueryResolvers.get_courier_salaries(db, courier_id, limit=3),
            accommodation=QueryResolvers.get_courier_accommodation(db, courier_id),
        )
