"""Workflow Services Package"""

from app.services.workflow.approval_service import WorkflowApprovalService
from app.services.workflow.event_trigger_service import EventTriggerService, event_trigger_service
from app.services.workflow.execution_service import WorkflowExecutionService
from app.services.workflow.instance_service import InstanceService, instance_service
from app.services.workflow.template_service import TemplateService, template_service

__all__ = [
    # Service classes
    "TemplateService",
    "InstanceService",
    "EventTriggerService",
    "WorkflowApprovalService",
    "WorkflowExecutionService",
    # Service instances
    "template_service",
    "instance_service",
    "event_trigger_service",
]
