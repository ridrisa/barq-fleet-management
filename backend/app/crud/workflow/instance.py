from app.crud.base import CRUDBase
from app.models.workflow.instance import WorkflowInstance
from app.schemas.workflow.instance import WorkflowInstanceCreate, WorkflowInstanceUpdate

workflow_instance = CRUDBase[WorkflowInstance, WorkflowInstanceCreate, WorkflowInstanceUpdate](
    WorkflowInstance
)
