from app.crud.base import CRUDBase
from app.models.workflow.history import WorkflowHistory, WorkflowStepHistory
from app.schemas.workflow.history import (
    WorkflowHistoryCreate,
    WorkflowStepHistoryCreate,
)

workflow_history = CRUDBase[WorkflowHistory, WorkflowHistoryCreate, dict](WorkflowHistory)
workflow_step_history = CRUDBase[WorkflowStepHistory, WorkflowStepHistoryCreate, dict](
    WorkflowStepHistory
)
