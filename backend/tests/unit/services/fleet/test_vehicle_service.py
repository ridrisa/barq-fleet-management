"""
Unit Tests for Vehicle Service

Tests cover:
- Vehicle CRUD operations
- Status management
- Service tracking
- Mileage updates
- Document expiry tracking
- Search functionality
- Statistics

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, timedelta
from unittest.mock import Mock, patch

from app.services.fleet.vehicle import VehicleService, vehicle_service
from app.models.fleet.vehicle import Vehicle, VehicleStatus, VehicleType


class TestVehicleService:
    """Test Vehicle Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create VehicleService instance"""
        return VehicleService(Vehicle)

    # ==================== CRUD TESTS ====================

    def test_create_vehicle_success(self, service, db_session, test_organization):
        """Test successful vehicle creation"""
        from app.schemas.fleet import VehicleCreate

        vehicle_data = VehicleCreate(
            plate_number="XYZ-9999",
            vehicle_type=VehicleType.MOTORCYCLE,
            make="Honda",
            model="Wave 110",
            year=2024,
            status=VehicleStatus.ACTIVE,
            city="Riyadh",
            organization_id=test_organization.id
        )

        vehicle = service.create(db_session, obj_in=vehicle_data)

        assert vehicle is not None
        assert vehicle.plate_number == "XYZ-9999"
        assert vehicle.vehicle_type == VehicleType.MOTORCYCLE
        assert vehicle.status == VehicleStatus.ACTIVE

    def test_get_vehicle_by_id(self, service, db_session, vehicle_factory):
        """Test getting vehicle by ID"""
        vehicle = vehicle_factory()

        result = service.get(db_session, vehicle.id)

        assert result is not None
        assert result.id == vehicle.id

    def test_get_by_plate_number_exists(self, service, db_session, vehicle_factory):
        """Test getting vehicle by plate number when exists"""
        vehicle = vehicle_factory(plate_number="ABC-1234")

        result = service.get_by_plate_number(db_session, "ABC-1234")

        assert result is not None
        assert result.plate_number == "ABC-1234"

    def test_get_by_plate_number_not_exists(self, service, db_session):
        """Test getting vehicle by plate number when not exists"""
        result = service.get_by_plate_number(db_session, "ZZZ-9999")

        assert result is None

    def test_get_by_vin_exists(self, service, db_session, vehicle_factory):
        """Test getting vehicle by VIN when exists"""
        vehicle = vehicle_factory(vin_number="VIN12345678901234")

        result = service.get_by_vin(db_session, "VIN12345678901234")

        assert result is not None
        assert result.vin_number == "VIN12345678901234"

    def test_get_by_vin_not_exists(self, service, db_session):
        """Test getting vehicle by VIN when not exists"""
        result = service.get_by_vin(db_session, "NONEXISTENTVIN1234")

        assert result is None

    # ==================== STATUS FILTER TESTS ====================

    def test_get_active_vehicles(self, service, db_session, vehicle_factory):
        """Test getting all active vehicles"""
        active1 = vehicle_factory(status=VehicleStatus.ACTIVE)
        active2 = vehicle_factory(status=VehicleStatus.ACTIVE)
        maintenance = vehicle_factory(status=VehicleStatus.MAINTENANCE)

        result = service.get_active_vehicles(db_session)

        assert len(result) >= 2
        assert all(v.status == VehicleStatus.ACTIVE for v in result)

    def test_get_active_vehicles_by_type(self, service, db_session, vehicle_factory):
        """Test getting active vehicles filtered by type"""
        motorcycle = vehicle_factory(status=VehicleStatus.ACTIVE, vehicle_type=VehicleType.MOTORCYCLE)
        car = vehicle_factory(status=VehicleStatus.ACTIVE, vehicle_type=VehicleType.CAR)

        result = service.get_active_vehicles(db_session, vehicle_type=VehicleType.MOTORCYCLE)

        assert len(result) >= 1
        assert all(v.vehicle_type == VehicleType.MOTORCYCLE for v in result)

    def test_get_by_status(self, service, db_session, vehicle_factory):
        """Test getting vehicles by specific status"""
        maintenance = vehicle_factory(status=VehicleStatus.MAINTENANCE)
        active = vehicle_factory(status=VehicleStatus.ACTIVE)

        result = service.get_by_status(db_session, VehicleStatus.MAINTENANCE)

        assert len(result) >= 1
        assert all(v.status == VehicleStatus.MAINTENANCE for v in result)

    def test_get_available_vehicles(self, service, db_session, vehicle_factory):
        """Test getting available vehicles (active and not assigned)"""
        available = vehicle_factory(status=VehicleStatus.ACTIVE)

        result = service.get_available_vehicles(db_session)

        assert len(result) >= 1
        assert all(v.status == VehicleStatus.ACTIVE for v in result)

    def test_get_by_city(self, service, db_session, vehicle_factory):
        """Test getting vehicles by city"""
        riyadh1 = vehicle_factory(assigned_to_city="Riyadh")
        riyadh2 = vehicle_factory(assigned_to_city="Riyadh")
        jeddah = vehicle_factory(assigned_to_city="Jeddah")

        result = service.get_by_city(db_session, "Riyadh")

        assert len(result) >= 2
        assert all(v.assigned_to_city == "Riyadh" for v in result)

    # ==================== SERVICE TRACKING TESTS ====================

    def test_get_due_for_service(self, service, db_session, vehicle_factory):
        """Test getting vehicles due for service"""
        due_soon = vehicle_factory(
            status=VehicleStatus.ACTIVE,
            next_service_due_date=date.today() + timedelta(days=5)
        )
        not_due = vehicle_factory(
            status=VehicleStatus.ACTIVE,
            next_service_due_date=date.today() + timedelta(days=30)
        )

        result = service.get_due_for_service(db_session, days_threshold=7)

        assert len(result) >= 1
        due_ids = [v.id for v in result]
        assert due_soon.id in due_ids

    def test_record_service(self, service, db_session, vehicle_factory):
        """Test recording service completion"""
        vehicle = vehicle_factory()
        service_date = date.today()
        service_mileage = 15000.0
        next_service_date = date.today() + timedelta(days=90)
        next_service_mileage = 20000.0

        result = service.record_service(
            db_session,
            vehicle.id,
            service_date,
            service_mileage,
            next_service_date,
            next_service_mileage
        )

        assert result is not None
        assert result.last_service_date == service_date
        assert result.last_service_mileage == service_mileage
        assert result.next_service_due_date == next_service_date
        assert result.next_service_due_mileage == next_service_mileage

    def test_record_service_without_next_schedule(self, service, db_session, vehicle_factory):
        """Test recording service without scheduling next"""
        vehicle = vehicle_factory()
        service_date = date.today()
        service_mileage = 15000.0

        result = service.record_service(
            db_session,
            vehicle.id,
            service_date,
            service_mileage
        )

        assert result is not None
        assert result.last_service_date == service_date
        assert result.last_service_mileage == service_mileage

    # ==================== MILEAGE TESTS ====================

    def test_update_mileage_higher(self, service, db_session, vehicle_factory):
        """Test updating mileage with higher value"""
        vehicle = vehicle_factory(current_mileage=10000.0)

        result = service.update_mileage(db_session, vehicle.id, 15000.0)

        assert result is not None
        assert result.current_mileage == 15000.0

    def test_update_mileage_lower_rejected(self, service, db_session, vehicle_factory):
        """Test updating mileage with lower value is rejected"""
        vehicle = vehicle_factory(current_mileage=10000.0)

        result = service.update_mileage(db_session, vehicle.id, 8000.0)

        assert result is not None
        assert result.current_mileage == 10000.0  # Unchanged

    def test_update_mileage_same_rejected(self, service, db_session, vehicle_factory):
        """Test updating mileage with same value is rejected"""
        vehicle = vehicle_factory(current_mileage=10000.0)

        result = service.update_mileage(db_session, vehicle.id, 10000.0)

        assert result.current_mileage == 10000.0  # Unchanged

    # ==================== STATUS UPDATE TESTS ====================

    def test_update_status_to_maintenance(self, service, db_session, vehicle_factory):
        """Test updating vehicle status to maintenance"""
        vehicle = vehicle_factory(status=VehicleStatus.ACTIVE)

        result = service.update_status(db_session, vehicle.id, VehicleStatus.MAINTENANCE)

        assert result is not None
        assert result.status == VehicleStatus.MAINTENANCE

    def test_update_status_to_active(self, service, db_session, vehicle_factory):
        """Test updating vehicle status to active"""
        vehicle = vehicle_factory(status=VehicleStatus.MAINTENANCE)

        result = service.update_status(db_session, vehicle.id, VehicleStatus.ACTIVE)

        assert result is not None
        assert result.status == VehicleStatus.ACTIVE

    def test_update_status_to_retired(self, service, db_session, vehicle_factory):
        """Test updating vehicle status to retired"""
        vehicle = vehicle_factory(status=VehicleStatus.ACTIVE)

        result = service.update_status(db_session, vehicle.id, VehicleStatus.RETIRED)

        assert result is not None
        assert result.status == VehicleStatus.RETIRED

    # ==================== DOCUMENT EXPIRY TESTS ====================

    def test_get_expiring_documents_registration(self, service, db_session, vehicle_factory):
        """Test getting vehicles with expiring registration"""
        expiring = vehicle_factory(
            status=VehicleStatus.ACTIVE,
            registration_expiry_date=date.today() + timedelta(days=15)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        assert len(result) >= 1

    def test_get_expiring_documents_insurance(self, service, db_session, vehicle_factory):
        """Test getting vehicles with expiring insurance"""
        expiring = vehicle_factory(
            status=VehicleStatus.ACTIVE,
            insurance_expiry_date=date.today() + timedelta(days=20)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        assert len(result) >= 1

    def test_get_expiring_documents_already_expired(self, service, db_session, vehicle_factory):
        """Test getting vehicles with already expired documents"""
        expired = vehicle_factory(
            status=VehicleStatus.ACTIVE,
            registration_expiry_date=date.today() - timedelta(days=5)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        expired_docs = [doc for doc in result if doc.vehicle_id == expired.id]
        assert len(expired_docs) >= 1
        if expired_docs:
            assert expired_docs[0].any_expired is True

    def test_get_expiring_documents_maintenance_vehicles(self, service, db_session, vehicle_factory):
        """Test getting expiring documents includes maintenance vehicles"""
        maintenance_vehicle = vehicle_factory(
            status=VehicleStatus.MAINTENANCE,
            registration_expiry_date=date.today() + timedelta(days=10)
        )

        result = service.get_expiring_documents(db_session, days_threshold=30)

        vehicle_ids = [doc.vehicle_id for doc in result]
        assert maintenance_vehicle.id in vehicle_ids

    # ==================== STATISTICS TESTS ====================

    def test_get_statistics(self, service, db_session, vehicle_factory):
        """Test getting vehicle statistics"""
        vehicle_factory(status=VehicleStatus.ACTIVE, vehicle_type=VehicleType.MOTORCYCLE)
        vehicle_factory(status=VehicleStatus.ACTIVE, vehicle_type=VehicleType.CAR)
        vehicle_factory(status=VehicleStatus.MAINTENANCE, vehicle_type=VehicleType.MOTORCYCLE)

        stats = service.get_statistics(db_session)

        assert "total" in stats
        assert "status_breakdown" in stats
        assert "type_breakdown" in stats
        assert "assigned" in stats
        assert "available" in stats
        assert stats["total"] >= 3

    def test_get_statistics_by_organization(self, service, db_session, vehicle_factory, test_organization):
        """Test getting vehicle statistics filtered by organization"""
        vehicle_factory(status=VehicleStatus.ACTIVE, organization_id=test_organization.id)
        vehicle_factory(status=VehicleStatus.ACTIVE, organization_id=test_organization.id)

        stats = service.get_statistics(db_session, organization_id=test_organization.id)

        assert stats["total"] >= 2

    # ==================== SEARCH TESTS ====================

    def test_search_vehicles_by_plate(self, service, db_session, vehicle_factory):
        """Test searching vehicles by plate number"""
        vehicle = vehicle_factory(plate_number="SEARCH-123")

        result = service.search_vehicles(db_session, search_term="SEARCH-123")

        assert len(result) >= 1
        assert any(v.plate_number == "SEARCH-123" for v in result)

    def test_search_vehicles_by_make(self, service, db_session, vehicle_factory):
        """Test searching vehicles by make"""
        vehicle = vehicle_factory(make="Toyota")

        result = service.search_vehicles(db_session, search_term="Toyota")

        assert len(result) >= 1

    def test_search_vehicles_by_model(self, service, db_session, vehicle_factory):
        """Test searching vehicles by model"""
        vehicle = vehicle_factory(model="Camry XLE")

        result = service.search_vehicles(db_session, search_term="Camry")

        assert len(result) >= 1

    def test_search_vehicles_by_vin(self, service, db_session, vehicle_factory):
        """Test searching vehicles by VIN"""
        vehicle = vehicle_factory(vin_number="SEARCHABLEVIN1234")

        result = service.search_vehicles(db_session, search_term="SEARCHABLEVIN")

        assert len(result) >= 1

    def test_search_vehicles_no_results(self, service, db_session):
        """Test searching with no matching results"""
        result = service.search_vehicles(db_session, search_term="XYZNOMATCH999")

        assert len(result) == 0

    def test_search_vehicles_case_insensitive(self, service, db_session, vehicle_factory):
        """Test search is case insensitive"""
        vehicle = vehicle_factory(make="Mercedes")

        result_lower = service.search_vehicles(db_session, search_term="mercedes")
        result_upper = service.search_vehicles(db_session, search_term="MERCEDES")

        assert len(result_lower) >= 1
        assert len(result_upper) >= 1

    # ==================== PAGINATION TESTS ====================

    def test_get_active_vehicles_pagination(self, service, db_session, vehicle_factory):
        """Test pagination for active vehicles"""
        for _ in range(5):
            vehicle_factory(status=VehicleStatus.ACTIVE)

        first_page = service.get_active_vehicles(db_session, skip=0, limit=2)
        second_page = service.get_active_vehicles(db_session, skip=2, limit=2)

        assert len(first_page) == 2
        assert len(second_page) == 2
        first_ids = {v.id for v in first_page}
        second_ids = {v.id for v in second_page}
        assert first_ids.isdisjoint(second_ids)

    def test_search_vehicles_pagination(self, service, db_session, vehicle_factory):
        """Test pagination for search results"""
        for i in range(5):
            vehicle_factory(make="TestMake")

        first_page = service.search_vehicles(db_session, search_term="TestMake", skip=0, limit=2)
        second_page = service.search_vehicles(db_session, search_term="TestMake", skip=2, limit=2)

        assert len(first_page) <= 2
        assert len(second_page) <= 2

    # ==================== ORGANIZATION FILTER TESTS ====================

    def test_get_active_vehicles_by_organization(self, service, db_session, vehicle_factory, test_organization, second_organization):
        """Test getting active vehicles filtered by organization"""
        org1_vehicle = vehicle_factory(status=VehicleStatus.ACTIVE, organization_id=test_organization.id)
        org2_vehicle = vehicle_factory(status=VehicleStatus.ACTIVE, organization_id=second_organization.id)

        result = service.get_active_vehicles(db_session, organization_id=test_organization.id)

        assert all(v.organization_id == test_organization.id for v in result)

    def test_search_vehicles_by_organization(self, service, db_session, vehicle_factory, test_organization):
        """Test searching vehicles filtered by organization"""
        vehicle = vehicle_factory(make="OrgSpecific", organization_id=test_organization.id)

        result = service.search_vehicles(
            db_session,
            search_term="OrgSpecific",
            organization_id=test_organization.id
        )

        assert len(result) >= 1
        assert all(v.organization_id == test_organization.id for v in result)
