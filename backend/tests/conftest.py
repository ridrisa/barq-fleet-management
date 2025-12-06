"""
Pytest Configuration and Fixtures for BARQ Fleet Management System

This module provides comprehensive test fixtures including:
- Test database setup (SQLite in-memory)
- Test client for API testing
- Authentication fixtures (users, tokens)
- Database session management
- Mock fixtures for external services
- Factory fixtures for test data generation

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import os
import sys
from typing import Generator, Dict, Any
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import Base
from app.core.database import get_db
from app.core.security import TokenManager, PasswordHasher
from app.models.user import User
from app.models.role import Role
from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType
from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType
from app.models.hr.leave import Leave, LeaveType, LeaveStatus
from app.models.hr.loan import Loan, LoanStatus
from app.models.hr.salary import Salary
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.models.operations.cod import COD, CODStatus
from app.models.support.ticket import Ticket, TicketPriority, TicketStatus
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.models.workflow.template import WorkflowTemplate
from app.models.tenant.organization import Organization
from app.models.tenant.organization_user import OrganizationUser

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

# Use PostgreSQL for tests (required for JSONB columns in analytics models)
TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/barq_fleet_test"
)


# ==================== Database Fixtures ====================

@pytest.fixture(scope="session")
def test_engine():
    """
    Create a test database engine using PostgreSQL

    Scope: session (created once per test session)

    Note: Uses PostgreSQL instead of SQLite because some models
    use PostgreSQL-specific types like JSONB.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    yield engine

    # Cleanup
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Create a new database session for each test

    Scope: function (new session per test)
    Automatically rolls back after each test
    """
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    session = TestSessionLocal()

    # Configure factories to use this session
    from tests.utils.factories import (
        UserFactory, AdminUserFactory, ManagerUserFactory,
        CourierFactory, VehicleFactory, AssignmentFactory,
        MaintenanceFactory, FuelLogFactory,
        LeaveFactory, LoanFactory, SalaryFactory, AttendanceFactory, BonusFactory,
        DeliveryFactory, CODCollectionFactory, RouteFactory, IncidentFactory,
        TicketFactory, WorkflowTemplateFactory, WorkflowInstanceFactory
    )

    # Set session on all factories
    for factory_class in [
        UserFactory, AdminUserFactory, ManagerUserFactory,
        CourierFactory, VehicleFactory, AssignmentFactory,
        MaintenanceFactory, FuelLogFactory,
        LeaveFactory, LoanFactory, SalaryFactory, AttendanceFactory, BonusFactory,
        DeliveryFactory, CODCollectionFactory, RouteFactory, IncidentFactory,
        TicketFactory, WorkflowTemplateFactory, WorkflowInstanceFactory
    ]:
        factory_class._meta.sqlalchemy_session = session

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def test_db(db_session: Session):
    """
    Alias for db_session for backward compatibility
    """
    return db_session


# ==================== FastAPI Client Fixtures ====================

@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create FastAPI test client with database override

    Scope: function (new client per test)
    """
    from app.main import app

    # Override database dependency
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


# ==================== Authentication Fixtures ====================

@pytest.fixture
def test_password() -> str:
    """Standard test password"""
    return "Test@1234"


@pytest.fixture
def test_user(db_session: Session, test_password: str) -> User:
    """
    Create a standard test user
    """
    user = User(
        email="test@barq.com",
        full_name="Test User",
        hashed_password=PasswordHasher.hash_password(test_password),
        is_active=True,
        is_superuser=False,
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session, test_password: str) -> User:
    """
    Create an admin test user
    """
    user = User(
        email="admin@barq.com",
        full_name="Admin User",
        hashed_password=PasswordHasher.hash_password(test_password),
        is_active=True,
        is_superuser=True,
        role="admin"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def manager_user(db_session: Session, test_password: str) -> User:
    """
    Create a manager test user
    """
    user = User(
        email="manager@barq.com",
        full_name="Manager User",
        hashed_password=PasswordHasher.hash_password(test_password),
        is_active=True,
        is_superuser=False,
        role="manager"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_token(test_user: User) -> str:
    """
    Generate JWT token for test user
    """
    return TokenManager.create_access_token(
        data={"sub": str(test_user.id), "email": test_user.email}
    )


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """
    Generate JWT token for admin user
    """
    return TokenManager.create_access_token(
        data={"sub": str(admin_user.id), "email": admin_user.email, "role": "admin"}
    )


@pytest.fixture
def manager_token(manager_user: User) -> str:
    """
    Generate JWT token for manager user
    """
    return TokenManager.create_access_token(
        data={"sub": str(manager_user.id), "email": manager_user.email, "role": "manager"}
    )


@pytest.fixture
def auth_headers(test_token: str) -> Dict[str, str]:
    """
    Create authorization headers for test requests
    """
    return {"Authorization": f"Bearer {test_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> Dict[str, str]:
    """
    Create authorization headers for admin requests
    """
    return {"Authorization": f"Bearer {admin_token}"}


# ==================== Organization Fixtures ====================

@pytest.fixture
def test_organization(db_session: Session) -> Organization:
    """
    Create a test organization
    """
    org = Organization(
        name="Test Organization",
        slug="test-org",
        is_active=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def second_organization(db_session: Session) -> Organization:
    """
    Create a second test organization for isolation tests
    """
    org = Organization(
        name="Second Test Organization",
        slug="second-test-org",
        is_active=True
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


@pytest.fixture
def test_org_user(
    db_session: Session,
    test_user: User,
    test_organization: Organization
) -> OrganizationUser:
    """
    Associate test user with test organization
    """
    org_user = OrganizationUser(
        user_id=test_user.id,
        organization_id=test_organization.id,
        role="ADMIN",
        is_active=True
    )
    db_session.add(org_user)
    db_session.commit()
    db_session.refresh(org_user)
    return org_user


@pytest.fixture
def org_token(test_user: User, test_organization: Organization) -> str:
    """
    Generate JWT token with organization context for test user
    """
    return TokenManager.create_access_token(
        data={
            "sub": str(test_user.id),
            "email": test_user.email,
            "org_id": test_organization.id,
            "org_role": "ADMIN"
        }
    )


@pytest.fixture
def org_headers(org_token: str) -> Dict[str, str]:
    """
    Create authorization headers with organization context
    """
    return {"Authorization": f"Bearer {org_token}"}


@pytest.fixture
def admin_org_token(admin_user: User, test_organization: Organization) -> str:
    """
    Generate JWT token with organization context for admin user
    """
    return TokenManager.create_access_token(
        data={
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "role": "admin",
            "org_id": test_organization.id,
            "org_role": "OWNER"
        }
    )


@pytest.fixture
def admin_org_headers(admin_org_token: str) -> Dict[str, str]:
    """
    Create authorization headers for admin with organization context
    """
    return {"Authorization": f"Bearer {admin_org_token}"}


@pytest.fixture
def organization_factory(db_session: Session):
    """
    Factory for creating test organizations
    """
    def _create_org(**kwargs) -> Organization:
        default_data = {
            "name": f"Org-{datetime.now().timestamp()}",
            "slug": f"org-{datetime.now().timestamp()}",
            "is_active": True
        }
        default_data.update(kwargs)

        org = Organization(**default_data)
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        return org

    return _create_org


# ==================== Model Factory Fixtures ====================

@pytest.fixture
def courier_factory(db_session: Session):
    """
    Factory for creating test couriers
    """
    def _create_courier(**kwargs) -> Courier:
        default_data = {
            "barq_id": f"BRQ-{datetime.now().timestamp()}",
            "full_name": "Test Courier",
            "email": f"courier{datetime.now().timestamp()}@test.com",
            "mobile_number": "+966501234567",
            "employee_id": f"EMP-{datetime.now().timestamp()}",
            "status": CourierStatus.ACTIVE,
            "sponsorship_status": SponsorshipStatus.INHOUSE,
            "project_type": ProjectType.BARQ,
            "city": "Riyadh",
            "nationality": "Saudi Arabia",
        }
        default_data.update(kwargs)

        courier = Courier(**default_data)
        db_session.add(courier)
        db_session.commit()
        db_session.refresh(courier)
        return courier

    return _create_courier


@pytest.fixture
def vehicle_factory(db_session: Session):
    """
    Factory for creating test vehicles
    """
    def _create_vehicle(**kwargs) -> Vehicle:
        default_data = {
            "plate_number": f"ABC-{datetime.now().timestamp()}",
            "vehicle_type": VehicleType.MOTORCYCLE,
            "make": "Honda",
            "model": "Wave 110",
            "year": 2023,
            "status": VehicleStatus.AVAILABLE,
            "city": "Riyadh",
        }
        default_data.update(kwargs)

        vehicle = Vehicle(**default_data)
        db_session.add(vehicle)
        db_session.commit()
        db_session.refresh(vehicle)
        return vehicle

    return _create_vehicle


@pytest.fixture
def leave_factory(db_session: Session):
    """
    Factory for creating test leave requests
    """
    def _create_leave(courier: Courier, **kwargs) -> Leave:
        default_data = {
            "courier_id": courier.id,
            "leave_type": LeaveType.ANNUAL,
            "start_date": datetime.now().date(),
            "end_date": (datetime.now() + timedelta(days=5)).date(),
            "reason": "Personal reasons",
            "status": LeaveStatus.PENDING,
        }
        default_data.update(kwargs)

        leave = Leave(**default_data)
        db_session.add(leave)
        db_session.commit()
        db_session.refresh(leave)
        return leave

    return _create_leave


@pytest.fixture
def loan_factory(db_session: Session):
    """
    Factory for creating test loans
    """
    def _create_loan(courier: Courier, **kwargs) -> Loan:
        default_data = {
            "courier_id": courier.id,
            "amount": 5000.00,
            "installment_amount": 500.00,
            "remaining_amount": 5000.00,
            "reason": "Personal loan",
            "status": LoanStatus.ACTIVE,
        }
        default_data.update(kwargs)

        loan = Loan(**default_data)
        db_session.add(loan)
        db_session.commit()
        db_session.refresh(loan)
        return loan

    return _create_loan


@pytest.fixture
def delivery_factory(db_session: Session):
    """
    Factory for creating test deliveries
    """
    def _create_delivery(courier: Courier, **kwargs) -> Delivery:
        default_data = {
            "courier_id": courier.id,
            "tracking_number": f"TRK-{datetime.now().timestamp()}",
            "status": DeliveryStatus.PENDING,
            "pickup_address": "123 Pickup St, Riyadh",
            "delivery_address": "456 Delivery Ave, Riyadh",
            "customer_name": "Test Customer",
            "customer_phone": "+966509876543",
        }
        default_data.update(kwargs)

        delivery = Delivery(**default_data)
        db_session.add(delivery)
        db_session.commit()
        db_session.refresh(delivery)
        return delivery

    return _create_delivery


@pytest.fixture
def cod_factory(db_session: Session):
    """
    Factory for creating test COD collections
    """
    def _create_cod(courier: Courier, **kwargs) -> CODCollection:
        default_data = {
            "courier_id": courier.id,
            "amount": 250.00,
            "status": CODStatus.COLLECTED,
            "collection_date": datetime.now().date(),
        }
        default_data.update(kwargs)

        cod = CODCollection(**default_data)
        db_session.add(cod)
        db_session.commit()
        db_session.refresh(cod)
        return cod

    return _create_cod


@pytest.fixture
def ticket_factory(db_session: Session):
    """
    Factory for creating test support tickets
    """
    def _create_ticket(user: User, **kwargs) -> Ticket:
        default_data = {
            "title": "Test Support Ticket",
            "description": "This is a test ticket",
            "priority": TicketPriority.MEDIUM,
            "status": TicketStatus.OPEN,
            "requester_id": user.id,
            "category": "technical",
        }
        default_data.update(kwargs)

        ticket = Ticket(**default_data)
        db_session.add(ticket)
        db_session.commit()
        db_session.refresh(ticket)
        return ticket

    return _create_ticket


@pytest.fixture
def workflow_template_factory(db_session: Session):
    """
    Factory for creating test workflow templates
    """
    def _create_workflow_template(**kwargs) -> WorkflowTemplate:
        default_data = {
            "name": "Test Workflow",
            "description": "Test workflow template",
            "category": "leave_approval",
            "is_active": True,
        }
        default_data.update(kwargs)

        template = WorkflowTemplate(**default_data)
        db_session.add(template)
        db_session.commit()
        db_session.refresh(template)
        return template

    return _create_workflow_template


@pytest.fixture
def workflow_instance_factory(db_session: Session):
    """
    Factory for creating test workflow instances
    """
    def _create_workflow_instance(template: WorkflowTemplate, initiator: User, **kwargs) -> WorkflowInstance:
        default_data = {
            "template_id": template.id,
            "initiator_id": initiator.id,
            "current_state": WorkflowStatus.DRAFT,
            "title": "Test Workflow Instance",
        }
        default_data.update(kwargs)

        instance = WorkflowInstance(**default_data)
        db_session.add(instance)
        db_session.commit()
        db_session.refresh(instance)
        return instance

    return _create_workflow_instance


# ==================== Mock Service Fixtures ====================

@pytest.fixture
def mock_email_service(mocker):
    """
    Mock email notification service
    """
    return mocker.patch("app.services.email_notification_service.EmailNotificationService.send_email")


@pytest.fixture
def mock_sms_service(mocker):
    """
    Mock SMS notification service
    """
    return mocker.patch("app.services.sms_notification_service.SMSNotificationService.send_sms")


@pytest.fixture
def mock_redis(mocker):
    """
    Mock Redis cache
    """
    return mocker.patch("redis.Redis")


# ==================== Test Data Fixtures ====================

@pytest.fixture
def sample_courier_data() -> Dict[str, Any]:
    """
    Sample courier data for API tests
    """
    return {
        "barq_id": "BRQ-TEST-001",
        "full_name": "Ahmad Hassan",
        "email": "ahmad.hassan@test.com",
        "mobile_number": "+966501234567",
        "employee_id": "EMP-001",
        "status": "active",
        "sponsorship_status": "inhouse",
        "project_type": "barq",
        "city": "Riyadh",
        "nationality": "Saudi Arabia",
        "position": "Courier",
    }


@pytest.fixture
def sample_vehicle_data() -> Dict[str, Any]:
    """
    Sample vehicle data for API tests
    """
    return {
        "plate_number": "ABC-1234",
        "vehicle_type": "motorcycle",
        "make": "Honda",
        "model": "Wave 110",
        "year": 2023,
        "status": "available",
        "city": "Riyadh",
    }


@pytest.fixture
def sample_leave_data() -> Dict[str, Any]:
    """
    Sample leave request data for API tests
    """
    return {
        "leave_type": "annual",
        "start_date": datetime.now().date().isoformat(),
        "end_date": (datetime.now() + timedelta(days=5)).date().isoformat(),
        "reason": "Family vacation",
    }


@pytest.fixture
def sample_delivery_data() -> Dict[str, Any]:
    """
    Sample delivery data for API tests
    """
    return {
        "tracking_number": "TRK-TEST-001",
        "pickup_address": "123 Pickup St, Riyadh",
        "delivery_address": "456 Delivery Ave, Riyadh",
        "customer_name": "Test Customer",
        "customer_phone": "+966509876543",
        "status": "pending",
    }


# ==================== Utility Fixtures ====================

@pytest.fixture
def freeze_time(mocker):
    """
    Freeze time for predictable datetime testing
    """
    from datetime import datetime
    fixed_time = datetime(2025, 1, 15, 12, 0, 0)

    class FrozenDatetime:
        @classmethod
        def now(cls):
            return fixed_time

        @classmethod
        def utcnow(cls):
            return fixed_time

    mocker.patch("datetime.datetime", FrozenDatetime)
    return fixed_time


# ==================== Pytest Configuration ====================

def pytest_configure(config):
    """
    Configure pytest with custom markers
    """
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as security test"
    )


def pytest_collection_modifyitems(config, items):
    """
    Automatically mark tests based on their location
    """
    for item in items:
        # Add markers based on test path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        elif "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)