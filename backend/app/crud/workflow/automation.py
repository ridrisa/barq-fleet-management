from app.crud.base import CRUDBase
from app.models.workflow.automation import (
    WorkflowAutomation,
    AutomationExecutionLog,
)
from app.schemas.workflow.automation import (
    WorkflowAutomationCreate,
    WorkflowAutomationUpdate,
    AutomationExecutionLogCreate,
    AutomationExecutionLogUpdate,
)

workflow_automation = CRUDBase[
    WorkflowAutomation, WorkflowAutomationCreate, WorkflowAutomationUpdate
](WorkflowAutomation)
automation_execution_log = CRUDBase[
    AutomationExecutionLog, AutomationExecutionLogCreate, AutomationExecutionLogUpdate
](AutomationExecutionLog)
