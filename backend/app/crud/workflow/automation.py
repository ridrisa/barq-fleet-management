from app.crud.base import CRUDBase
from app.models.workflow.automation import (
    AutomationExecutionLog,
    WorkflowAutomation,
)
from app.schemas.workflow.automation import (
    AutomationExecutionLogCreate,
    AutomationExecutionLogUpdate,
    WorkflowAutomationCreate,
    WorkflowAutomationUpdate,
)

workflow_automation = CRUDBase[
    WorkflowAutomation, WorkflowAutomationCreate, WorkflowAutomationUpdate
](WorkflowAutomation)
automation_execution_log = CRUDBase[
    AutomationExecutionLog, AutomationExecutionLogCreate, AutomationExecutionLogUpdate
](AutomationExecutionLog)
