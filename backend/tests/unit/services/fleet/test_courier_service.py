"""
Unit Tests for Courier Service

Tests cover:
- Courier CRUD operations
- Status management
- Vehicle assignment
- Document expiry tracking
- Search functionality
- Statistics

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch

from app.services.fleet.courier import CourierService, courier_service
from app.models.fleet.courier import Courier, CourierStatus, SponsorshipStatus, ProjectType


class TestCourierService:
    """Test Courier Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create CourierService instance"""
        return CourierService(Courier)

    # ==================== CRUD TESTS ====================

    def test_create_courier_success(self, service, db_session, test_organization):
        """Test successful courier creation"""
        from app.schemas.fleet import CourierCreate

        courier_data = CourierCreate(
            barq_id="BRQ-NEW-001",
            full_name="Test Courier",
            email="newcourier@test.com",
            mobile_number="+966501234567",
            employee_id="EMP-NEW-001",
            status=CourierStatus.ACTIVE,
            sponsorship_status=SponsorshipStatus.INHOUSE,
            project_type=ProjectType.BARQ,
            city="Riyadh",
            nationality="Saudi Arabia",
            organization_id=test_organization.id
        )

        courier = service.create(db_session, obj_in=courier_data)

        assert courier is not None
        assert courier.barq_id == "BRQ-NEW-001"
        assert courier.full_name == "Test Courier"
        assert courier.status == CourierStatus.ACTIVE

    def test_get_courier_by_id(self, service, db_session, courier_factory):
        """Test getting courier by ID"""
        courier = courier_factory()

        result = service.get(db_session, courier.id)

        assert result is not None
        assert result.id == courier.id

    def test_get_by_barq_id_exists(self, service, db_session, courier_factory):
        """Test getting courier by BARQ ID when exists"""
        courier = courier_factory(barq_id="BRQ-TEST-001")

        result = service.get_by_barq_id(db_session, "BRQ-TEST-001")

        assert result is not None
        assert result.barq_id == "BRQ-TEST-001"

    def test_get_by_barq_id_not_exists(self, service, db_session):
        """Test getting courier by BARQ ID when not exists"""
        result = service.get_by_barq_id(db_session, "BRQ-NONEXISTENT")

        assert result is None

    def test_get_by_email_exists(self, service, db_session, courier_factory):
        """Test getting courier by email when exists"""
        courier = courier_factory(email="courier@test.com")

        result = service.get_by_email(db_session, "courier@test.com")

        assert result is not None
        assert result.email == "courier@test.com"

    def test_get_by_email_not_exists(self, service, db_session):
        """Test getting courier by email when not exists"""
        result = service.get_by_email(db_session, "nonexistent@test.com")

        assert result is None

    def test_get_by_employee_id_exists(self, service, db_session, courier_factory):
        """Test getting courier by employee ID when exists"""
        courier = courier_factory(employee_id="EMP-FIND-001")

        result = service.get_by_employee_id(db_session, "EMP-FIND-001")

        assert result is not None
        assert result.employee_id == "EMP-FIND-001"

    def test_get_by_employee_id_not_exists(self, service, db_session):
        """Test getting courier by employee ID when not exists"""
        result = service.get_by_employee_id(db_session, "EMP-NONEXISTENT")

        assert result is None

    # ==================== STATUS FILTER TESTS ====================

    def test_get_active_couriers(self, service, db_session, courier_factory):
        """Test getting all active couriers"""
        # Create active and inactive couriers
        active1 = courier_factory(status=CourierStatus.ACTIVE)
        active2 = courier_factory(status=CourierStatus.ACTIVE)
        inactive = courier_factory(status=CourierStatus.TERMINATED)

        result = service.get_active_couriers(db_session)

        assert len(result) >= 2
        assert all(c.status == CourierStatus.ACTIVE for c in result)

    def test_get_active_couriers_by_city(self, service, db_session, courier_factory):
        """Test getting active couriers filtered by city"""
        riyadh_courier = courier_factory(status=CourierStatus.ACTIVE, city="Riyadh")
        jeddah_courier = courier_factory(status=CourierStatus.ACTIVE, city="Jeddah")

        result = service.get_active_couriers(db_session, city="Riyadh")

        assert len(result) >= 1
        assert all(c.city == "Riyadh" for c in result)

    def test_get_by_status(self, service, db_session, courier_factory):
        """Test getting couriers by specific status"""
        on_leave = courier_factory(status=CourierStatus.ON_LEAVE)
        active = courier_factory(status=CourierStatus.ACTIVE)

        result = service.get_by_status(db_session, CourierStatus.ON_LEAVE)

        assert len(result) >= 1
        assert all(c.status == CourierStatus.ON_LEAVE for c in result)

    def test_get_without_vehicle(self, service, db_session, courier_factory):
        """Test getting active couriers without vehicles"""
        without_vehicle = courier_factory(status=CourierStatus.ACTIVE, current_vehicle_id=None)

        result = service.get_without_vehicle(db_session)

        assert len(result) >= 1
        assert all(c.current_vehicle_id is None for c in result)

    def test_get_by_city(self, service, db_session, courier_factory):
        """Test getting couriers by city"""
        riyadh1 = courier_factory(city="Riyadh")
        riyadh2 = courier_factory(city="Riyadh")
        jeddah = courier_factory(city="Jeddah")

        result = service.get_by_city(db_session, "Riyadh")

        assert len(result) >= 2
        assert all(c.city == "Riyadh" for c in result)

    # ==================== VEHICLE ASSIGNMENT TESTS ====================

    def test_assign_vehicle(self, service, db_session, courier_factory, vehicle_factory):
        """Test assigning vehicle to courier"""
        courier = courier_factory()
        vehicle = vehicle_factory()

        result = service.assign_vehicle(db_session, courier.id, vehicle.id)

        assert result is not None
        assert result.current_vehicle_id == vehicle.id

    def test_unassign_vehicle(self, service, db_session, courier_factory, vehicle_factory):
        """Test unassigning vehicle from courier"""
        courier = courier_factory()
        vehicle = vehicle_factory()

        # First assign
        service.assign_vehicle(db_session, courier.id, vehicle.id)

        # Then unassign
        result = service.unassign_vehicle(db_session, courier.id)

        assert result is not None
        assert result.current_vehicle_id is None

    # ==================== STATUS UPDATE TESTS ====================

    def test_update_status_to_active(self, service, db_session, courier_factory):
        """Test updating courier status to active"""
        courier = courier_factory(status=CourierStatus.ON_LEAVE)

        result = service.update_status(db_session, courier.id, CourierStatus.ACTIVE)

        assert result is not None
        assert result.status == CourierStatus.ACTIVE

    def test_update_status_to_terminated(self, service, db_session, courier_factory):
        """Test updating courier status to terminated with last working day"""
        courier = courier_factory(status=CourierStatus.ACTIVE)
        last_day = date.today()

        result = service.update_status(
            db_session,
            courier.id,
            CourierStatus.TERMINATED,
            last_working_day=last_day
        )

        assert result is not None
        assert result.status == CourierStatus.TERMINATED
        assert result.last_working_day == last_day

    def test_update_status_to_on_leave(self, service, db_session, courier_factory):
        """Test updating courier status to on leave"""
        courier = courier_factory(status=CourierStatus.ACTIVE)

        result = service.update_status(db_session, courier.id, CourierStatus.ON_LEAVE)

        assert result is not None
        assert result.status == CourierStatus.ON_LEAVE

    # ==================== DOCUMENT EXPIRY TESTS ====================

    def test_get_expiring_documents_iqama(self, service, db_session, courier_factory):
        """Test getting couriers with expiring iqama"""
        expiring_iqama = courier_factory(
            status=CourierStatus.ACTIVE,
            iqama_expiry_date=date.today() + timedelta(days=15)
        )
        valid_iqama = courier_factory(
            status=CourierStatus.ACTIVE,
            iqama_expiry_date=date.today() + timedelta(days=60)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        expiring_ids = [doc.courier_id for doc in result]
        assert expiring_iqama.id in expiring_ids

    def test_get_expiring_documents_passport(self, service, db_session, courier_factory):
        """Test getting couriers with expiring passport"""
        expiring_passport = courier_factory(
            status=CourierStatus.ACTIVE,
            passport_expiry_date=date.today() + timedelta(days=20)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        assert len(result) >= 1

    def test_get_expiring_documents_license(self, service, db_session, courier_factory):
        """Test getting couriers with expiring license"""
        expiring_license = courier_factory(
            status=CourierStatus.ACTIVE,
            license_expiry_date=date.today() + timedelta(days=10)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        assert len(result) >= 1

    def test_get_expiring_documents_already_expired(self, service, db_session, courier_factory):
        """Test getting couriers with already expired documents"""
        expired = courier_factory(
            status=CourierStatus.ACTIVE,
            iqama_expiry_date=date.today() - timedelta(days=5)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        expired_docs = [doc for doc in result if doc.courier_id == expired.id]
        assert len(expired_docs) >= 1
        if expired_docs:
            assert expired_docs[0].any_expired is True

    # ==================== STATISTICS TESTS ====================

    def test_get_statistics(self, service, db_session, courier_factory):
        """Test getting courier statistics"""
        # Create couriers with different statuses
        courier_factory(status=CourierStatus.ACTIVE)
        courier_factory(status=CourierStatus.ACTIVE)
        courier_factory(status=CourierStatus.ON_LEAVE)
        courier_factory(status=CourierStatus.TERMINATED)

        stats = service.get_statistics(db_session)

        assert "total" in stats
        assert "status_breakdown" in stats
        assert "with_vehicle" in stats
        assert "without_vehicle" in stats
        assert "sponsorship_breakdown" in stats
        assert "project_breakdown" in stats
        assert stats["total"] >= 4

    def test_get_statistics_by_organization(self, service, db_session, courier_factory, test_organization):
        """Test getting courier statistics filtered by organization"""
        courier_factory(status=CourierStatus.ACTIVE, organization_id=test_organization.id)
        courier_factory(status=CourierStatus.ACTIVE, organization_id=test_organization.id)

        stats = service.get_statistics(db_session, organization_id=test_organization.id)

        assert stats["total"] >= 2

    # ==================== SEARCH TESTS ====================

    def test_search_couriers_by_name(self, service, db_session, courier_factory):
        """Test searching couriers by name"""
        courier = courier_factory(full_name="Ahmad Hassan Al-Fahad")

        result = service.search_couriers(db_session, search_term="Ahmad")

        assert len(result) >= 1
        assert any(c.full_name == "Ahmad Hassan Al-Fahad" for c in result)

    def test_search_couriers_by_barq_id(self, service, db_session, courier_factory):
        """Test searching couriers by BARQ ID"""
        courier = courier_factory(barq_id="BRQ-SEARCH-999")

        result = service.search_couriers(db_session, search_term="SEARCH-999")

        assert len(result) >= 1
        assert any(c.barq_id == "BRQ-SEARCH-999" for c in result)

    def test_search_couriers_by_email(self, service, db_session, courier_factory):
        """Test searching couriers by email"""
        courier = courier_factory(email="searchable@test.com")

        result = service.search_couriers(db_session, search_term="searchable")

        assert len(result) >= 1

    def test_search_couriers_by_phone(self, service, db_session, courier_factory):
        """Test searching couriers by phone number"""
        courier = courier_factory(mobile_number="+966555123456")

        result = service.search_couriers(db_session, search_term="555123456")

        assert len(result) >= 1

    def test_search_couriers_no_results(self, service, db_session):
        """Test searching with no matching results"""
        result = service.search_couriers(db_session, search_term="XYZNOMATCH")

        assert len(result) == 0

    def test_search_couriers_case_insensitive(self, service, db_session, courier_factory):
        """Test search is case insensitive"""
        courier = courier_factory(full_name="Mohammed Al-Saud")

        result_lower = service.search_couriers(db_session, search_term="mohammed")
        result_upper = service.search_couriers(db_session, search_term="MOHAMMED")

        assert len(result_lower) >= 1
        assert len(result_upper) >= 1

    # ==================== PAGINATION TESTS ====================

    def test_get_active_couriers_pagination(self, service, db_session, courier_factory):
        """Test pagination for active couriers"""
        for _ in range(5):
            courier_factory(status=CourierStatus.ACTIVE)

        first_page = service.get_active_couriers(db_session, skip=0, limit=2)
        second_page = service.get_active_couriers(db_session, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
        # Ensure different couriers
        first_ids = {c.id for c in first_page}
        second_ids = {c.id for c in second_page}
        assert first_ids.isdisjoint(second_ids)

    def test_search_couriers_pagination(self, service, db_session, courier_factory):
        """Test pagination for search results"""
        for i in range(5):
            courier_factory(full_name=f"Test Courier {i}", city="TestCity")

        first_page = service.search_couriers(db_session, search_term="Test Courier", skip=0, limit=2)
        second_page = service.search_couriers(db_session, search_term="Test Courier", skip=2, limit=2)

        assert len(first_page) <= 2
        assert len(second_page) <= 2

    # ==================== ORGANIZATION FILTER TESTS ====================

    def test_get_active_couriers_by_organization(self, service, db_session, courier_factory, test_organization, second_organization):
        """Test getting active couriers filtered by organization"""
        org1_courier = courier_factory(status=CourierStatus.ACTIVE, organization_id=test_organization.id)
        org2_courier = courier_factory(status=CourierStatus.ACTIVE, organization_id=second_organization.id)

        result = service.get_active_couriers(db_session, organization_id=test_organization.id)

        assert all(c.organization_id == test_organization.id for c in result)

    def test_search_couriers_by_organization(self, service, db_session, courier_factory, test_organization):
        """Test searching couriers filtered by organization"""
        courier = courier_factory(full_name="Org Specific Courier", organization_id=test_organization.id)

        result = service.search_couriers(
            db_session,
            search_term="Org Specific",
            organization_id=test_organization.id
        )

        assert len(result) >= 1
        assert all(c.organization_id == test_organization.id for c in result)
