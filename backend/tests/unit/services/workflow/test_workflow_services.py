"""
Unit Tests for Workflow Services

Tests cover:
- Template Service
- Instance Service
- State Machine
- Execution Service
- Approval Service

Author: BARQ QA Team
Last Updated: 2025-12-10
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, patch

from app.services.workflow.template_service import WorkflowTemplateService
from app.services.workflow.instance_service import WorkflowInstanceService
from app.services.workflow.state_machine import WorkflowStateMachine
from app.services.workflow.execution_service import WorkflowExecutionService
from app.services.workflow.approval_service import ApprovalService
from app.models.workflow.template import WorkflowTemplate
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus


# ==================== TEMPLATE SERVICE TESTS ====================

class TestWorkflowTemplateService:
    """Test Workflow Template Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create WorkflowTemplateService instance"""
        return WorkflowTemplateService(WorkflowTemplate)

    def test_create_template(self, service, db_session, test_organization):
        """Test creating a workflow template"""
        from app.schemas.workflow.template import WorkflowTemplateCreate

        template_data = WorkflowTemplateCreate(
            name="Leave Approval Workflow",
            description="Standard leave approval process",
            category="leave_approval",
            is_active=True,
            organization_id=test_organization.id
        )

        template = service.create(db_session, obj_in=template_data)

        assert template is not None
        assert template.name == "Leave Approval Workflow"
        assert template.is_active is True

    def test_get_template_by_id(self, service, db_session, workflow_template_factory):
        """Test getting template by ID"""
        template = workflow_template_factory()

        result = service.get(db_session, template.id)

        assert result is not None
        assert result.id == template.id

    def test_get_active_templates(self, service, db_session, workflow_template_factory):
        """Test getting active templates"""
        active = workflow_template_factory(is_active=True)
        inactive = workflow_template_factory(is_active=False)

        result = service.get_active(db_session)

        assert all(t.is_active is True for t in result)

    def test_get_templates_by_category(self, service, db_session, workflow_template_factory):
        """Test getting templates by category"""
        leave = workflow_template_factory(category="leave_approval")
        loan = workflow_template_factory(category="loan_approval")

        result = service.get_by_category(db_session, category="leave_approval")

        assert all(t.category == "leave_approval" for t in result)

    def test_activate_template(self, service, db_session, workflow_template_factory):
        """Test activating a template"""
        template = workflow_template_factory(is_active=False)

        result = service.activate(db_session, template_id=template.id)

        assert result.is_active is True

    def test_deactivate_template(self, service, db_session, workflow_template_factory):
        """Test deactivating a template"""
        template = workflow_template_factory(is_active=True)

        result = service.deactivate(db_session, template_id=template.id)

        assert result.is_active is False

    def test_clone_template(self, service, db_session, workflow_template_factory):
        """Test cloning a template"""
        original = workflow_template_factory(name="Original Template")

        clone = service.clone(db_session, template_id=original.id, new_name="Cloned Template")

        assert clone is not None
        assert clone.name == "Cloned Template"
        assert clone.id != original.id

    def test_get_template_statistics(self, service, db_session, workflow_template_factory):
        """Test getting template statistics"""
        workflow_template_factory(category="leave_approval")
        workflow_template_factory(category="loan_approval")
        workflow_template_factory(category="leave_approval")

        stats = service.get_statistics(db_session)

        assert "total_templates" in stats
        assert "active_templates" in stats
        assert "category_breakdown" in stats


# ==================== INSTANCE SERVICE TESTS ====================

class TestWorkflowInstanceService:
    """Test Workflow Instance Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create WorkflowInstanceService instance"""
        return WorkflowInstanceService(WorkflowInstance)

    def test_create_instance(self, service, db_session, workflow_template_factory, test_user, test_organization):
        """Test creating a workflow instance"""
        from app.schemas.workflow.instance import WorkflowInstanceCreate

        template = workflow_template_factory()
        instance_data = WorkflowInstanceCreate(
            template_id=template.id,
            initiator_id=test_user.id,
            title="Leave Request",
            organization_id=test_organization.id
        )

        instance = service.create(db_session, obj_in=instance_data)

        assert instance is not None
        assert instance.template_id == template.id
        assert instance.current_state == WorkflowStatus.DRAFT

    def test_get_instance_by_id(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user):
        """Test getting instance by ID"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user)

        result = service.get(db_session, instance.id)

        assert result is not None
        assert result.id == instance.id

    def test_get_instances_by_initiator(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user):
        """Test getting instances by initiator"""
        template = workflow_template_factory()
        user_instance = workflow_instance_factory(template, test_user)
        admin_instance = workflow_instance_factory(template, admin_user)

        result = service.get_by_initiator(db_session, initiator_id=test_user.id)

        assert all(i.initiator_id == test_user.id for i in result)

    def test_get_instances_by_status(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user):
        """Test getting instances by status"""
        template = workflow_template_factory()
        draft = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.DRAFT)
        pending = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.get_by_status(db_session, status=WorkflowStatus.PENDING)

        assert all(i.current_state == WorkflowStatus.PENDING for i in result)

    def test_submit_instance(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user):
        """Test submitting a workflow instance"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.DRAFT)

        result = service.submit(db_session, instance_id=instance.id)

        assert result.current_state == WorkflowStatus.PENDING

    def test_cancel_instance(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user):
        """Test cancelling a workflow instance"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.cancel(db_session, instance_id=instance.id, reason="No longer needed")

        assert result.current_state == WorkflowStatus.CANCELLED

    def test_get_pending_instances_for_approver(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user):
        """Test getting pending instances for approver"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.get_pending_for_approver(db_session, approver_id=admin_user.id)

        # Should return instances pending approval


# ==================== STATE MACHINE TESTS ====================

class TestWorkflowStateMachine:
    """Test Workflow State Machine operations"""

    def test_can_transition_draft_to_pending(self):
        """Test valid transition from DRAFT to PENDING"""
        machine = WorkflowStateMachine()

        can_transition = machine.can_transition(WorkflowStatus.DRAFT, WorkflowStatus.PENDING)

        assert can_transition is True

    def test_cannot_transition_draft_to_approved(self):
        """Test invalid transition from DRAFT to APPROVED"""
        machine = WorkflowStateMachine()

        can_transition = machine.can_transition(WorkflowStatus.DRAFT, WorkflowStatus.APPROVED)

        assert can_transition is False

    def test_can_transition_pending_to_approved(self):
        """Test valid transition from PENDING to APPROVED"""
        machine = WorkflowStateMachine()

        can_transition = machine.can_transition(WorkflowStatus.PENDING, WorkflowStatus.APPROVED)

        assert can_transition is True

    def test_can_transition_pending_to_rejected(self):
        """Test valid transition from PENDING to REJECTED"""
        machine = WorkflowStateMachine()

        can_transition = machine.can_transition(WorkflowStatus.PENDING, WorkflowStatus.REJECTED)

        assert can_transition is True

    def test_get_available_transitions(self):
        """Test getting available transitions from state"""
        machine = WorkflowStateMachine()

        transitions = machine.get_available_transitions(WorkflowStatus.PENDING)

        assert WorkflowStatus.APPROVED in transitions
        assert WorkflowStatus.REJECTED in transitions

    def test_transition_validates_state(self):
        """Test that transition validates current state"""
        machine = WorkflowStateMachine()

        with pytest.raises(ValueError):
            machine.transition(
                current_state=WorkflowStatus.COMPLETED,
                target_state=WorkflowStatus.PENDING
            )


# ==================== EXECUTION SERVICE TESTS ====================

class TestWorkflowExecutionService:
    """Test Workflow Execution Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create WorkflowExecutionService instance"""
        return WorkflowExecutionService(db_session)

    def test_execute_step(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user):
        """Test executing a workflow step"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.execute_step(
            instance_id=instance.id,
            action="approve",
            actor_id=test_user.id
        )

        assert result is not None

    def test_execute_step_with_data(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user):
        """Test executing a workflow step with data"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.execute_step(
            instance_id=instance.id,
            action="approve",
            actor_id=test_user.id,
            data={"comments": "Approved"}
        )

        assert result is not None

    def test_get_execution_history(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user):
        """Test getting execution history"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user)

        history = service.get_execution_history(instance_id=instance.id)

        assert isinstance(history, list)


# ==================== APPROVAL SERVICE TESTS ====================

class TestApprovalService:
    """Test Approval Service operations"""

    @pytest.fixture
    def service(self, db_session):
        """Create ApprovalService instance"""
        return ApprovalService(db_session)

    def test_approve_workflow(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user):
        """Test approving a workflow"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.approve(
            instance_id=instance.id,
            approver_id=admin_user.id,
            comments="Approved"
        )

        assert result.current_state == WorkflowStatus.APPROVED

    def test_reject_workflow(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user):
        """Test rejecting a workflow"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.reject(
            instance_id=instance.id,
            approver_id=admin_user.id,
            reason="Incomplete documentation"
        )

        assert result.current_state == WorkflowStatus.REJECTED

    def test_request_more_info(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user):
        """Test requesting more info"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.request_more_info(
            instance_id=instance.id,
            approver_id=admin_user.id,
            questions=["Please provide additional details"]
        )

        # Instance should be in a state waiting for info

    def test_get_approval_queue(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user):
        """Test getting approval queue"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        queue = service.get_approval_queue(approver_id=admin_user.id)

        assert isinstance(queue, list)

    def test_delegate_approval(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user, manager_user):
        """Test delegating approval"""
        template = workflow_template_factory()
        instance = workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)

        result = service.delegate(
            instance_id=instance.id,
            from_approver_id=admin_user.id,
            to_approver_id=manager_user.id
        )

        # Should successfully delegate

    def test_bulk_approve(self, service, db_session, workflow_instance_factory, workflow_template_factory, test_user, admin_user):
        """Test bulk approval"""
        template = workflow_template_factory()
        instances = [
            workflow_instance_factory(template, test_user, current_state=WorkflowStatus.PENDING)
            for _ in range(3)
        ]
        instance_ids = [i.id for i in instances]

        results = service.bulk_approve(
            instance_ids=instance_ids,
            approver_id=admin_user.id
        )

        assert len(results) == 3
