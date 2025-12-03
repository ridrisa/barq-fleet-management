"""
Operations Models
"""

from app.models.operations.cod import COD, CODStatus
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.models.operations.dispatch import DispatchAssignment, DispatchPriority, DispatchStatus
from app.models.operations.document import DocumentCategory, OperationsDocument
from app.models.operations.feedback import (
    CustomerFeedback,
    FeedbackSentiment,
    FeedbackStatus,
    FeedbackTemplate,
    FeedbackType,
)
from app.models.operations.handover import Handover, HandoverStatus, HandoverType
from app.models.operations.incident import Incident, IncidentStatus, IncidentType
from app.models.operations.priority_queue import PriorityQueueEntry, QueuePriority, QueueStatus
from app.models.operations.quality import (
    InspectionStatus,
    QualityInspection,
    QualityMetric,
    QualityMetricType,
)
from app.models.operations.route import Route, RouteStatus
from app.models.operations.settings import (
    DispatchRule,
    NotificationSetting,
    OperationsSettings,
    SLAThreshold,
    ZoneDefault,
)
from app.models.operations.sla import SLADefinition, SLAPriority, SLAStatus, SLATracking, SLAType
from app.models.operations.zone import Zone, ZoneStatus

__all__ = [
    # COD
    "COD",
    "CODStatus",
    # Delivery
    "Delivery",
    "DeliveryStatus",
    # Route
    "Route",
    "RouteStatus",
    # Incident
    "Incident",
    "IncidentType",
    "IncidentStatus",
    # Zone
    "Zone",
    "ZoneStatus",
    # Handover
    "Handover",
    "HandoverStatus",
    "HandoverType",
    # Quality
    "QualityMetric",
    "QualityInspection",
    "QualityMetricType",
    "InspectionStatus",
    # SLA
    "SLADefinition",
    "SLATracking",
    "SLAType",
    "SLAPriority",
    "SLAStatus",
    # Dispatch
    "DispatchAssignment",
    "DispatchStatus",
    "DispatchPriority",
    # Priority Queue
    "PriorityQueueEntry",
    "QueuePriority",
    "QueueStatus",
    # Feedback
    "CustomerFeedback",
    "FeedbackTemplate",
    "FeedbackType",
    "FeedbackStatus",
    "FeedbackSentiment",
    # Settings
    "OperationsSettings",
    "DispatchRule",
    "SLAThreshold",
    "NotificationSetting",
    "ZoneDefault",
    # Document
    "OperationsDocument",
    "DocumentCategory",
]
