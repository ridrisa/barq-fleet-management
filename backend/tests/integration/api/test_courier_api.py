"""
Integration Tests for Courier API Endpoints

Tests cover:
- CRUD operations (Create, Read, Update, Delete)
- Authentication and authorization
- Pagination and filtering
- Error handling
- Data validation

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from tests.utils.test_helpers import APITestHelper, DataGenerator


class TestCourierAPI:
    """Integration tests for /api/v1/fleet/couriers endpoints"""

    BASE_URL = "/api/v1/fleet/couriers"

    def test_create_courier_success(self, client, admin_headers, sample_courier_data):
        """Test successful courier creation"""
        response = client.post(
            self.BASE_URL,
            json=sample_courier_data,
            headers=admin_headers
        )

        data = APITestHelper.assert_success_response(response, 201)
        assert "data" in data
        courier = data["data"]

        assert courier["barq_id"] == sample_courier_data["barq_id"]
        assert courier["full_name"] == sample_courier_data["full_name"]
        assert courier["email"] == sample_courier_data["email"]
        assert courier["status"] == sample_courier_data["status"]
        assert "id" in courier
        assert "created_at" in courier

    def test_create_courier_without_auth(self, client, sample_courier_data):
        """Test courier creation fails without authentication"""
        response = client.post(
            self.BASE_URL,
            json=sample_courier_data
        )

        APITestHelper.assert_error_response(response, 401)

    def test_create_courier_missing_required_fields(self, client, admin_headers):
        """Test courier creation with missing required fields"""
        incomplete_data = {
            "full_name": "Test Courier"
            # Missing barq_id and mobile_number
        }

        response = client.post(
            self.BASE_URL,
            json=incomplete_data,
            headers=admin_headers
        )

        APITestHelper.assert_error_response(response, 422)

    def test_create_courier_duplicate_barq_id(
        self,
        client,
        admin_headers,
        courier_factory
    ):
        """Test creating courier with duplicate barq_id fails"""
        existing_courier = courier_factory(barq_id="BRQ-DUPLICATE")

        duplicate_data = {
            "barq_id": "BRQ-DUPLICATE",
            "full_name": "Duplicate Courier",
            "mobile_number": "+966509999999",
            "email": "duplicate@test.com"
        }

        response = client.post(
            self.BASE_URL,
            json=duplicate_data,
            headers=admin_headers
        )

        APITestHelper.assert_error_response(response, 400)

    def test_get_courier_by_id(self, client, auth_headers, courier_factory):
        """Test retrieving courier by ID"""
        courier = courier_factory(
            full_name="Test Courier",
            email="test@example.com"
        )

        response = client.get(
            f"{self.BASE_URL}/{courier.id}",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        courier_data = data["data"]

        assert courier_data["id"] == courier.id
        assert courier_data["full_name"] == "Test Courier"
        assert courier_data["email"] == "test@example.com"

    def test_get_courier_not_found(self, client, auth_headers):
        """Test retrieving non-existent courier returns 404"""
        response = client.get(
            f"{self.BASE_URL}/99999",
            headers=auth_headers
        )

        APITestHelper.assert_error_response(response, 404)

    def test_list_couriers_with_pagination(self, client, auth_headers, courier_factory):
        """Test listing couriers with pagination"""
        # Create 15 couriers
        for i in range(15):
            courier_factory(full_name=f"Courier {i}")

        response = client.get(
            f"{self.BASE_URL}?page=1&page_size=10",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        APITestHelper.assert_pagination(data, expected_page=1, expected_page_size=10)

        assert len(data["items"]) == 10
        assert data["total"] >= 15

    def test_list_couriers_filter_by_status(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test filtering couriers by status"""
        from app.models.fleet.courier import CourierStatus

        # Create couriers with different statuses
        courier_factory(status=CourierStatus.ACTIVE, full_name="Active 1")
        courier_factory(status=CourierStatus.ACTIVE, full_name="Active 2")
        courier_factory(status=CourierStatus.INACTIVE, full_name="Inactive 1")

        response = client.get(
            f"{self.BASE_URL}?status=active",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        assert len(data["items"]) >= 2

        for courier in data["items"]:
            assert courier["status"] == "active"

    def test_list_couriers_filter_by_city(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test filtering couriers by city"""
        courier_factory(city="Riyadh", full_name="Riyadh Courier 1")
        courier_factory(city="Riyadh", full_name="Riyadh Courier 2")
        courier_factory(city="Jeddah", full_name="Jeddah Courier 1")

        response = client.get(
            f"{self.BASE_URL}?city=Riyadh",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        assert len(data["items"]) >= 2

        for courier in data["items"]:
            assert courier["city"] == "Riyadh"

    def test_list_couriers_search_by_name(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test searching couriers by name"""
        courier_factory(full_name="Ahmad Hassan")
        courier_factory(full_name="Mohammad Ali")
        courier_factory(full_name="Ahmed Salem")

        response = client.get(
            f"{self.BASE_URL}?search=Ahmad",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        assert len(data["items"]) >= 2

        for courier in data["items"]:
            assert "Ahmad" in courier["full_name"] or "Ahmed" in courier["full_name"]

    def test_update_courier_success(
        self,
        client,
        admin_headers,
        courier_factory
    ):
        """Test updating courier information"""
        courier = courier_factory(full_name="Original Name")

        update_data = {
            "full_name": "Updated Name",
            "email": "updated@example.com"
        }

        response = client.put(
            f"{self.BASE_URL}/{courier.id}",
            json=update_data,
            headers=admin_headers
        )

        data = APITestHelper.assert_success_response(response)
        updated_courier = data["data"]

        assert updated_courier["full_name"] == "Updated Name"
        assert updated_courier["email"] == "updated@example.com"

    def test_update_courier_status(
        self,
        client,
        admin_headers,
        courier_factory
    ):
        """Test updating courier status"""
        from app.models.fleet.courier import CourierStatus

        courier = courier_factory(status=CourierStatus.ACTIVE)

        update_data = {
            "status": "on_leave"
        }

        response = client.put(
            f"{self.BASE_URL}/{courier.id}",
            json=update_data,
            headers=admin_headers
        )

        data = APITestHelper.assert_success_response(response)
        assert data["data"]["status"] == "on_leave"

    def test_update_courier_non_admin_forbidden(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test that non-admin users cannot update courier"""
        courier = courier_factory()

        update_data = {"full_name": "Hacked Name"}

        response = client.put(
            f"{self.BASE_URL}/{courier.id}",
            json=update_data,
            headers=auth_headers
        )

        # Should return 403 Forbidden or 401
        assert response.status_code in [401, 403]

    def test_delete_courier_success(self, client, admin_headers, courier_factory):
        """Test deleting courier"""
        courier = courier_factory()

        response = client.delete(
            f"{self.BASE_URL}/{courier.id}",
            headers=admin_headers
        )

        data = APITestHelper.assert_success_response(response, 200)

        # Verify courier is deleted
        get_response = client.get(
            f"{self.BASE_URL}/{courier.id}",
            headers=admin_headers
        )
        assert get_response.status_code == 404

    def test_delete_courier_non_admin_forbidden(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test that non-admin users cannot delete courier"""
        courier = courier_factory()

        response = client.delete(
            f"{self.BASE_URL}/{courier.id}",
            headers=auth_headers
        )

        assert response.status_code in [401, 403]

    def test_get_courier_performance(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test retrieving courier performance metrics"""
        courier = courier_factory()

        response = client.get(
            f"{self.BASE_URL}/{courier.id}/performance",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        performance = data["data"]

        assert "total_deliveries" in performance
        assert "delivery_rate" in performance
        assert "rating" in performance

    def test_get_courier_documents(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test retrieving courier documents status"""
        from datetime import date, timedelta

        courier = courier_factory(
            iqama_expiry_date=date.today() + timedelta(days=30),
            passport_expiry_date=date.today() + timedelta(days=60),
            license_expiry_date=date.today() + timedelta(days=90)
        )

        response = client.get(
            f"{self.BASE_URL}/{courier.id}/documents",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        documents = data["data"]

        assert "iqama" in documents
        assert "passport" in documents
        assert "license" in documents
        assert documents["iqama"]["expired"] is False

    def test_courier_assignment_history(
        self,
        client,
        auth_headers,
        courier_factory
    ):
        """Test retrieving courier vehicle assignment history"""
        courier = courier_factory()

        response = client.get(
            f"{self.BASE_URL}/{courier.id}/assignments",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_bulk_update_courier_status(
        self,
        client,
        admin_headers,
        courier_factory
    ):
        """Test bulk updating courier statuses"""
        couriers = [courier_factory() for _ in range(3)]
        courier_ids = [c.id for c in couriers]

        bulk_data = {
            "courier_ids": courier_ids,
            "status": "inactive"
        }

        response = client.post(
            f"{self.BASE_URL}/bulk-update-status",
            json=bulk_data,
            headers=admin_headers
        )

        data = APITestHelper.assert_success_response(response)
        assert data["data"]["updated_count"] == 3

    def test_export_couriers_csv(self, client, admin_headers, courier_factory):
        """Test exporting couriers to CSV"""
        for i in range(5):
            courier_factory(full_name=f"Export Courier {i}")

        response = client.get(
            f"{self.BASE_URL}/export?format=csv",
            headers=admin_headers
        )

        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/csv"
        assert len(response.content) > 0

    def test_courier_validation_invalid_phone(
        self,
        client,
        admin_headers,
        sample_courier_data
    ):
        """Test courier creation with invalid phone number"""
        sample_courier_data["mobile_number"] = "invalid-phone"

        response = client.post(
            self.BASE_URL,
            json=sample_courier_data,
            headers=admin_headers
        )

        APITestHelper.assert_error_response(response, 422)

    def test_courier_validation_invalid_email(
        self,
        client,
        admin_headers,
        sample_courier_data
    ):
        """Test courier creation with invalid email"""
        sample_courier_data["email"] = "not-an-email"

        response = client.post(
            self.BASE_URL,
            json=sample_courier_data,
            headers=admin_headers
        )

        APITestHelper.assert_error_response(response, 422)

    def test_courier_stats_endpoint(self, client, auth_headers, courier_factory):
        """Test courier statistics endpoint"""
        from app.models.fleet.courier import CourierStatus

        courier_factory(status=CourierStatus.ACTIVE)
        courier_factory(status=CourierStatus.ACTIVE)
        courier_factory(status=CourierStatus.INACTIVE)

        response = client.get(
            f"{self.BASE_URL}/stats",
            headers=auth_headers
        )

        data = APITestHelper.assert_success_response(response)
        stats = data["data"]

        assert "total_couriers" in stats
        assert "active_couriers" in stats
        assert "inactive_couriers" in stats
        assert stats["active_couriers"] >= 2
        assert stats["inactive_couriers"] >= 1
