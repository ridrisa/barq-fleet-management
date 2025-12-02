"""
Integration Tests for Fleet Couriers API

Tests all courier management endpoints including CRUD operations,
filtering, searching, and courier-specific operations.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta, date

from app.models.fleet.courier import CourierStatus, SponsorshipStatus, ProjectType
from tests.utils.factories import CourierFactory, UserFactory, AdminUserFactory
from tests.utils.api_helpers import (
    make_get_request,
    make_post_request,
    make_put_request,
    make_delete_request,
    assert_success_response,
    assert_error_response,
    assert_unauthorized,
    assert_forbidden,
    assert_not_found,
    assert_validation_error,
    create_test_token
)


@pytest.mark.integration
@pytest.mark.fleet
class TestCouriersAPI:
    """Test Couriers API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session, client):
        """Setup test data"""
        self.db = db_session
        self.client = client

        # Create test users
        self.admin_user = AdminUserFactory.create()
        self.regular_user = UserFactory.create()

        # Create tokens
        self.admin_token = create_test_token(
            self.admin_user.id,
            self.admin_user.email,
            "admin"
        )
        self.user_token = create_test_token(
            self.regular_user.id,
            self.regular_user.email,
            "user"
        )

        self.db.commit()

    def test_list_couriers_success(self):
        """Test listing all couriers"""
        # Create test couriers
        CourierFactory.create(full_name="Ahmad Hassan")
        CourierFactory.create(full_name="Mohammed Ali")
        CourierFactory.create(full_name="Khalid Omar")
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert len(data.get("items", data)) >= 3

    def test_list_couriers_unauthorized(self):
        """Test listing couriers without authentication"""
        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers"
        )

        assert_unauthorized(response)

    def test_list_couriers_with_pagination(self):
        """Test courier listing with pagination"""
        # Create 25 couriers
        for i in range(25):
            CourierFactory.create()
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"page": 1, "page_size": 10}
        )

        assert_success_response(response)
        data = response.json()

        assert "items" in data
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1

    def test_list_couriers_filter_by_status(self):
        """Test filtering couriers by status"""
        CourierFactory.create(status=CourierStatus.ACTIVE)
        CourierFactory.create(status=CourierStatus.ACTIVE)
        CourierFactory.create(status=CourierStatus.INACTIVE)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"status": "active"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2
        assert all(item["status"] == "active" for item in items)

    def test_list_couriers_filter_by_city(self):
        """Test filtering couriers by city"""
        CourierFactory.create(city="Riyadh")
        CourierFactory.create(city="Riyadh")
        CourierFactory.create(city="Jeddah")
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"city": "Riyadh"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2
        assert all(item["city"] == "Riyadh" for item in items)

    def test_list_couriers_filter_by_project_type(self):
        """Test filtering couriers by project type"""
        CourierFactory.create(project_type=ProjectType.BARQ)
        CourierFactory.create(project_type=ProjectType.FOOD)
        CourierFactory.create(project_type=ProjectType.BARQ)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"project_type": "barq"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2

    def test_search_couriers_by_name(self):
        """Test searching couriers by name"""
        CourierFactory.create(full_name="Ahmad Hassan")
        CourierFactory.create(full_name="Mohammed Ahmad")
        CourierFactory.create(full_name="Khalid Omar")
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"search": "Ahmad"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2

    def test_search_couriers_by_email(self):
        """Test searching couriers by email"""
        CourierFactory.create(email="ahmad@test.com")
        CourierFactory.create(email="mohammed@test.com")
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"search": "ahmad@test.com"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 1
        assert items[0]["email"] == "ahmad@test.com"

    def test_create_courier_success(self):
        """Test creating a new courier"""
        courier_data = {
            "barq_id": "BRQ-TEST-001",
            "full_name": "Ahmad Hassan",
            "email": "ahmad.hassan@test.com",
            "mobile_number": "+966501234567",
            "employee_id": "EMP-001",
            "status": "active",
            "sponsorship_status": "inhouse",
            "project_type": "barq",
            "city": "Riyadh",
            "nationality": "Saudi Arabia"
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert response.status_code == 201
        data = response.json()

        assert data["barq_id"] == "BRQ-TEST-001"
        assert data["full_name"] == "Ahmad Hassan"
        assert data["email"] == "ahmad.hassan@test.com"
        assert data["status"] == "active"
        assert "id" in data

    def test_create_courier_duplicate_barq_id(self):
        """Test creating courier with duplicate barq_id"""
        CourierFactory.create(barq_id="BRQ-DUPLICATE")
        self.db.commit()

        courier_data = {
            "barq_id": "BRQ-DUPLICATE",
            "full_name": "Test Courier",
            "email": "test@test.com",
            "mobile_number": "+966501234567",
            "employee_id": "EMP-002",
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert response.status_code in [400, 409]

    def test_create_courier_duplicate_email(self):
        """Test creating courier with duplicate email"""
        CourierFactory.create(email="duplicate@test.com")
        self.db.commit()

        courier_data = {
            "barq_id": "BRQ-NEW-001",
            "full_name": "Test Courier",
            "email": "duplicate@test.com",
            "mobile_number": "+966501234567",
            "employee_id": "EMP-003",
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert response.status_code in [400, 409]

    def test_create_courier_missing_required_fields(self):
        """Test creating courier with missing required fields"""
        incomplete_data = {
            "full_name": "Test Courier"
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            incomplete_data,
            self.admin_token
        )

        assert_validation_error(response)

    def test_create_courier_invalid_email(self):
        """Test creating courier with invalid email"""
        courier_data = {
            "barq_id": "BRQ-TEST-002",
            "full_name": "Test Courier",
            "email": "invalid-email",
            "mobile_number": "+966501234567",
            "employee_id": "EMP-004",
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert_validation_error(response, "email")

    def test_get_courier_by_id_success(self):
        """Test retrieving a courier by ID"""
        courier = CourierFactory.create(
            full_name="Ahmad Hassan",
            email="ahmad@test.com"
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier.id}",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["id"] == courier.id
        assert data["full_name"] == "Ahmad Hassan"
        assert data["email"] == "ahmad@test.com"

    def test_get_courier_by_id_not_found(self):
        """Test retrieving non-existent courier"""
        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers/99999",
            self.admin_token
        )

        assert_not_found(response)

    def test_update_courier_success(self):
        """Test updating a courier"""
        courier = CourierFactory.create(
            full_name="Ahmad Hassan",
            status=CourierStatus.ACTIVE
        )
        self.db.commit()

        update_data = {
            "full_name": "Ahmad Hassan Updated",
            "status": "inactive"
        }

        response = make_put_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier.id}",
            update_data,
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["full_name"] == "Ahmad Hassan Updated"
        assert data["status"] == "inactive"

    def test_update_courier_not_found(self):
        """Test updating non-existent courier"""
        update_data = {"full_name": "Updated Name"}

        response = make_put_request(
            self.client,
            "/api/v1/fleet/couriers/99999",
            update_data,
            self.admin_token
        )

        assert_not_found(response)

    def test_update_courier_status(self):
        """Test updating courier status"""
        courier = CourierFactory.create(status=CourierStatus.ACTIVE)
        self.db.commit()

        response = make_put_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier.id}",
            {"status": "on_leave"},
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "on_leave"

    def test_delete_courier_success(self):
        """Test deleting a courier"""
        courier = CourierFactory.create()
        self.db.commit()
        courier_id = courier.id

        response = make_delete_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier_id}",
            self.admin_token
        )

        assert response.status_code in [200, 204]

        # Verify courier is deleted/soft-deleted
        get_response = make_get_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier_id}",
            self.admin_token
        )

        assert get_response.status_code == 404

    def test_delete_courier_not_found(self):
        """Test deleting non-existent courier"""
        response = make_delete_request(
            self.client,
            "/api/v1/fleet/couriers/99999",
            self.admin_token
        )

        assert_not_found(response)

    def test_get_courier_performance(self):
        """Test retrieving courier performance metrics"""
        courier = CourierFactory.create(
            performance_score=95.5,
            total_deliveries=150
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier.id}/performance",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert "performance_score" in data
        assert "total_deliveries" in data

    def test_list_couriers_by_sponsorship_status(self):
        """Test filtering couriers by sponsorship status"""
        CourierFactory.create(sponsorship_status=SponsorshipStatus.INHOUSE)
        CourierFactory.create(sponsorship_status=SponsorshipStatus.AJEER)
        CourierFactory.create(sponsorship_status=SponsorshipStatus.INHOUSE)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"sponsorship_status": "inhouse"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2

    def test_courier_document_expiry_alerts(self):
        """Test getting couriers with expiring documents"""
        # Courier with expiring iqama
        CourierFactory.create(
            iqama_expiry_date=date.today() + timedelta(days=15)
        )
        # Courier with expiring license
        CourierFactory.create(
            license_expiry_date=date.today() + timedelta(days=20)
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers/expiring-documents",
            self.admin_token,
            params={"days": 30}
        )

        assert_success_response(response)
        data = response.json()

        assert len(data) >= 2

    def test_bulk_update_courier_status(self):
        """Test bulk updating courier statuses"""
        courier1 = CourierFactory.create(status=CourierStatus.ACTIVE)
        courier2 = CourierFactory.create(status=CourierStatus.ACTIVE)
        self.db.commit()

        bulk_update_data = {
            "courier_ids": [courier1.id, courier2.id],
            "status": "inactive"
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers/bulk-update-status",
            bulk_update_data,
            self.admin_token
        )

        assert_success_response(response)

    def test_export_couriers_csv(self):
        """Test exporting couriers to CSV"""
        CourierFactory.create()
        CourierFactory.create()
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers/export",
            self.admin_token,
            params={"format": "csv"}
        )

        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")

    def test_courier_statistics(self):
        """Test getting courier statistics"""
        CourierFactory.create(status=CourierStatus.ACTIVE)
        CourierFactory.create(status=CourierStatus.ACTIVE)
        CourierFactory.create(status=CourierStatus.INACTIVE)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers/statistics",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert "total_couriers" in data
        assert "active_couriers" in data
        assert "inactive_couriers" in data
