from app.crud.base import CRUDBase
from app.models.workflow.attachment import WorkflowAttachment
from app.schemas.workflow.attachment import WorkflowAttachmentCreate, WorkflowAttachmentUpdate

workflow_attachment = CRUDBase[
    WorkflowAttachment, WorkflowAttachmentCreate, WorkflowAttachmentUpdate
](WorkflowAttachment)
