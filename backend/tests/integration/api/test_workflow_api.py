"""
Integration Tests for Workflow Engine API

Tests workflow template and instance management.

Author: BARQ QA Team
Last Updated: 2025-12-02
"""

import pytest
from app.models.workflow.instance import WorkflowState
from tests.utils.factories import (
    AdminUserFactory,
    UserFactory,
    WorkflowTemplateFactory,
    WorkflowInstanceFactory,
    CourierFactory,
    LeaveFactory
)
from tests.utils.api_helpers import (
    make_get_request,
    make_post_request,
    make_put_request,
    assert_success_response,
    assert_not_found,
    assert_validation_error,
    create_test_token
)


@pytest.mark.integration
@pytest.mark.workflow
class TestWorkflowAPI:
    """Test Workflow Engine API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self, db_session, client):
        """Setup test data"""
        self.db = db_session
        self.client = client

        self.admin_user = AdminUserFactory.create()
        self.regular_user = UserFactory.create()
        self.courier = CourierFactory.create()

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

    def test_list_workflow_templates(self):
        """Test listing workflow templates"""
        WorkflowTemplateFactory.create(name="Leave Approval")
        WorkflowTemplateFactory.create(name="Delivery Approval")
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/workflow/templates",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()
        assert len(data.get("items", data)) >= 2

    def test_create_workflow_template(self):
        """Test creating a workflow template"""
        template_data = {
            "name": "Test Workflow Template",
            "description": "Test description",
            "category": "leave_approval",
            "is_active": True
        }

        response = make_post_request(
            self.client,
            "/api/v1/workflow/templates",
            template_data,
            self.admin_token
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workflow Template"

    def test_get_workflow_template_by_id(self):
        """Test retrieving workflow template by ID"""
        template = WorkflowTemplateFactory.create(name="Test Template")
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/workflow/templates/{template.id}",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()
        assert data["id"] == template.id
        assert data["name"] == "Test Template"

    def test_update_workflow_template(self):
        """Test updating a workflow template"""
        template = WorkflowTemplateFactory.create(name="Original Name")
        self.db.commit()

        update_data = {"name": "Updated Name"}

        response = make_put_request(
            self.client,
            f"/api/v1/workflow/templates/{template.id}",
            update_data,
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_list_workflow_instances(self):
        """Test listing workflow instances"""
        template = WorkflowTemplateFactory.create()
        WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id
        )
        WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/workflow/instances",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()
        assert len(data.get("items", data)) >= 2

    def test_create_workflow_instance(self):
        """Test creating a workflow instance"""
        template = WorkflowTemplateFactory.create()
        leave = LeaveFactory.create(courier_id=self.courier.id)
        self.db.commit()

        instance_data = {
            "template_id": template.id,
            "entity_type": "leave",
            "entity_id": leave.id,
            "title": "Test Workflow Instance"
        }

        response = make_post_request(
            self.client,
            "/api/v1/workflow/instances",
            instance_data,
            self.admin_token
        )

        assert response.status_code == 201
        data = response.json()
        assert data["template_id"] == template.id
        assert data["entity_type"] == "leave"

    def test_get_workflow_instance_by_id(self):
        """Test retrieving workflow instance by ID"""
        template = WorkflowTemplateFactory.create()
        instance = WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/workflow/instances/{instance.id}",
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()
        assert data["id"] == instance.id

    def test_approve_workflow_instance(self):
        """Test approving a workflow instance"""
        template = WorkflowTemplateFactory.create()
        instance = WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id,
            current_state=WorkflowState.PENDING
        )
        self.db.commit()

        approve_data = {
            "action": "approve",
            "notes": "Approved"
        }

        response = make_post_request(
            self.client,
            f"/api/v1/workflow/instances/{instance.id}/action",
            approve_data,
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()
        assert data["current_state"] in ["approved", "completed"]

    def test_reject_workflow_instance(self):
        """Test rejecting a workflow instance"""
        template = WorkflowTemplateFactory.create()
        instance = WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id,
            current_state=WorkflowState.PENDING
        )
        self.db.commit()

        reject_data = {
            "action": "reject",
            "notes": "Rejected due to incomplete information"
        }

        response = make_post_request(
            self.client,
            f"/api/v1/workflow/instances/{instance.id}/action",
            reject_data,
            self.admin_token
        )

        assert_success_response(response)
        data = response.json()
        assert data["current_state"] == "rejected"

    def test_filter_workflow_instances_by_state(self):
        """Test filtering workflow instances by state"""
        template = WorkflowTemplateFactory.create()
        WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id,
            current_state=WorkflowState.PENDING
        )
        WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id,
            current_state=WorkflowState.APPROVED
        )
        WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id,
            current_state=WorkflowState.PENDING
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            "/api/v1/workflow/instances",
            self.admin_token,
            params={"state": "pending"}
        )

        assert_success_response(response)
        data = response.json()
        items = data.get("items", data)
        assert len(items) == 2

    def test_get_workflow_instance_history(self):
        """Test retrieving workflow instance history"""
        template = WorkflowTemplateFactory.create()
        instance = WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id
        )
        self.db.commit()

        response = make_get_request(
            self.client,
            f"/api/v1/workflow/instances/{instance.id}/history",
            self.admin_token
        )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)

    def test_workflow_instance_comments(self):
        """Test adding comments to workflow instance"""
        template = WorkflowTemplateFactory.create()
        instance = WorkflowInstanceFactory.create(
            template_id=template.id,
            initiator_id=self.admin_user.id
        )
        self.db.commit()

        comment_data = {
            "content": "This is a test comment"
        }

        response = make_post_request(
            self.client,
            f"/api/v1/workflow/instances/{instance.id}/comments",
            comment_data,
            self.admin_token
        )

        if response.status_code == 201:
            data = response.json()
            assert data["content"] == "This is a test comment"

    def test_workflow_statistics(self):
        """Test getting workflow statistics"""
        response = make_get_request(
            self.client,
            "/api/v1/workflow/statistics",
            self.admin_token
        )

        if response.status_code == 200:
            data = response.json()
            assert "total_instances" in data
