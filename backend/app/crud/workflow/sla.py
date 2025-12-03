from app.crud.base import CRUDBase
from app.models.workflow.sla import SLAEvent, WorkflowSLA, WorkflowSLAInstance
from app.schemas.workflow.sla import (
    SLAEventCreate,
    WorkflowSLACreate,
    WorkflowSLAInstanceCreate,
    WorkflowSLAInstanceUpdate,
    WorkflowSLAUpdate,
)

workflow_sla = CRUDBase[WorkflowSLA, WorkflowSLACreate, WorkflowSLAUpdate](WorkflowSLA)
workflow_sla_instance = CRUDBase[
    WorkflowSLAInstance, WorkflowSLAInstanceCreate, WorkflowSLAInstanceUpdate
](WorkflowSLAInstance)
sla_event = CRUDBase[SLAEvent, SLAEventCreate, dict](SLAEvent)
