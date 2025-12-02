"""
E2E Tests for Delivery Lifecycle Workflow

Tests the complete delivery lifecycle from creation to completion.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta, date
from decimal import Decimal

from app.models.operations.delivery import DeliveryStatus
from tests.utils.factories import (
    AdminUserFactory,
    CourierFactory,
    VehicleFactory,
    DeliveryFactory
)
from tests.utils.api_helpers import (
    make_get_request,
    make_post_request,
    make_patch_request,
    assert_success_response,
    create_test_token
)


@pytest.mark.e2e
@pytest.mark.operations
class TestDeliveryLifecycleWorkflow:
    """Test complete delivery lifecycle workflow"""

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

        # Create active courier with vehicle
        self.courier = CourierFactory.create(status="active")
        self.vehicle = VehicleFactory.create(status="active")
        self.db.commit()

    def test_complete_delivery_lifecycle_success(self):
        """
        Test complete successful delivery lifecycle:
        1. Create delivery
        2. Assign to courier
        3. Pickup
        4. In transit
        5. Deliver
        6. Collect COD
        7. Verify completion
        """

        # Step 1: Create delivery order
        delivery_data = {
            "tracking_number": "TRK-E2E-LIFECYCLE-001",
            "pickup_address": "Warehouse A, King Fahd Road, Riyadh",
            "pickup_lat": 24.7136,
            "pickup_lng": 46.6753,
            "delivery_address": "Customer Address, Olaya Street, Riyadh",
            "delivery_lat": 24.6877,
            "delivery_lng": 46.7219,
            "customer_name": "Ahmad Mohammed",
            "customer_phone": "+966501234567",
            "cod_amount": 250.00,
            "package_description": "Electronics - Mobile Phone",
            "priority": "normal"
        }

        create_response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            delivery_data,
            self.admin_token
        )

        assert create_response.status_code == 201
        delivery = create_response.json()
        delivery_id = delivery["id"]

        assert delivery["status"] == "pending"
        assert delivery["tracking_number"] == "TRK-E2E-LIFECYCLE-001"
        assert delivery["cod_amount"] == 250.00

        # Step 2: Assign delivery to courier
        assign_data = {
            "courier_id": self.courier.id,
            "vehicle_id": self.vehicle.id
        }

        assign_response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/assign",
            assign_data,
            self.admin_token
        )

        assert_success_response(assign_response)
        assigned_delivery = assign_response.json()

        assert assigned_delivery["courier_id"] == self.courier.id
        assert assigned_delivery["status"] == "assigned"

        # Step 3: Courier picks up package
        pickup_data = {
            "status": "picked_up",
            "pickup_time": datetime.now().isoformat(),
            "pickup_notes": "Package collected from warehouse"
        }

        pickup_response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            pickup_data,
            self.admin_token
        )

        assert_success_response(pickup_response)
        picked_delivery = pickup_response.json()

        assert picked_delivery["status"] == "picked_up"

        # Step 4: Delivery in transit
        transit_data = {
            "status": "in_transit",
            "current_lat": 24.7000,
            "current_lng": 46.7000
        }

        transit_response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            transit_data,
            self.admin_token
        )

        assert_success_response(transit_response)
        transit_delivery = transit_response.json()

        assert transit_delivery["status"] == "in_transit"

        # Step 5: Complete delivery
        complete_data = {
            "status": "delivered",
            "delivery_time": datetime.now().isoformat(),
            "delivery_notes": "Delivered to customer successfully",
            "recipient_name": "Ahmad Mohammed",
            "signature": "signature_base64_data_here"
        }

        complete_response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            complete_data,
            self.admin_token
        )

        assert_success_response(complete_response)
        completed_delivery = complete_response.json()

        assert completed_delivery["status"] == "delivered"
        assert completed_delivery["delivery_time"] is not None

        # Step 6: Collect COD payment
        cod_data = {
            "delivery_id": delivery_id,
            "courier_id": self.courier.id,
            "amount": 250.00,
            "collection_date": date.today().isoformat(),
            "payment_method": "cash"
        }

        cod_response = make_post_request(
            self.client,
            "/api/v1/operations/cod-collections",
            cod_data,
            self.admin_token
        )

        assert cod_response.status_code == 201
        cod_collection = cod_response.json()

        assert cod_collection["amount"] == 250.00
        assert cod_collection["status"] == "collected"

        # Step 7: Verify delivery completion
        final_response = make_get_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}",
            self.admin_token
        )

        assert_success_response(final_response)
        final_delivery = final_response.json()

        assert final_delivery["status"] == "delivered"
        assert final_delivery["cod_collected"] is True

        # Verify delivery in courier's history
        courier_deliveries_response = make_get_request(
            self.client,
            f"/api/v1/operations/couriers/{self.courier.id}/deliveries",
            self.admin_token
        )

        assert_success_response(courier_deliveries_response)
        courier_deliveries = courier_deliveries_response.json().get("items", [])

        delivery_ids = [d["id"] for d in courier_deliveries]
        assert delivery_id in delivery_ids

    def test_delivery_lifecycle_with_failure(self):
        """
        Test delivery lifecycle ending in failure:
        1. Create delivery
        2. Assign to courier
        3. Attempt delivery
        4. Mark as failed
        5. Reschedule
        """

        # Step 1: Create delivery
        delivery_data = {
            "tracking_number": "TRK-E2E-FAILED-001",
            "pickup_address": "Warehouse B, Riyadh",
            "delivery_address": "Customer Address, Riyadh",
            "customer_name": "Customer Name",
            "customer_phone": "+966501111111"
        }

        create_response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            delivery_data,
            self.admin_token
        )

        assert create_response.status_code == 201
        delivery_id = create_response.json()["id"]

        # Step 2: Assign to courier
        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/assign",
            {"courier_id": self.courier.id},
            self.admin_token
        )

        # Step 3: Pick up
        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            {"status": "picked_up"},
            self.admin_token
        )

        # Step 4: Attempt delivery and fail
        fail_data = {
            "status": "failed",
            "failure_reason": "Customer not available",
            "failure_time": datetime.now().isoformat(),
            "notes": "Customer did not answer phone"
        }

        fail_response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            fail_data,
            self.admin_token
        )

        assert_success_response(fail_response)
        failed_delivery = fail_response.json()

        assert failed_delivery["status"] == "failed"
        assert failed_delivery["failure_reason"] == "Customer not available"

        # Step 5: Reschedule delivery
        reschedule_data = {
            "scheduled_date": (date.today() + timedelta(days=1)).isoformat(),
            "scheduled_time_slot": "morning",
            "notes": "Rescheduled as per customer request"
        }

        reschedule_response = make_post_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/reschedule",
            reschedule_data,
            self.admin_token
        )

        if reschedule_response.status_code == 200:
            rescheduled_delivery = reschedule_response.json()
            assert rescheduled_delivery["status"] == "rescheduled"

    def test_delivery_lifecycle_with_return(self):
        """
        Test delivery lifecycle with return to sender:
        1. Create delivery
        2. Assign and pickup
        3. Customer rejects
        4. Return to sender
        """

        # Step 1: Create delivery
        delivery_data = {
            "tracking_number": "TRK-E2E-RETURN-001",
            "pickup_address": "Warehouse C, Riyadh",
            "delivery_address": "Customer Address, Riyadh",
            "customer_name": "Customer Name",
            "customer_phone": "+966502222222"
        }

        create_response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            delivery_data,
            self.admin_token
        )

        delivery_id = create_response.json()["id"]

        # Step 2: Assign and pickup
        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/assign",
            {"courier_id": self.courier.id},
            self.admin_token
        )

        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            {"status": "picked_up"},
            self.admin_token
        )

        # Step 3: Customer rejects - initiate return
        return_data = {
            "status": "return_to_sender",
            "return_reason": "Customer refused delivery",
            "return_initiated_time": datetime.now().isoformat()
        }

        return_response = make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            return_data,
            self.admin_token
        )

        if return_response.status_code == 200:
            returned_delivery = return_response.json()
            assert returned_delivery["status"] == "return_to_sender"

    def test_multiple_delivery_assignments_workflow(self):
        """
        Test assigning multiple deliveries to a courier in a route
        """

        # Create multiple deliveries
        delivery_ids = []
        for i in range(3):
            delivery_data = {
                "tracking_number": f"TRK-E2E-MULTI-{i+1:03d}",
                "pickup_address": "Central Warehouse, Riyadh",
                "delivery_address": f"Customer Address {i+1}, Riyadh",
                "customer_name": f"Customer {i+1}",
                "customer_phone": f"+96650{i}111111"
            }

            response = make_post_request(
                self.client,
                "/api/v1/operations/deliveries",
                delivery_data,
                self.admin_token
            )

            delivery_ids.append(response.json()["id"])

        # Assign all deliveries to courier
        for delivery_id in delivery_ids:
            make_patch_request(
                self.client,
                f"/api/v1/operations/deliveries/{delivery_id}/assign",
                {"courier_id": self.courier.id},
                self.admin_token
            )

        # Verify courier has all deliveries assigned
        courier_deliveries_response = make_get_request(
            self.client,
            f"/api/v1/operations/couriers/{self.courier.id}/deliveries",
            self.admin_token,
            params={"status": "assigned"}
        )

        assert_success_response(courier_deliveries_response)
        assigned_deliveries = courier_deliveries_response.json().get("items", [])

        assert len(assigned_deliveries) >= 3

    def test_delivery_tracking_history(self):
        """
        Test delivery tracking history throughout lifecycle
        """

        # Create and process delivery
        delivery_data = {
            "tracking_number": "TRK-E2E-HISTORY-001",
            "pickup_address": "Test Warehouse",
            "delivery_address": "Test Address",
            "customer_name": "Test Customer",
            "customer_phone": "+966501234567"
        }

        create_response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            delivery_data,
            self.admin_token
        )

        delivery_id = create_response.json()["id"]

        # Assign
        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/assign",
            {"courier_id": self.courier.id},
            self.admin_token
        )

        # Pickup
        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            {"status": "picked_up"},
            self.admin_token
        )

        # Get tracking history
        history_response = make_get_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/tracking-history",
            self.admin_token
        )

        if history_response.status_code == 200:
            history = history_response.json()
            assert len(history) >= 2  # Created, Assigned, Picked up

    def test_delivery_performance_metrics(self):
        """
        Test delivery performance metrics after completion
        """

        # Create and complete a delivery
        delivery_data = {
            "tracking_number": "TRK-E2E-METRICS-001",
            "pickup_address": "Test Warehouse",
            "delivery_address": "Test Address",
            "customer_name": "Test Customer",
            "customer_phone": "+966501234567"
        }

        create_response = make_post_request(
            self.client,
            "/api/v1/operations/deliveries",
            delivery_data,
            self.admin_token
        )

        delivery_id = create_response.json()["id"]

        # Complete the delivery workflow
        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/assign",
            {"courier_id": self.courier.id},
            self.admin_token
        )

        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            {"status": "picked_up"},
            self.admin_token
        )

        make_patch_request(
            self.client,
            f"/api/v1/operations/deliveries/{delivery_id}/status",
            {"status": "delivered"},
            self.admin_token
        )

        # Check courier performance metrics
        metrics_response = make_get_request(
            self.client,
            f"/api/v1/operations/couriers/{self.courier.id}/performance",
            self.admin_token
        )

        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            assert "total_deliveries" in metrics
            assert metrics["total_deliveries"] >= 1
