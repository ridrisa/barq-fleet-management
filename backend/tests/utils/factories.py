"""
Test Data Factories for BARQ Fleet Management System

This module provides factory functions for creating test data using the Factory Boy pattern.
Each factory creates model instances with realistic default values.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any
from decimal import Decimal

from factory import Factory, Faker, LazyAttribute, SubFactory, Sequence
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker as FakerInstance

from app.models.user import User
from app.models.role import Role
from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType
from app.models.fleet.assignment import CourierVehicleAssignment, AssignmentStatus, AssignmentType
from app.models.fleet.maintenance import VehicleMaintenance, MaintenanceType, MaintenanceStatus
from app.models.fleet.fuel_log import FuelLog
from app.models.hr.leave import Leave, LeaveType, LeaveStatus
from app.models.hr.loan import Loan, LoanStatus
from app.models.hr.salary import Salary
from app.models.hr.attendance import Attendance, AttendanceStatus
from app.models.hr.bonus import Bonus, BonusType
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.models.operations.cod import COD, CODStatus
from app.models.operations.route import Route, RouteStatus
from app.models.operations.incident import Incident, IncidentType, IncidentStatus
from app.models.support.ticket import Ticket, TicketPriority, TicketStatus
from app.models.workflow.template import WorkflowTemplate
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.core.security import PasswordHasher

fake = FakerInstance()


# ==================== Base Factory Configuration ====================

class BaseFactory(SQLAlchemyModelFactory):
    """Base factory with common configuration"""

    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "commit"


# ==================== User & Auth Factories ====================

class UserFactory(BaseFactory):
    """Factory for creating User instances"""

    class Meta:
        model = User

    email = Faker('email')
    full_name = Faker('name')
    hashed_password = LazyAttribute(lambda _: PasswordHasher.hash_password("Test@1234"))
    is_active = True
    is_superuser = False
    role = "user"
    phone_number = Faker('phone_number')


class AdminUserFactory(UserFactory):
    """Factory for creating Admin User instances"""

    email = Sequence(lambda n: f"admin{n}@barq.com")
    full_name = "Admin User"
    is_superuser = True
    role = "admin"


class ManagerUserFactory(UserFactory):
    """Factory for creating Manager User instances"""

    email = Sequence(lambda n: f"manager{n}@barq.com")
    full_name = "Manager User"
    role = "manager"


# ==================== Fleet Management Factories ====================

class CourierFactory(BaseFactory):
    """Factory for creating Courier instances"""

    class Meta:
        model = Courier

    barq_id = Sequence(lambda n: f"BRQ-{1000 + n}")
    full_name = Faker('name')
    email = Faker('email')
    mobile_number = "+966501234567"
    employee_id = Sequence(lambda n: f"EMP-{1000 + n}")
    status = CourierStatus.ACTIVE
    sponsorship_status = SponsorshipStatus.INHOUSE
    project_type = ProjectType.BARQ
    city = "Riyadh"
    nationality = "Saudi Arabia"
    position = "Courier"
    hiring_date = LazyAttribute(lambda _: (datetime.now() - timedelta(days=180)).date())


class VehicleFactory(BaseFactory):
    """Factory for creating Vehicle instances"""

    class Meta:
        model = Vehicle

    plate_number = Sequence(lambda n: f"ABC-{1000 + n}")
    vehicle_type = VehicleType.MOTORCYCLE
    make = "Honda"
    model = "Wave 110"
    year = 2023
    status = VehicleStatus.ACTIVE
    city = "Riyadh"
    vin = Sequence(lambda n: f"VIN{n:017d}")
    registration_date = LazyAttribute(lambda _: (datetime.now() - timedelta(days=365)).date())


class AssignmentFactory(BaseFactory):
    """Factory for creating Assignment instances"""

    class Meta:
        model = CourierVehicleAssignment

    status = AssignmentStatus.ACTIVE
    start_date = LazyAttribute(lambda _: datetime.now().date())
    notes = "Test assignment"


class MaintenanceFactory(BaseFactory):
    """Factory for creating Maintenance instances"""

    class Meta:
        model = VehicleMaintenance

    maintenance_type = MaintenanceType.ROUTINE
    status = MaintenanceStatus.SCHEDULED
    scheduled_date = LazyAttribute(lambda _: (datetime.now() + timedelta(days=7)).date())
    description = "Routine maintenance check"
    estimated_cost = Decimal("500.00")


class FuelLogFactory(BaseFactory):
    """Factory for creating FuelLog instances"""

    class Meta:
        model = FuelLog

    liters = Decimal("10.5")
    cost = Decimal("52.50")
    odometer_reading = Sequence(lambda n: 10000 + (n * 100))
    fuel_date = LazyAttribute(lambda _: datetime.now().date())
    station_name = "Shell Station"


# ==================== HR Management Factories ====================

class LeaveFactory(BaseFactory):
    """Factory for creating Leave instances"""

    class Meta:
        model = Leave

    leave_type = LeaveType.ANNUAL
    start_date = LazyAttribute(lambda _: (datetime.now() + timedelta(days=7)).date())
    end_date = LazyAttribute(lambda _: (datetime.now() + timedelta(days=12)).date())
    reason = "Personal vacation"
    status = LeaveStatus.PENDING


class LoanFactory(BaseFactory):
    """Factory for creating Loan instances"""

    class Meta:
        model = Loan

    amount = Decimal("5000.00")
    installment_amount = Decimal("500.00")
    remaining_amount = Decimal("5000.00")
    reason = "Personal loan"
    status = LoanStatus.PENDING
    request_date = LazyAttribute(lambda _: datetime.now().date())


class SalaryFactory(BaseFactory):
    """Factory for creating Salary instances"""

    class Meta:
        model = Salary

    basic_salary = Decimal("3000.00")
    housing_allowance = Decimal("500.00")
    transportation_allowance = Decimal("300.00")
    food_allowance = Decimal("200.00")
    month = LazyAttribute(lambda _: datetime.now().month)
    year = LazyAttribute(lambda _: datetime.now().year)
    payment_status = "pending"


class AttendanceFactory(BaseFactory):
    """Factory for creating Attendance instances"""

    class Meta:
        model = Attendance

    date = LazyAttribute(lambda _: datetime.now().date())
    check_in_time = LazyAttribute(lambda _: datetime.now().replace(hour=8, minute=0, second=0))
    status = AttendanceStatus.PRESENT


class BonusFactory(BaseFactory):
    """Factory for creating Bonus instances"""

    class Meta:
        model = Bonus

    amount = Decimal("500.00")
    bonus_type = BonusType.PERFORMANCE
    description = "Monthly performance bonus"
    month = LazyAttribute(lambda _: datetime.now().month)
    year = LazyAttribute(lambda _: datetime.now().year)


# ==================== Operations Factories ====================

class DeliveryFactory(BaseFactory):
    """Factory for creating Delivery instances"""

    class Meta:
        model = Delivery

    tracking_number = Sequence(lambda n: f"TRK-{10000 + n}")
    status = DeliveryStatus.PENDING
    pickup_address = "123 Pickup St, Riyadh"
    delivery_address = "456 Delivery Ave, Riyadh"
    customer_name = Faker('name')
    customer_phone = "+966509876543"
    created_at = LazyAttribute(lambda _: datetime.now())


class CODCollectionFactory(BaseFactory):
    """Factory for creating COD Collection instances"""

    class Meta:
        model = COD

    amount = Decimal("250.00")
    status = CODStatus.COLLECTED
    collection_date = LazyAttribute(lambda _: datetime.now().date())


class RouteFactory(BaseFactory):
    """Factory for creating Route instances"""

    class Meta:
        model = Route

    name = Sequence(lambda n: f"Route-{n}")
    status = RouteStatus.ACTIVE
    start_location = "Warehouse A"
    end_location = "Distribution Center B"
    estimated_duration = 120  # minutes


class IncidentFactory(BaseFactory):
    """Factory for creating Incident instances"""

    class Meta:
        model = Incident

    title = "Test Incident"
    description = "Test incident description"
    incident_type = IncidentType.ACCIDENT
    status = IncidentStatus.REPORTED
    incident_date = LazyAttribute(lambda _: datetime.now())


# ==================== Support System Factories ====================

class TicketFactory(BaseFactory):
    """Factory for creating Support Ticket instances"""

    class Meta:
        model = Ticket

    title = "Test Support Ticket"
    description = "This is a test support ticket"
    priority = TicketPriority.MEDIUM
    status = TicketStatus.OPEN
    category = "technical"


# ==================== Workflow Engine Factories ====================

class WorkflowTemplateFactory(BaseFactory):
    """Factory for creating Workflow Template instances"""

    class Meta:
        model = WorkflowTemplate

    name = Sequence(lambda n: f"Workflow Template {n}")
    description = "Test workflow template"
    category = "leave_approval"
    is_active = True


class WorkflowInstanceFactory(BaseFactory):
    """Factory for creating Workflow Instance instances"""

    class Meta:
        model = WorkflowInstance

    current_state = WorkflowStatus.PENDING
    title = "Test Workflow Instance"


# ==================== Utility Functions ====================

def create_courier_with_salary(session, **kwargs) -> tuple[Courier, Salary]:
    """Create a courier with associated salary record"""
    courier = CourierFactory.create(**kwargs)
    salary = SalaryFactory.create(courier_id=courier.id)
    session.commit()
    return courier, salary


def create_vehicle_assignment(session, courier=None, vehicle=None, **kwargs) -> CourierVehicleAssignment:
    """Create a vehicle assignment with courier and vehicle"""
    if not courier:
        courier = CourierFactory.create()
    if not vehicle:
        vehicle = VehicleFactory.create()

    assignment = AssignmentFactory.create(
        courier_id=courier.id,
        vehicle_id=vehicle.id,
        **kwargs
    )
    session.commit()
    return assignment


def create_delivery_workflow(session, courier=None, **kwargs) -> tuple[Courier, Delivery, WorkflowInstance]:
    """Create a complete delivery workflow scenario"""
    if not courier:
        courier = CourierFactory.create()

    delivery = DeliveryFactory.create(courier_id=courier.id, **kwargs)

    template = WorkflowTemplateFactory.create(category="delivery_approval")
    instance = WorkflowInstanceFactory.create(
        template_id=template.id,
        initiator_id=courier.id,
        entity_type="delivery",
        entity_id=delivery.id
    )

    session.commit()
    return courier, delivery, instance


def create_leave_request_workflow(session, courier=None, **kwargs) -> tuple[Courier, Leave, WorkflowInstance]:
    """Create a complete leave request workflow scenario"""
    if not courier:
        courier = CourierFactory.create()

    leave = LeaveFactory.create(courier_id=courier.id, **kwargs)

    template = WorkflowTemplateFactory.create(category="leave_approval")
    instance = WorkflowInstanceFactory.create(
        template_id=template.id,
        initiator_id=courier.id,
        entity_type="leave",
        entity_id=leave.id
    )

    session.commit()
    return courier, leave, instance
