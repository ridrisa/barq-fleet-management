"""Workflow Services Package"""
from app.services.workflow.template_service import TemplateService, template_service
from app.services.workflow.instance_service import InstanceService, instance_service
from app.services.workflow.event_trigger_service import EventTriggerService, event_trigger_service

__all__ = [
    # Service classes
    "TemplateService",
    "InstanceService",
    "EventTriggerService",
    # Service instances
    "template_service",
    "instance_service",
    "event_trigger_service",
]
