from app.crud.base import CRUDBase
from app.models.workflow.template import WorkflowTemplate
from app.schemas.workflow.template import WorkflowTemplateCreate, WorkflowTemplateUpdate

workflow_template = CRUDBase[WorkflowTemplate, WorkflowTemplateCreate, WorkflowTemplateUpdate](WorkflowTemplate)
