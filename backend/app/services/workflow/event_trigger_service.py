"""Workflow Event Trigger Service

Handles automatic workflow creation when specific events occur (e.g., loan/leave creation).
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime, date
import logging

from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.models.workflow.trigger import (
    WorkflowTrigger, TriggerExecution, TriggerType, TriggerEventType
)
from app.models.workflow.template import WorkflowTemplate

logger = logging.getLogger(__name__)


class EventTriggerService:
    """Service for handling workflow event triggers"""

    def trigger_workflow_for_entity(
        self,
        db: Session,
        *,
        entity_type: str,
        entity_id: int,
        event_type: TriggerEventType,
        entity_data: Dict[str, Any],
        initiated_by: int,
    ) -> Optional[WorkflowInstance]:
        """
        Trigger a workflow for a specific entity event.

        Args:
            entity_type: Type of entity (loan, leave, etc.)
            entity_id: ID of the entity
            event_type: Type of event (record_created, etc.)
            entity_data: Data from the entity
            initiated_by: User ID who initiated the action

        Returns:
            Created workflow instance if a matching trigger exists
        """
        # Find matching active trigger
        trigger = self._find_matching_trigger(
            db, entity_type=entity_type, event_type=event_type
        )

        if not trigger:
            logger.info(f"No workflow trigger found for {entity_type} {event_type}")
            return None

        # Check conditions if any
        if not self._evaluate_conditions(trigger, entity_data):
            logger.info(f"Trigger conditions not met for {entity_type} {entity_id}")
            return None

        # Create workflow instance
        workflow_instance = self._create_workflow_instance(
            db,
            trigger=trigger,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_data=entity_data,
            initiated_by=initiated_by,
        )

        # Log trigger execution
        self._log_trigger_execution(
            db,
            trigger=trigger,
            workflow_instance=workflow_instance,
            entity_data=entity_data,
        )

        return workflow_instance

    def _find_matching_trigger(
        self,
        db: Session,
        *,
        entity_type: str,
        event_type: TriggerEventType,
    ) -> Optional[WorkflowTrigger]:
        """Find an active trigger matching the entity type and event"""
        return (
            db.query(WorkflowTrigger)
            .filter(
                WorkflowTrigger.is_active == True,
                WorkflowTrigger.entity_type == entity_type,
                WorkflowTrigger.event_type == event_type,
                WorkflowTrigger.trigger_type.in_([
                    TriggerType.AUTOMATIC,
                    TriggerType.EVENT_BASED,
                ]),
            )
            .order_by(WorkflowTrigger.priority.desc())
            .first()
        )

    def _evaluate_conditions(
        self, trigger: WorkflowTrigger, entity_data: Dict[str, Any]
    ) -> bool:
        """Evaluate trigger conditions against entity data"""
        if not trigger.conditions:
            return True

        conditions = trigger.conditions
        logic = trigger.condition_logic or "AND"

        results = []
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")

            entity_value = entity_data.get(field)

            if operator == "equals":
                results.append(entity_value == value)
            elif operator == "not_equals":
                results.append(entity_value != value)
            elif operator == "greater_than":
                results.append(float(entity_value or 0) > float(value))
            elif operator == "less_than":
                results.append(float(entity_value or 0) < float(value))
            elif operator == "contains":
                results.append(value in str(entity_value or ""))
            elif operator == "in":
                results.append(entity_value in value)
            else:
                results.append(True)

        if logic == "AND":
            return all(results)
        else:  # OR
            return any(results)

    def _create_workflow_instance(
        self,
        db: Session,
        *,
        trigger: WorkflowTrigger,
        entity_type: str,
        entity_id: int,
        entity_data: Dict[str, Any],
        initiated_by: int,
    ) -> WorkflowInstance:
        """Create a new workflow instance from a trigger"""
        instance = WorkflowInstance(
            template_id=trigger.workflow_template_id,
            initiated_by=initiated_by,
            status=WorkflowStatus.PENDING_APPROVAL,
            current_step=1,
            started_at=date.today(),
            data={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "entity_data": entity_data,
                "trigger_id": trigger.id,
                "triggered_at": datetime.utcnow().isoformat(),
            },
        )

        db.add(instance)
        db.commit()
        db.refresh(instance)

        # Update trigger last_triggered_at
        trigger.last_triggered_at = datetime.utcnow()
        db.commit()

        logger.info(
            f"Created workflow instance {instance.id} for {entity_type} {entity_id}"
        )
        return instance

    def _log_trigger_execution(
        self,
        db: Session,
        *,
        trigger: WorkflowTrigger,
        workflow_instance: WorkflowInstance,
        entity_data: Dict[str, Any],
    ) -> TriggerExecution:
        """Log the trigger execution"""
        execution = TriggerExecution(
            trigger_id=trigger.id,
            workflow_instance_id=workflow_instance.id,
            triggered_at=datetime.utcnow(),
            trigger_data=entity_data,
            status="success",
            workflow_created=True,
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)
        return execution

    def complete_entity_workflow(
        self,
        db: Session,
        *,
        workflow_instance_id: int,
        approved: bool,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Complete a workflow and return entity update info.

        Returns dict with entity_type, entity_id, and new_status to update.
        """
        instance = (
            db.query(WorkflowInstance)
            .filter(WorkflowInstance.id == workflow_instance_id)
            .first()
        )

        if not instance or not instance.data:
            return None

        # Update workflow status
        instance.status = WorkflowStatus.APPROVED if approved else WorkflowStatus.REJECTED
        instance.completed_at = date.today()
        if notes:
            instance.notes = notes
        db.commit()

        # Return entity info for caller to update
        return {
            "entity_type": instance.data.get("entity_type"),
            "entity_id": instance.data.get("entity_id"),
            "approved": approved,
        }

    def get_pending_approvals(
        self,
        db: Session,
        *,
        entity_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[WorkflowInstance]:
        """Get pending workflow instances optionally filtered by entity type"""
        query = db.query(WorkflowInstance).filter(
            WorkflowInstance.status == WorkflowStatus.PENDING_APPROVAL
        )

        if entity_type:
            query = query.filter(
                WorkflowInstance.data["entity_type"].astext == entity_type
            )

        return query.order_by(WorkflowInstance.created_at.desc()).offset(skip).limit(limit).all()

    def get_entity_workflow(
        self,
        db: Session,
        *,
        entity_type: str,
        entity_id: int,
    ) -> Optional[WorkflowInstance]:
        """Get workflow instance for a specific entity"""
        return (
            db.query(WorkflowInstance)
            .filter(
                WorkflowInstance.data["entity_type"].astext == entity_type,
                WorkflowInstance.data["entity_id"].astext == str(entity_id),
            )
            .order_by(WorkflowInstance.created_at.desc())
            .first()
        )


event_trigger_service = EventTriggerService()
