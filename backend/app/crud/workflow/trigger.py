from app.crud.base import CRUDBase
from app.models.workflow.trigger import WorkflowTrigger, TriggerExecution
from app.schemas.workflow.trigger import (
    WorkflowTriggerCreate,
    WorkflowTriggerUpdate,
    TriggerExecutionCreate,
)

workflow_trigger = CRUDBase[
    WorkflowTrigger, WorkflowTriggerCreate, WorkflowTriggerUpdate
](WorkflowTrigger)
trigger_execution = CRUDBase[TriggerExecution, TriggerExecutionCreate, dict](
    TriggerExecution
)
