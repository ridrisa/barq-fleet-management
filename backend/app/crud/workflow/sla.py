from app.crud.base import CRUDBase
from app.models.workflow.sla import WorkflowSLA, WorkflowSLAInstance, SLAEvent
from app.schemas.workflow.sla import (
    WorkflowSLACreate,
    WorkflowSLAUpdate,
    WorkflowSLAInstanceCreate,
    WorkflowSLAInstanceUpdate,
    SLAEventCreate,
)

workflow_sla = CRUDBase[WorkflowSLA, WorkflowSLACreate, WorkflowSLAUpdate](WorkflowSLA)
workflow_sla_instance = CRUDBase[
    WorkflowSLAInstance, WorkflowSLAInstanceCreate, WorkflowSLAInstanceUpdate
](WorkflowSLAInstance)
sla_event = CRUDBase[SLAEvent, SLAEventCreate, dict](SLAEvent)
