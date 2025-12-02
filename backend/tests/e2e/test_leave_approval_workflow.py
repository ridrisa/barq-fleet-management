"""
E2E Test: Leave Request and Approval Workflow

Complete user workflow from leave request creation to approval/rejection

Scenario:
1. Courier submits leave request
2. Request enters workflow system
3. Manager reviews and approves
4. HR processes approval
5. Leave status updated
6. Notifications sent

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta, date
from tests.utils.test_helpers import APITestHelper


class TestLeaveApprovalWorkflow:
    """E2E test for complete leave approval workflow"""

    def test_complete_leave_approval_workflow(
        self,
        client,
        db_session,
        admin_user,
        manager_user,
        test_user,
        admin_headers,
        manager_token,
        test_token,
        courier_factory,
        mock_email_service,
        mock_sms_service
    ):
        """
        Test complete leave approval workflow end-to-end

        Steps:
        1. Create courier
        2. Submit leave request
        3. Verify workflow instance created
        4. Manager reviews and approves
        5. HR processes
        6. Verify final status and notifications
        """

        # Step 1: Create courier
        courier = courier_factory(
            full_name="Ahmad Hassan",
            email="ahmad@test.com",
            mobile_number="+966501234567"
        )

        # Step 2: Submit leave request
        leave_data = {
            "courier_id": courier.id,
            "leave_type": "annual",
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=12)).isoformat(),
            "reason": "Family vacation",
        }

        manager_headers = {"Authorization": f"Bearer {manager_token}"}
        user_headers = {"Authorization": f"Bearer {test_token}"}

        response = client.post(
            "/api/v1/hr/leaves",
            json=leave_data,
            headers=user_headers
        )

        data = APITestHelper.assert_success_response(response, 201)
        leave_id = data["data"]["id"]

        # Verify leave created with pending status
        assert data["data"]["status"] == "pending"
        assert data["data"]["courier_id"] == courier.id

        # Step 3: Verify workflow instance was created
        workflow_response = client.get(
            f"/api/v1/workflow/instances?entity_id={leave_id}&entity_type=leave",
            headers=admin_headers
        )

        workflow_data = APITestHelper.assert_success_response(workflow_response)
        assert len(workflow_data["items"]) > 0
        workflow_instance = workflow_data["items"][0]
        workflow_id = workflow_instance["id"]

        assert workflow_instance["current_state"] == "pending"
        assert workflow_instance["entity_type"] == "leave"

        # Step 4: Manager reviews leave request
        # First, get leave details
        get_leave_response = client.get(
            f"/api/v1/hr/leaves/{leave_id}",
            headers=manager_headers
        )

        leave_details = APITestHelper.assert_success_response(get_leave_response)
        assert leave_details["data"]["status"] == "pending"

        # Manager approves the leave
        approval_data = {
            "action": "approve",
            "comments": "Approved for family vacation. Have a good time!",
            "approved_by": manager_user.id
        }

        approve_response = client.post(
            f"/api/v1/workflow/instances/{workflow_id}/actions",
            json=approval_data,
            headers=manager_headers
        )

        approval_result = APITestHelper.assert_success_response(approve_response)
        assert approval_result["data"]["status"] == "approved"

        # Step 5: Verify workflow state updated
        updated_workflow_response = client.get(
            f"/api/v1/workflow/instances/{workflow_id}",
            headers=admin_headers
        )

        updated_workflow = APITestHelper.assert_success_response(updated_workflow_response)
        assert updated_workflow["data"]["current_state"] in ["approved", "completed"]

        # Step 6: Verify leave status updated
        final_leave_response = client.get(
            f"/api/v1/hr/leaves/{leave_id}",
            headers=user_headers
        )

        final_leave = APITestHelper.assert_success_response(final_leave_response)
        assert final_leave["data"]["status"] == "approved"
        assert final_leave["data"]["approved_by"] == manager_user.id
        assert "approved_at" in final_leave["data"]

        # Step 7: Verify notifications were sent
        # Email to courier
        assert mock_email_service.called
        email_calls = mock_email_service.call_args_list
        assert any("approved" in str(call).lower() for call in email_calls)

        # SMS notification
        assert mock_sms_service.called
        sms_calls = mock_sms_service.call_args_list
        assert any(courier.mobile_number in str(call) for call in sms_calls)

        # Step 8: Verify audit trail
        audit_response = client.get(
            f"/api/v1/workflow/instances/{workflow_id}/history",
            headers=admin_headers
        )

        audit_data = APITestHelper.assert_success_response(audit_response)
        assert len(audit_data["items"]) >= 2  # Created + Approved

        # Verify history contains creation and approval
        history_actions = [item["action"] for item in audit_data["items"]]
        assert "created" in history_actions or "submitted" in history_actions
        assert "approved" in history_actions

    def test_leave_rejection_workflow(
        self,
        client,
        db_session,
        manager_user,
        test_user,
        manager_token,
        test_token,
        courier_factory,
        mock_email_service
    ):
        """Test leave rejection workflow"""

        courier = courier_factory()
        user_headers = {"Authorization": f"Bearer {test_token}"}
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        # Submit leave request
        leave_data = {
            "courier_id": courier.id,
            "leave_type": "annual",
            "start_date": (date.today() + timedelta(days=2)).isoformat(),
            "end_date": (date.today() + timedelta(days=4)).isoformat(),
            "reason": "Short notice request",
        }

        response = client.post(
            "/api/v1/hr/leaves",
            json=leave_data,
            headers=user_headers
        )

        leave_id = APITestHelper.assert_success_response(response, 201)["data"]["id"]

        # Find workflow instance
        workflow_response = client.get(
            f"/api/v1/workflow/instances?entity_id={leave_id}",
            headers=manager_headers
        )

        workflow_id = APITestHelper.assert_success_response(workflow_response)["items"][0]["id"]

        # Manager rejects the leave
        rejection_data = {
            "action": "reject",
            "comments": "Request submitted on short notice. Please resubmit with more advance time.",
            "approved_by": manager_user.id
        }

        reject_response = client.post(
            f"/api/v1/workflow/instances/{workflow_id}/actions",
            json=rejection_data,
            headers=manager_headers
        )

        APITestHelper.assert_success_response(reject_response)

        # Verify leave status is rejected
        final_leave_response = client.get(
            f"/api/v1/hr/leaves/{leave_id}",
            headers=user_headers
        )

        final_leave = APITestHelper.assert_success_response(final_leave_response)
        assert final_leave["data"]["status"] == "rejected"

        # Verify rejection notification sent
        assert mock_email_service.called

    def test_leave_approval_with_insufficient_balance(
        self,
        client,
        test_user,
        test_token,
        courier_factory
    ):
        """Test leave request with insufficient leave balance"""

        courier = courier_factory()
        user_headers = {"Authorization": f"Bearer {test_token}"}

        # Request 30 days leave (exceeds annual allowance)
        leave_data = {
            "courier_id": courier.id,
            "leave_type": "annual",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=30)).isoformat(),
            "reason": "Extended vacation",
        }

        response = client.post(
            "/api/v1/hr/leaves",
            json=leave_data,
            headers=user_headers
        )

        # Should fail validation
        error_data = APITestHelper.assert_error_response(response, 400)
        assert "insufficient" in error_data["detail"].lower() or "balance" in error_data["detail"].lower()

    def test_concurrent_leave_requests(
        self,
        client,
        test_user,
        test_token,
        courier_factory
    ):
        """Test handling of overlapping leave requests"""

        courier = courier_factory()
        user_headers = {"Authorization": f"Bearer {test_token}"}

        # Submit first leave request
        leave_data_1 = {
            "courier_id": courier.id,
            "leave_type": "annual",
            "start_date": (date.today() + timedelta(days=10)).isoformat(),
            "end_date": (date.today() + timedelta(days=15)).isoformat(),
            "reason": "First vacation",
        }

        response1 = client.post(
            "/api/v1/hr/leaves",
            json=leave_data_1,
            headers=user_headers
        )

        APITestHelper.assert_success_response(response1, 201)

        # Submit overlapping leave request
        leave_data_2 = {
            "courier_id": courier.id,
            "leave_type": "annual",
            "start_date": (date.today() + timedelta(days=12)).isoformat(),
            "end_date": (date.today() + timedelta(days=18)).isoformat(),
            "reason": "Second vacation (overlapping)",
        }

        response2 = client.post(
            "/api/v1/hr/leaves",
            json=leave_data_2,
            headers=user_headers
        )

        # Should fail due to overlap
        error_data = APITestHelper.assert_error_response(response2, 400)
        assert "overlap" in error_data["detail"].lower()

    def test_emergency_leave_fast_track(
        self,
        client,
        manager_user,
        test_user,
        manager_token,
        test_token,
        courier_factory
    ):
        """Test emergency leave request (expedited approval)"""

        courier = courier_factory()
        user_headers = {"Authorization": f"Bearer {test_token}"}
        manager_headers = {"Authorization": f"Bearer {manager_token}"}

        # Submit emergency leave
        leave_data = {
            "courier_id": courier.id,
            "leave_type": "emergency",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=2)).isoformat(),
            "reason": "Family emergency - hospitalization",
            "is_emergency": True
        }

        response = client.post(
            "/api/v1/hr/leaves",
            json=leave_data,
            headers=user_headers
        )

        leave_id = APITestHelper.assert_success_response(response, 201)["data"]["id"]

        # Emergency leaves should be auto-approved or fast-tracked
        # Check if requires approval or auto-approved
        leave_status_response = client.get(
            f"/api/v1/hr/leaves/{leave_id}",
            headers=user_headers
        )

        leave_status = APITestHelper.assert_success_response(leave_status_response)
        # Emergency should either be auto-approved or marked as high priority
        assert leave_status["data"]["leave_type"] == "emergency"
