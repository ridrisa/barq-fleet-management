"""
Workflow Execution Service
Handles workflow instance execution, state transitions, and step progression
"""
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.models.workflow.template import WorkflowTemplate
from app.crud.workflow import workflow_instance, workflow_template
from app.services.workflow.state_machine import WorkflowExecutionEngine
from app.core.exceptions import AppException


class WorkflowExecutionService:
    """Service for executing workflows"""

    def __init__(self, db: Session):
        self.db = db
        self.engine = WorkflowExecutionEngine()

    def create_and_start_workflow(
        self,
        template_id: int,
        initiated_by: int,
        initial_data: Optional[Dict[str, Any]] = None,
    ) -> WorkflowInstance:
        """
        Create a new workflow instance from template and start it

        Args:
            template_id: Workflow template ID
            initiated_by: User ID who initiated the workflow
            initial_data: Initial workflow data

        Returns:
            WorkflowInstance
        """
        # Get template
        template = workflow_template.get(self.db, id=template_id)
        if not template:
            raise AppException(
                status_code=404,
                detail="Workflow template not found",
                code="TEMPLATE_NOT_FOUND",
            )

        if not template.is_active:
            raise AppException(
                status_code=400,
                detail="Workflow template is not active",
                code="TEMPLATE_INACTIVE",
            )

        # Initialize workflow using engine
        success, workflow_data, error = self.engine.start_workflow(template.steps)
        if not success:
            raise AppException(
                status_code=400, detail=error or "Failed to start workflow", code="START_FAILED"
            )

        # Merge initial data
        if initial_data:
            workflow_data.update(initial_data)

        # Create instance
        instance = workflow_instance.create(
            self.db,
            obj_in={
                "template_id": template_id,
                "initiated_by": initiated_by,
                "status": WorkflowStatus.IN_PROGRESS,
                "current_step": 0,
                "data": workflow_data,
                "started_at": datetime.utcnow(),
            },
        )

        return instance

    def advance_workflow(
        self,
        instance_id: int,
        step_data: Optional[Dict[str, Any]] = None,
    ) -> WorkflowInstance:
        """
        Advance workflow to next step

        Args:
            instance_id: Workflow instance ID
            step_data: Data from completed step

        Returns:
            Updated WorkflowInstance
        """
        # Get instance with template
        instance = workflow_instance.get(self.db, id=instance_id)
        if not instance:
            raise AppException(
                status_code=404,
                detail="Workflow instance not found",
                code="INSTANCE_NOT_FOUND",
            )

        # Check if workflow can be advanced
        if self.engine.state_machine.is_terminal(instance.status):
            raise AppException(
                status_code=400,
                detail=f"Cannot advance workflow in {instance.status.value} state",
                code="TERMINAL_STATE",
            )

        # Get template
        template = instance.template
        if not template:
            raise AppException(
                status_code=404,
                detail="Workflow template not found",
                code="TEMPLATE_NOT_FOUND",
            )

        # Complete current step first
        current_data = instance.data or {}
        success, updated_data, error = self.engine.complete_current_step(
            instance.current_step,
            template.steps,
            current_data,
            step_data,
        )

        if not success:
            raise AppException(
                status_code=400,
                detail=error or "Failed to complete step",
                code="STEP_COMPLETION_FAILED",
            )

        # Advance to next step
        success, next_step, final_data, error = self.engine.advance_step(
            instance.current_step,
            template.steps,
            updated_data,
        )

        if not success:
            raise AppException(
                status_code=400,
                detail=error or "Failed to advance step",
                code="STEP_ADVANCE_FAILED",
            )

        # Determine new status
        new_status = instance.status
        completed_at = None

        if next_step >= len(template.steps):
            # Workflow complete
            new_status = WorkflowStatus.COMPLETED
            completed_at = datetime.utcnow()

        # Update instance
        instance = workflow_instance.update(
            self.db,
            db_obj=instance,
            obj_in={
                "current_step": next_step,
                "status": new_status,
                "data": final_data,
                "completed_at": completed_at,
            },
        )

        return instance

    def transition_status(
        self,
        instance_id: int,
        new_status: WorkflowStatus,
        notes: Optional[str] = None,
    ) -> WorkflowInstance:
        """
        Transition workflow to a new status

        Args:
            instance_id: Workflow instance ID
            new_status: Target status
            notes: Optional notes about transition

        Returns:
            Updated WorkflowInstance
        """
        instance = workflow_instance.get(self.db, id=instance_id)
        if not instance:
            raise AppException(
                status_code=404,
                detail="Workflow instance not found",
                code="INSTANCE_NOT_FOUND",
            )

        # Validate transition
        is_valid, error = self.engine.state_machine.validate_transition(
            instance.status, new_status
        )

        if not is_valid:
            raise AppException(
                status_code=400, detail=error or "Invalid status transition", code="INVALID_TRANSITION"
            )

        # Update instance
        update_data = {"status": new_status}

        if notes:
            update_data["notes"] = notes

        if new_status == WorkflowStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()

        instance = workflow_instance.update(
            self.db,
            db_obj=instance,
            obj_in=update_data,
        )

        return instance

    def cancel_workflow(
        self, instance_id: int, reason: Optional[str] = None
    ) -> WorkflowInstance:
        """
        Cancel a workflow instance

        Args:
            instance_id: Workflow instance ID
            reason: Cancellation reason

        Returns:
            Updated WorkflowInstance
        """
        return self.transition_status(
            instance_id,
            WorkflowStatus.CANCELLED,
            notes=reason,
        )

    def get_workflow_status(self, instance_id: int) -> Dict[str, Any]:
        """
        Get detailed workflow status including progress

        Args:
            instance_id: Workflow instance ID

        Returns:
            Dictionary with workflow status details
        """
        instance = workflow_instance.get(self.db, id=instance_id)
        if not instance:
            raise AppException(
                status_code=404,
                detail="Workflow instance not found",
                code="INSTANCE_NOT_FOUND",
            )

        template = instance.template
        total_steps = len(template.steps) if template else 0
        current_step = instance.current_step

        # Calculate progress
        progress_percentage = 0
        if total_steps > 0:
            progress_percentage = (current_step / total_steps) * 100

        # Get completed steps count
        instance_data = instance.data or {}
        completed_steps = len(instance_data.get("steps_completed", []))
        skipped_steps = len(instance_data.get("steps_skipped", []))

        return {
            "instance_id": instance.id,
            "status": instance.status.value,
            "current_step": current_step,
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "skipped_steps": skipped_steps,
            "progress_percentage": round(progress_percentage, 2),
            "started_at": instance.started_at,
            "completed_at": instance.completed_at,
            "is_terminal": self.engine.state_machine.is_terminal(instance.status),
            "valid_transitions": [
                s.value
                for s in self.engine.state_machine.get_valid_transitions(instance.status)
            ],
        }
