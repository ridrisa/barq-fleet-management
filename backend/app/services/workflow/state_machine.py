"""
Workflow State Machine
Manages workflow instance state transitions and validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.models.workflow.instance import WorkflowStatus


class WorkflowStateMachine:
    """
    State machine for workflow instances

    State Transition Diagram:

    PENDING → IN_PROGRESS → COMPLETED
         ↓           ↓            ↑
    CANCELLED  REJECTED     APPROVED
                     ↓
              PENDING_APPROVAL

    """

    # Valid state transitions
    TRANSITIONS: Dict[WorkflowStatus, List[WorkflowStatus]] = {
        WorkflowStatus.DRAFT: [
            WorkflowStatus.IN_PROGRESS,
            WorkflowStatus.CANCELLED,
        ],
        WorkflowStatus.IN_PROGRESS: [
            WorkflowStatus.PENDING_APPROVAL,
            WorkflowStatus.COMPLETED,
            WorkflowStatus.REJECTED,
            WorkflowStatus.CANCELLED,
        ],
        WorkflowStatus.PENDING_APPROVAL: [
            WorkflowStatus.APPROVED,
            WorkflowStatus.REJECTED,
            WorkflowStatus.IN_PROGRESS,  # Back to in progress if changes needed
            WorkflowStatus.CANCELLED,
        ],
        WorkflowStatus.APPROVED: [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.IN_PROGRESS,  # Can continue processing
        ],
        WorkflowStatus.REJECTED: [
            WorkflowStatus.IN_PROGRESS,  # Can be restarted
            WorkflowStatus.CANCELLED,
        ],
        WorkflowStatus.COMPLETED: [],  # Terminal state
        WorkflowStatus.CANCELLED: [],  # Terminal state
    }

    # Terminal states (cannot be transitioned from)
    TERMINAL_STATES = [WorkflowStatus.COMPLETED, WorkflowStatus.CANCELLED]

    # States that require approval
    APPROVAL_STATES = [WorkflowStatus.PENDING_APPROVAL]

    @classmethod
    def can_transition(cls, from_status: WorkflowStatus, to_status: WorkflowStatus) -> bool:
        """Check if transition from one status to another is valid"""
        if from_status not in cls.TRANSITIONS:
            return False
        return to_status in cls.TRANSITIONS[from_status]

    @classmethod
    def get_valid_transitions(cls, from_status: WorkflowStatus) -> List[WorkflowStatus]:
        """Get list of valid transitions from current status"""
        return cls.TRANSITIONS.get(from_status, [])

    @classmethod
    def is_terminal(cls, status: WorkflowStatus) -> bool:
        """Check if status is a terminal state"""
        return status in cls.TERMINAL_STATES

    @classmethod
    def requires_approval(cls, status: WorkflowStatus) -> bool:
        """Check if status requires approval"""
        return status in cls.APPROVAL_STATES

    @classmethod
    def validate_transition(
        cls, from_status: WorkflowStatus, to_status: WorkflowStatus
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate state transition and return (is_valid, error_message)
        """
        if from_status == to_status:
            return True, None  # No transition needed

        if cls.is_terminal(from_status):
            return False, f"Cannot transition from terminal state {from_status.value}"

        if not cls.can_transition(from_status, to_status):
            return False, f"Invalid transition from {from_status.value} to {to_status.value}"

        return True, None


class WorkflowStepExecutor:
    """
    Executes workflow steps based on step configuration
    """

    @staticmethod
    def can_execute_step(
        instance_data: dict,
        step_config: dict,
        current_step_index: int,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a step can be executed based on conditions

        Args:
            instance_data: Current workflow instance data
            step_config: Step configuration from template
            current_step_index: Index of current step

        Returns:
            (can_execute, reason)
        """
        # Check if step has conditions
        conditions = step_config.get("conditions", [])
        if not conditions:
            return True, None

        # Evaluate conditions
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            if not field or not operator:
                continue

            field_value = instance_data.get(field)

            # Evaluate based on operator
            if operator == "equals" and field_value != value:
                return False, f"Condition not met: {field} must equal {value}"
            elif operator == "not_equals" and field_value == value:
                return False, f"Condition not met: {field} must not equal {value}"
            elif operator == "greater_than" and not (field_value and field_value > value):
                return False, f"Condition not met: {field} must be greater than {value}"
            elif operator == "less_than" and not (field_value and field_value < value):
                return False, f"Condition not met: {field} must be less than {value}"
            elif operator == "contains" and not (field_value and value in str(field_value)):
                return False, f"Condition not met: {field} must contain {value}"
            elif operator == "exists" and field_value is None:
                return False, f"Condition not met: {field} must exist"

        return True, None

    @staticmethod
    def execute_step_action(
        step_config: dict,
        instance_data: dict,
    ) -> Tuple[bool, dict, Optional[str]]:
        """
        Execute the action defined in a step

        Args:
            step_config: Step configuration
            instance_data: Current instance data

        Returns:
            (success, updated_data, error_message)
        """
        action_type = step_config.get("action_type", "manual")

        # Manual action - requires user input
        if action_type == "manual":
            return True, instance_data, None

        # Auto-complete action
        if action_type == "auto_complete":
            return True, instance_data, None

        # Set field action
        if action_type == "set_field":
            field = step_config.get("field")
            value = step_config.get("value")
            if field:
                instance_data[field] = value
            return True, instance_data, None

        # Update field action
        if action_type == "update_field":
            field = step_config.get("field")
            operation = step_config.get("operation", "set")
            value = step_config.get("value")

            if field and value is not None:
                if operation == "increment":
                    instance_data[field] = instance_data.get(field, 0) + value
                elif operation == "decrement":
                    instance_data[field] = instance_data.get(field, 0) - value
                elif operation == "append":
                    if field not in instance_data:
                        instance_data[field] = []
                    if isinstance(instance_data[field], list):
                        instance_data[field].append(value)
                else:  # set
                    instance_data[field] = value

            return True, instance_data, None

        # Custom action - would be handled by automation service
        if action_type == "custom":
            return True, instance_data, "Custom action requires external processing"

        return False, instance_data, f"Unknown action type: {action_type}"


class WorkflowExecutionEngine:
    """
    Main workflow execution engine
    Orchestrates workflow instance execution
    """

    def __init__(self):
        self.state_machine = WorkflowStateMachine()
        self.step_executor = WorkflowStepExecutor()

    def start_workflow(self, template_steps: List[dict]) -> Tuple[bool, dict, Optional[str]]:
        """
        Start a workflow instance

        Returns:
            (success, initial_data, error_message)
        """
        if not template_steps:
            return False, {}, "Template has no steps defined"

        # Initialize workflow data
        initial_data = {
            "started_at": datetime.utcnow().isoformat(),
            "steps_completed": [],
            "steps_skipped": [],
            "step_history": [],
        }

        return True, initial_data, None

    def advance_step(
        self,
        current_step: int,
        template_steps: List[dict],
        instance_data: dict,
    ) -> Tuple[bool, int, dict, Optional[str]]:
        """
        Advance to next step in workflow

        Returns:
            (success, next_step_index, updated_data, error_message)
        """
        if current_step >= len(template_steps):
            return False, current_step, instance_data, "Already at last step"

        next_step = current_step + 1

        # Check if there's a next step
        if next_step >= len(template_steps):
            # Workflow complete
            instance_data["completed_at"] = datetime.utcnow().isoformat()
            return True, next_step, instance_data, None

        # Check if next step can be executed
        next_step_config = template_steps[next_step]
        can_execute, reason = self.step_executor.can_execute_step(
            instance_data, next_step_config, next_step
        )

        if not can_execute:
            # Skip this step
            instance_data["steps_skipped"].append(
                {
                    "step_index": next_step,
                    "reason": reason,
                    "skipped_at": datetime.utcnow().isoformat(),
                }
            )
            # Try next step recursively
            return self.advance_step(next_step, template_steps, instance_data)

        # Execute step action if auto-executable
        if next_step_config.get("action_type") in ["auto_complete", "set_field", "update_field"]:
            success, updated_data, error = self.step_executor.execute_step_action(
                next_step_config, instance_data
            )
            if success:
                instance_data = updated_data
                instance_data["steps_completed"].append(
                    {
                        "step_index": next_step,
                        "completed_at": datetime.utcnow().isoformat(),
                    }
                )

        # Record step transition
        instance_data["step_history"].append(
            {
                "from_step": current_step,
                "to_step": next_step,
                "transitioned_at": datetime.utcnow().isoformat(),
            }
        )

        return True, next_step, instance_data, None

    def complete_current_step(
        self,
        current_step: int,
        template_steps: List[dict],
        instance_data: dict,
        step_data: Optional[dict] = None,
    ) -> Tuple[bool, dict, Optional[str]]:
        """
        Mark current step as complete and update instance data

        Returns:
            (success, updated_data, error_message)
        """
        if current_step >= len(template_steps):
            return False, instance_data, "Invalid step index"

        # Merge step data into instance data
        if step_data:
            instance_data.update(step_data)

        # Mark step as completed
        instance_data["steps_completed"].append(
            {
                "step_index": current_step,
                "completed_at": datetime.utcnow().isoformat(),
            }
        )

        return True, instance_data, None
