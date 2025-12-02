"""
Integration Tests for HR Leave Management API

Tests leave request creation, approval workflow, and leave balance management.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from datetime import datetime, timedelta, date

from app.models.hr.leave import LeaveType, LeaveStatus
from tests.utils.factories import (
    CourierFactory,
    LeaveFactory,
    AdminUserFactory,
    ManagerUserFactory,
    UserFactory
)
from tests.utils.api_helpers import (
    make_get_request,
    make_post_request,
    make_put_request,
    make_delete_request,
    assert_success_response,
    assert_error_response,
    assert_unauthorized,
    assert_not_found,
    assert_validation_error,
    create_test_token
)


@pytest.mark.integration
@pytest.mark.hr
class TestLeaveAPI:
    """Test Leave Management API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session, client):
        """Setup test data"""
        self.db = db_session
        self.client = client

        # Create test users
        self.admin_user = AdminUserFactory.create()
        self.manager_user = ManagerUserFactory.create()
        self.regular_user = UserFactory.create()

        # Create test courier
        self.courier = CourierFactory.create()

        # Create tokens
        self.admin_token = create_test_token(
            self.admin_user.id,
            self.admin_user.email,
            "admin"
        )
        self.manager_token = create_test_token(
            self.manager_user.id,
            self.manager_user.email,
            "manager"
        )
        self.user_token = create_test_token(
            self.regular_user.id,
            self.regular_user.email,
            "user"
        )

        self.db.commit()

    def test_list_leave_requests(self):
        """Test listing all leave requests"""
        LeaveFactory.create(courier_id=self.courier.id)
        LeaveFactory.create(courier_id=self.courier.id)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/hr/leaves",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert len(data.get("items", data)) >= 2

    def test_list_leave_requests_filter_by_status(self):
        """Test filtering leave requests by status"""
        LeaveFactory.create(courier_id=self.courier.id, status=LeaveStatus.PENDING)
        LeaveFactory.create(courier_id=self.courier.id, status=LeaveStatus.APPROVED)
        LeaveFactory.create(courier_id=self.courier.id, status=LeaveStatus.PENDING)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/hr/leaves",
            self.admin_token,
            params={"status": "pending"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2
        assert all(item["status"] == "pending" for item in items)

    def test_list_leave_requests_filter_by_type(self):
        """Test filtering leave requests by type"""
        LeaveFactory.create(courier_id=self.courier.id, leave_type=LeaveType.ANNUAL)
        LeaveFactory.create(courier_id=self.courier.id, leave_type=LeaveType.SICK)
        LeaveFactory.create(courier_id=self.courier.id, leave_type=LeaveType.ANNUAL)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/hr/leaves",
            self.admin_token,
            params={"leave_type": "annual"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)

        assert len(items) == 2

    def test_create_leave_request_success(self):
        """Test creating a leave request"""
        leave_data = {
            "courier_id": self.courier.id,
            "leave_type": "annual",
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=12)).isoformat(),
            "reason": "Family vacation"
        }

        response = make_post_request(
            self.client,
            "/api/v1/hr/leaves",
            leave_data,
            self.admin_token
        )

        assert response.status_code == 201
        data = response.json()

        assert data["leave_type"] == "annual"
        assert data["status"] == "pending"
        assert "id" in data

    def test_create_leave_request_overlapping_dates(self):
        """Test creating leave with overlapping dates"""
        start_date = date.today() + timedelta(days=7)
        end_date = date.today() + timedelta(days=12)

        # Create existing leave
        LeaveFactory.create(
            courier_id=self.courier.id,
            start_date=start_date,
            end_date=end_date,
            status=LeaveStatus.APPROVED
        )
        self.db.commit()

        # Try to create overlapping leave
        leave_data = {
            "courier_id": self.courier.id,
            "leave_type": "annual",
            "start_date": (start_date + timedelta(days=2)).isoformat(),
            "end_date": (end_date + timedelta(days=2)).isoformat(),
            "reason": "Test"
        }

        response = make_post_request(
            self.client,
            "/api/v1/hr/leaves",
            leave_data,
            self.admin_token
        )

        assert response.status_code in [400, 409]

    def test_create_leave_request_invalid_date_range(self):
        """Test creating leave with end date before start date"""
        leave_data = {
            "courier_id": self.courier.id,
            "leave_type": "annual",
            "start_date": (date.today() + timedelta(days=12)).isoformat(),
            "end_date": (date.today() + timedelta(days=7)).isoformat(),
            "reason": "Test"
        }

        response = make_post_request(
            self.client,
            "/api/v1/hr/leaves",
            leave_data,
            self.admin_token
        )

        assert response.status_code in [400, 422]

    def test_create_leave_request_past_date(self):
        """Test creating leave with past dates"""
        leave_data = {
            "courier_id": self.courier.id,
            "leave_type": "annual",
            "start_date": (date.today() - timedelta(days=7)).isoformat(),
            "end_date": (date.today() - timedelta(days=2)).isoformat(),
            "reason": "Test"
        }

        response = make_post_request(
            self.client,
            "/api/v1/hr/leaves",
            leave_data,
            self.admin_token
        )

        assert response.status_code in [400, 422]

    def test_get_leave_by_id(self):
        """Test retrieving a leave request by ID"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            leave_type=LeaveType.ANNUAL
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/hr/leaves/{leave.id}",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["id"] == leave.id
        assert data["leave_type"] == "annual"

    def test_get_leave_not_found(self):
        """Test retrieving non-existent leave"""
        response = make_get_request(
            self.client,
            "/api/v1/hr/leaves/99999",
            self.admin_token
        )

        assert_not_found(response)

    def test_approve_leave_request(self):
        """Test approving a leave request"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            status=LeaveStatus.PENDING
        )
        self.db.commit()

        response = make_post_request(
            self.client,
            f"/api/v1/hr/leaves/{leave.id}/approve",
            {"notes": "Approved by manager"},
            self.manager_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "approved"

    def test_reject_leave_request(self):
        """Test rejecting a leave request"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            status=LeaveStatus.PENDING
        )
        self.db.commit()

        response = make_post_request(
            self.client,
            f"/api/v1/hr/leaves/{leave.id}/reject",
            {"reason": "Insufficient staffing"},
            self.manager_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "rejected"

    def test_cannot_approve_already_approved_leave(self):
        """Test cannot approve already approved leave"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            status=LeaveStatus.APPROVED
        )
        self.db.commit()

        response = make_post_request(
            self.client,
            f"/api/v1/hr/leaves/{leave.id}/approve",
            {},
            self.manager_token
        )

        assert response.status_code in [400, 409]

    def test_cancel_leave_request(self):
        """Test canceling a leave request"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            status=LeaveStatus.APPROVED
        )
        self.db.commit()

        response = make_post_request(
            self.client,
            f"/api/v1/hr/leaves/{leave.id}/cancel",
            {"reason": "Personal reasons"},
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["status"] == "cancelled"

    def test_get_courier_leave_balance(self):
        """Test getting courier's leave balance"""
        response = make_get_request(
            self.client,
            f"/api/v1/hr/couriers/{self.courier.id}/leave-balance",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert "annual_leave_balance" in data
        assert "sick_leave_balance" in data

    def test_get_leave_statistics(self):
        """Test getting leave statistics"""
        LeaveFactory.create(courier_id=self.courier.id, status=LeaveStatus.PENDING)
        LeaveFactory.create(courier_id=self.courier.id, status=LeaveStatus.APPROVED)
        LeaveFactory.create(courier_id=self.courier.id, status=LeaveStatus.REJECTED)
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/hr/leaves/statistics",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert "total_requests" in data
        assert "pending_requests" in data
        assert "approved_requests" in data

    def test_get_upcoming_leaves(self):
        """Test getting upcoming leaves"""
        LeaveFactory.create(
            courier_id=self.courier.id,
            start_date=date.today() + timedelta(days=5),
            status=LeaveStatus.APPROVED
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/hr/leaves/upcoming",
            self.admin_token,
            params={"days": 30}
        )

        assert_success_response(response)
        data = response.json()

        assert len(data) >= 1

    def test_update_leave_request(self):
        """Test updating a leave request"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            status=LeaveStatus.PENDING
        )
        self.db.commit()

        update_data = {
            "reason": "Updated reason",
            "end_date": (date.today() + timedelta(days=15)).isoformat()
        }

        response = make_put_request(
            self.client,
            f"/api/v1/hr/leaves/{leave.id}",
            update_data,
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert data["reason"] == "Updated reason"

    def test_cannot_update_approved_leave(self):
        """Test cannot update approved leave"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            status=LeaveStatus.APPROVED
        )
        self.db.commit()

        update_data = {"reason": "Updated"}

        response = make_put_request(
            self.client,
            f"/api/v1/hr/leaves/{leave.id}",
            update_data,
            self.admin_token
        )

        assert response.status_code in [400, 403]

    def test_delete_leave_request(self):
        """Test deleting a leave request"""
        leave = LeaveFactory.create(
            courier_id=self.courier.id,
            status=LeaveStatus.PENDING
        )
        self.db.commit()
        leave_id = leave.id

        response = make_delete_request(
            self.client,
            f"/api/v1/hr/leaves/{leave_id}",
            self.admin_token
        )

        assert response.status_code in [200, 204]

    def test_get_leave_by_courier(self):
        """Test getting leave requests for a specific courier"""
        LeaveFactory.create(courier_id=self.courier.id)
        LeaveFactory.create(courier_id=self.courier.id)
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/hr/couriers/{self.courier.id}/leaves",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()

        assert len(data.get("items", data)) >= 2

    def test_leave_calendar_view(self):
        """Test getting leave calendar"""
        LeaveFactory.create(
            courier_id=self.courier.id,
            start_date=date.today() + timedelta(days=10),
            status=LeaveStatus.APPROVED
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/hr/leaves/calendar",
            self.admin_token,
            params={
                "year": date.today().year,
                "month": date.today().month
            }
        )

        assert_success_response(response)
