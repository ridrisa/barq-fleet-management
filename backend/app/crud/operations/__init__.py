"""
Operations CRUD
"""

from app.crud.operations.cod import cod
from app.crud.operations.delivery import delivery
from app.crud.operations.dispatch import dispatch_assignment
from app.crud.operations.document import operations_document
from app.crud.operations.feedback import customer_feedback, feedback_template
from app.crud.operations.handover import handover
from app.crud.operations.incident import incident
from app.crud.operations.priority_queue import priority_queue_entry
from app.crud.operations.quality import quality_inspection, quality_metric
from app.crud.operations.route import route
from app.crud.operations.settings import (
    dispatch_rule,
    notification_setting,
    operations_settings,
    sla_threshold,
    zone_default,
)
from app.crud.operations.sla import sla_definition, sla_tracking
from app.crud.operations.zone import zone

__all__ = [
    # COD
    "cod",
    # Delivery
    "delivery",
    # Route
    "route",
    # Incident
    "incident",
    # Zone
    "zone",
    # Handover
    "handover",
    # Quality
    "quality_metric",
    "quality_inspection",
    # SLA
    "sla_definition",
    "sla_tracking",
    # Dispatch
    "dispatch_assignment",
    # Priority Queue
    "priority_queue_entry",
    # Feedback
    "customer_feedback",
    "feedback_template",
    # Settings
    "operations_settings",
    "dispatch_rule",
    "sla_threshold",
    "notification_setting",
    "zone_default",
    # Document
    "operations_document",
]
