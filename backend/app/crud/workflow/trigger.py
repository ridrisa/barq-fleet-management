from app.crud.base import CRUDBase
from app.models.workflow.trigger import TriggerExecution, WorkflowTrigger
from app.schemas.workflow.trigger import (
    TriggerExecutionCreate,
    WorkflowTriggerCreate,
    WorkflowTriggerUpdate,
)

workflow_trigger = CRUDBase[WorkflowTrigger, WorkflowTriggerCreate, WorkflowTriggerUpdate](
    WorkflowTrigger
)
trigger_execution = CRUDBase[TriggerExecution, TriggerExecutionCreate, dict](TriggerExecution)
