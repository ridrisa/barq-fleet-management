"""Operations Services"""

from app.services.operations.cod_service import cod_service
from app.services.operations.delivery_service import delivery_service
from app.services.operations.dispatch_assignment_service import dispatch_assignment_service
from app.services.operations.feedback_service import (
    customer_feedback_service,
    feedback_template_service,
)
from app.services.operations.handover_service import handover_service
from app.services.operations.incident_service import incident_service
from app.services.operations.operations_document_service import operations_document_service
from app.services.operations.quality_service import (
    quality_inspection_service,
    quality_metric_service,
)
from app.services.operations.route_service import route_service
from app.services.operations.settings_service import (
    dispatch_rule_service,
    notification_setting_service,
    operations_settings_service,
    sla_threshold_service,
    zone_default_service,
)
from app.services.operations.sla_service import sla_definition_service, sla_tracking_service
from app.services.operations.zone_service import zone_service
from app.services.operations.priority_queue_service import priority_queue_service

__all__ = [
    # Core operations
    "delivery_service",
    "route_service",
    "cod_service",
    "incident_service",
    # Dispatch
    "dispatch_assignment_service",
    # Handover
    "handover_service",
    # Zone
    "zone_service",
    # SLA
    "sla_definition_service",
    "sla_tracking_service",
    # Quality
    "quality_metric_service",
    "quality_inspection_service",
    # Feedback
    "customer_feedback_service",
    "feedback_template_service",
    # Settings
    "operations_settings_service",
    "dispatch_rule_service",
    "sla_threshold_service",
    "notification_setting_service",
    "zone_default_service",
    # Documents
    "operations_document_service",
    # Priority Queue
    "priority_queue_service",
]
