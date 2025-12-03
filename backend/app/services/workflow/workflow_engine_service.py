"""Workflow Engine with State Machine

Implements workflow execution with state management:
- State machine for workflow steps
- Automatic step transitions
- Approval chains
- SLA tracking
- Conditional branching
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.models.workflow.template import WorkflowTemplate


class StepAction(str, Enum):
    """Actions that can be performed on workflow steps"""

    APPROVE = "approve"
    REJECT = "reject"
    COMPLETE = "complete"
    SKIP = "skip"
    DELEGATE = "delegate"


class WorkflowEngineService:
    """
    Workflow execution engine with state machine

    Features:
    - State machine for step management
    - Automatic step progression
    - Approval chains
    - SLA monitoring
    - Event triggers
    """

    def start_workflow(
        self, db: Session, template_id: int, initiated_by: int, initial_data: Optional[Dict] = None
    ) -> WorkflowInstance:
        """
        Start a new workflow instance

        Args:
            db: Database session
            template_id: Workflow template ID
            initiated_by: User ID who initiated the workflow
            initial_data: Initial workflow data

        Returns:
            Created workflow instance
        """
        template = db.query(WorkflowTemplate).filter(WorkflowTemplate.id == template_id).first()

        if not template:
            raise ValueError(f"Workflow template {template_id} not found")

        # Create workflow instance
        instance = WorkflowInstance(
            template_id=template_id,
            initiated_by=initiated_by,
            status=WorkflowStatus.IN_PROGRESS,
            current_step=0,
            data=initial_data or {},
        )

        db.add(instance)
        db.commit()
        db.refresh(instance)

        return instance

    def get_current_step(self, db: Session, instance_id: int) -> Optional[Dict[str, Any]]:
        """Get the current step details for a workflow instance"""
        instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()

        if not instance or not instance.template:
            return None

        template = instance.template
        steps = template.steps

        if not steps or instance.current_step >= len(steps):
            return None

        current_step = steps[instance.current_step]

        return {
            "step_number": instance.current_step,
            "step_name": current_step.get("name", ""),
            "step_type": current_step.get("type", ""),
            "description": current_step.get("description", ""),
            "assigned_to": current_step.get("assigned_to", None),
            "requires_approval": current_step.get("requires_approval", False),
            "sla_hours": current_step.get("sla_hours", None),
        }

    def execute_step_action(
        self,
        db: Session,
        instance_id: int,
        action: StepAction,
        user_id: int,
        comments: Optional[str] = None,
        data: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Execute an action on the current workflow step

        Args:
            db: Database session
            instance_id: Workflow instance ID
            action: Action to execute
            user_id: User performing the action
            comments: Optional comments
            data: Optional data to update

        Returns:
            Result of the action
        """
        instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()

        if not instance:
            return {"success": False, "error": "Workflow instance not found"}

        current_step = self.get_current_step(db, instance_id)

        if not current_step:
            return {"success": False, "error": "No current step found"}

        # Check if user is authorized for this step
        if current_step.get("assigned_to") and current_step["assigned_to"] != user_id:
            return {"success": False, "error": "User not authorized for this step"}

        # Update workflow data if provided
        if data:
            if not instance.data:
                instance.data = {}
            instance.data.update(data)

        # Add action to history
        if not instance.data.get("history"):
            instance.data["history"] = []

        instance.data["history"].append(
            {
                "step": instance.current_step,
                "action": action.value,
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "comments": comments,
            }
        )

        # Handle action
        if action == StepAction.APPROVE:
            return self._handle_approve(db, instance, current_step)

        elif action == StepAction.REJECT:
            return self._handle_reject(db, instance, comments)

        elif action == StepAction.COMPLETE:
            return self._handle_complete(db, instance)

        elif action == StepAction.SKIP:
            return self._handle_skip(db, instance)

        else:
            return {"success": False, "error": f"Unsupported action: {action}"}

    def _handle_approve(
        self, db: Session, instance: WorkflowInstance, current_step: Dict
    ) -> Dict[str, Any]:
        """Handle approval action"""
        # Move to next step
        instance.current_step += 1

        # Check if workflow is complete
        if instance.current_step >= len(instance.template.steps):
            instance.status = WorkflowStatus.COMPLETED
            instance.current_step = len(instance.template.steps) - 1

        db.commit()
        db.refresh(instance)

        return {
            "success": True,
            "message": "Step approved, moved to next step",
            "current_step": instance.current_step,
            "status": instance.status.value,
        }

    def _handle_reject(
        self, db: Session, instance: WorkflowInstance, comments: Optional[str]
    ) -> Dict[str, Any]:
        """Handle rejection action"""
        instance.status = WorkflowStatus.REJECTED

        if not instance.data:
            instance.data = {}

        instance.data["rejection_reason"] = comments

        db.commit()
        db.refresh(instance)

        return {"success": True, "message": "Workflow rejected", "status": instance.status.value}

    def _handle_complete(self, db: Session, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle complete action"""
        instance.status = WorkflowStatus.COMPLETED

        db.commit()
        db.refresh(instance)

        return {"success": True, "message": "Workflow completed", "status": instance.status.value}

    def _handle_skip(self, db: Session, instance: WorkflowInstance) -> Dict[str, Any]:
        """Handle skip action"""
        instance.current_step += 1

        if instance.current_step >= len(instance.template.steps):
            instance.status = WorkflowStatus.COMPLETED

        db.commit()
        db.refresh(instance)

        return {
            "success": True,
            "message": "Step skipped",
            "current_step": instance.current_step,
            "status": instance.status.value,
        }

    def check_sla_violations(self, db: Session, instance_id: int) -> Dict[str, Any]:
        """Check if workflow has SLA violations"""
        instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()

        if not instance or not instance.template:
            return {"has_violation": False}

        current_step = self.get_current_step(db, instance_id)

        if not current_step or not current_step.get("sla_hours"):
            return {"has_violation": False}

        sla_hours = current_step["sla_hours"]
        elapsed_hours = (datetime.utcnow() - instance.created_at).total_seconds() / 3600

        has_violation = elapsed_hours > sla_hours

        return {
            "has_violation": has_violation,
            "sla_hours": sla_hours,
            "elapsed_hours": round(elapsed_hours, 2),
            "remaining_hours": round(sla_hours - elapsed_hours, 2),
        }

    def get_pending_approvals(self, db: Session, user_id: int) -> List[WorkflowInstance]:
        """Get all workflow instances pending approval by user"""
        instances = (
            db.query(WorkflowInstance)
            .filter(WorkflowInstance.status == WorkflowStatus.PENDING_APPROVAL)
            .all()
        )

        # Filter by user's assignment
        pending_for_user = []
        for instance in instances:
            current_step = self.get_current_step(db, instance.id)
            if current_step and current_step.get("assigned_to") == user_id:
                pending_for_user.append(instance)

        return pending_for_user

    def get_workflow_history(self, db: Session, instance_id: int) -> List[Dict[str, Any]]:
        """Get workflow execution history"""
        instance = db.query(WorkflowInstance).filter(WorkflowInstance.id == instance_id).first()

        if not instance or not instance.data:
            return []

        return instance.data.get("history", [])


# Singleton instance
workflow_engine_service = WorkflowEngineService()
