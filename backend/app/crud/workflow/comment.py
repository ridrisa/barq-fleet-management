from app.crud.base import CRUDBase
from app.models.workflow.comment import WorkflowComment
from app.schemas.workflow.comment import WorkflowCommentCreate, WorkflowCommentUpdate

workflow_comment = CRUDBase[WorkflowComment, WorkflowCommentCreate, WorkflowCommentUpdate](WorkflowComment)
