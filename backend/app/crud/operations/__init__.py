from app.crud.operations.cod import cod
from app.crud.operations.delivery import delivery
from app.crud.operations.route import route
from app.crud.operations.incident import incident
from app.crud.operations.zone import zone
from app.crud.operations.handover import handover
from app.crud.operations.quality import quality_metric, quality_inspection
from app.crud.operations.sla import sla_definition, sla_tracking
from app.crud.operations.dispatch import dispatch_assignment
from app.crud.operations.priority_queue import priority_queue_entry

__all__ = [
    "cod",
    "delivery",
    "route",
    "incident",
    "zone",
    "handover",
    "quality_metric",
    "quality_inspection",
    "sla_definition",
    "sla_tracking",
    "dispatch_assignment",
    "priority_queue_entry",
]
