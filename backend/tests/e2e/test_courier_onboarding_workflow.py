"""
E2E Tests for Courier Onboarding Workflow

Tests the complete courier onboarding process from creation to activation.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta, date

from app.models.fleet.courier import CourierStatus
from app.models.fleet.vehicle import VehicleStatus
from tests.utils.factories import AdminUserFactory, VehicleFactory
from tests.utils.api_helpers import (
    make_get_request,
    make_post_request,
    make_put_request,
    make_patch_request,
    assert_success_response,
    create_test_token
)


@pytest.mark.e2e
@pytest.mark.fleet
class TestCourierOnboardingWorkflow:
    """Test complete courier onboarding workflow"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session, client):
        """Setup test data"""
        self.db = db_session
        self.client = client

        # Create admin user
        self.admin_user = AdminUserFactory.create()
        self.admin_token = create_test_token(
            self.admin_user.id,
            self.admin_user.email,
            "admin"
        )

        self.db.commit()

    def test_complete_courier_onboarding_workflow(self):
        """
        Test complete courier onboarding workflow:
        1. Create courier profile
        2. Upload documents
        3. Assign vehicle
        4. Create salary record
        5. Activate courier
        """

        # Step 1: Create courier profile
        courier_data = {
            "barq_id": "BRQ-E2E-001",
            "full_name": "Ahmad Hassan Al-Rashid",
            "email": "ahmad.hassan@e2etest.com",
            "mobile_number": "+966501234567",
            "employee_id": "EMP-E2E-001",
            "status": "onboarding",
            "sponsorship_status": "inhouse",
            "project_type": "barq",
            "city": "Riyadh",
            "nationality": "Saudi Arabia",
            "position": "Courier",
            "date_of_birth": "1990-05-15",
            "national_id": "1234567890"
        }

        create_response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert create_response.status_code == 201
        courier = create_response.json()
        courier_id = courier["id"]

        assert courier["status"] == "onboarding"
        assert courier["barq_id"] == "BRQ-E2E-001"

        # Step 2: Upload courier documents
        document_data = {
            "courier_id": courier_id,
            "document_type": "national_id",
            "document_number": "1234567890",
            "issue_date": "2020-01-01",
            "expiry_date": "2030-01-01"
        }

        doc_response = make_post_request(
            self.client,
            "/api/v1/fleet/documents",
            document_data,
            self.admin_token
        )

        assert doc_response.status_code == 201

        # Upload license document
        license_data = {
            "courier_id": courier_id,
            "document_type": "driving_license",
            "document_number": "LIC-123456",
            "issue_date": "2021-01-01",
            "expiry_date": "2026-01-01"
        }

        license_response = make_post_request(
            self.client,
            "/api/v1/fleet/documents",
            license_data,
            self.admin_token
        )

        assert license_response.status_code == 201

        # Step 3: Assign vehicle to courier
        vehicle = VehicleFactory.create(status=VehicleStatus.AVAILABLE)
        self.db.commit()

        assignment_data = {
            "courier_id": courier_id,
            "vehicle_id": vehicle.id,
            "start_date": date.today().isoformat(),
            "notes": "Initial vehicle assignment"
        }

        assignment_response = make_post_request(
            self.client,
            "/api/v1/fleet/assignments",
            assignment_data,
            self.admin_token
        )

        assert assignment_response.status_code == 201
        assignment = assignment_response.json()

        assert assignment["courier_id"] == courier_id
        assert assignment["vehicle_id"] == vehicle.id

        # Step 4: Create salary record for courier
        salary_data = {
            "courier_id": courier_id,
            "basic_salary": 3000.00,
            "housing_allowance": 500.00,
            "transportation_allowance": 300.00,
            "food_allowance": 200.00,
            "month": datetime.now().month,
            "year": datetime.now().year
        }

        salary_response = make_post_request(
            self.client,
            "/api/v1/hr/salaries",
            salary_data,
            self.admin_token
        )

        assert salary_response.status_code == 201

        # Step 5: Complete onboarding and activate courier
        activation_data = {
            "status": "active",
            "joining_date": date.today().isoformat()
        }

        activation_response = make_put_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier_id}",
            activation_data,
            self.admin_token
        )

        assert_success_response(activation_response)
        activated_courier = activation_response.json()

        assert activated_courier["status"] == "active"
        assert activated_courier["joining_date"] is not None

        # Verify complete courier profile
        profile_response = make_get_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier_id}",
            self.admin_token
        )

        assert_success_response(profile_response)
        profile = profile_response.json()

        assert profile["status"] == "active"
        assert profile["barq_id"] == "BRQ-E2E-001"
        assert profile["full_name"] == "Ahmad Hassan Al-Rashid"

        # Verify courier has vehicle assigned
        assert profile.get("current_vehicle_id") == vehicle.id

        # Verify courier appears in active couriers list
        active_list_response = make_get_request(
            self.client,
            "/api/v1/fleet/couriers",
            self.admin_token,
            params={"status": "active"}
        )

        assert_success_response(active_list_response)
        active_couriers = active_list_response.json().get("items", [])

        courier_ids = [c["id"] for c in active_couriers]
        assert courier_id in courier_ids

    def test_courier_onboarding_with_validation_errors(self):
        """
        Test courier onboarding workflow with validation errors
        """

        # Try to create courier with missing required fields
        incomplete_data = {
            "barq_id": "BRQ-E2E-002",
            "full_name": "Test Courier"
            # Missing email, mobile, etc.
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            incomplete_data,
            self.admin_token
        )

        assert response.status_code == 422  # Validation error

    def test_courier_onboarding_with_duplicate_barq_id(self):
        """
        Test courier onboarding with duplicate BARQ ID
        """

        # Create first courier
        courier_data = {
            "barq_id": "BRQ-DUP-001",
            "full_name": "First Courier",
            "email": "first@test.com",
            "mobile_number": "+966501111111",
            "employee_id": "EMP-FIRST"
        }

        first_response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert first_response.status_code == 201

        # Try to create second courier with same BARQ ID
        duplicate_data = {
            "barq_id": "BRQ-DUP-001",  # Same BARQ ID
            "full_name": "Second Courier",
            "email": "second@test.com",
            "mobile_number": "+966502222222",
            "employee_id": "EMP-SECOND"
        }

        duplicate_response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            duplicate_data,
            self.admin_token
        )

        assert duplicate_response.status_code in [400, 409]  # Conflict error

    def test_cannot_assign_vehicle_to_onboarding_courier(self):
        """
        Test that certain operations are restricted for onboarding couriers
        """

        # Create courier in onboarding status
        courier_data = {
            "barq_id": "BRQ-E2E-003",
            "full_name": "Onboarding Courier",
            "email": "onboarding@test.com",
            "mobile_number": "+966503333333",
            "employee_id": "EMP-003",
            "status": "onboarding"
        }

        courier_response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert courier_response.status_code == 201
        courier_id = courier_response.json()["id"]

        # Verify courier is created but in onboarding status
        get_response = make_get_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier_id}",
            self.admin_token
        )

        courier = get_response.json()
        assert courier["status"] == "onboarding"

    def test_bulk_courier_onboarding(self):
        """
        Test onboarding multiple couriers at once
        """

        couriers_data = {
            "couriers": [
                {
                    "barq_id": "BRQ-BULK-001",
                    "full_name": "Bulk Courier 1",
                    "email": "bulk1@test.com",
                    "mobile_number": "+966504444444",
                    "employee_id": "EMP-BULK-001"
                },
                {
                    "barq_id": "BRQ-BULK-002",
                    "full_name": "Bulk Courier 2",
                    "email": "bulk2@test.com",
                    "mobile_number": "+966505555555",
                    "employee_id": "EMP-BULK-002"
                }
            ]
        }

        response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers/bulk-create",
            couriers_data,
            self.admin_token
        )

        if response.status_code == 201:
            result = response.json()
            assert len(result.get("created", [])) == 2

    def test_courier_profile_completeness_check(self):
        """
        Test checking courier profile completeness during onboarding
        """

        # Create courier with minimal information
        courier_data = {
            "barq_id": "BRQ-E2E-004",
            "full_name": "Incomplete Courier",
            "email": "incomplete@test.com",
            "mobile_number": "+966506666666",
            "employee_id": "EMP-004"
        }

        courier_response = make_post_request(
            self.client,
            "/api/v1/fleet/couriers",
            courier_data,
            self.admin_token
        )

        assert courier_response.status_code == 201
        courier_id = courier_response.json()["id"]

        # Check profile completeness
        completeness_response = make_get_request(
            self.client,
            f"/api/v1/fleet/couriers/{courier_id}/profile-completeness",
            self.admin_token
        )

        if completeness_response.status_code == 200:
            completeness = completeness_response.json()
            assert "completion_percentage" in completeness
            assert completeness["completion_percentage"] < 100
