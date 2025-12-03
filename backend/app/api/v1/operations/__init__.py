"""Operations API Routes"""

from fastapi import APIRouter

from app.api.v1.operations import (
    cod,
    delivery,
    dispatch,
    document,
    feedback,
    handovers,
    incidents,
    priority_queue,
    quality,
    routes,
    settings,
    sla,
    zones,
)

router = APIRouter()

# Existing routes
router.include_router(delivery.router, prefix="/deliveries", tags=["Deliveries"])
router.include_router(cod.router, prefix="/cod", tags=["COD"])

# Comprehensive routes (plural naming)
router.include_router(routes.router, prefix="/routes", tags=["Operations-Routes"])
router.include_router(incidents.router, prefix="/incidents", tags=["Operations-Incidents"])
router.include_router(handovers.router, prefix="/handovers", tags=["Operations-Handovers"])
router.include_router(zones.router, prefix="/zones", tags=["Operations-Zones"])
router.include_router(dispatch.router, prefix="/dispatch", tags=["Operations-Dispatch"])
router.include_router(
    priority_queue.router, prefix="/priority-queue", tags=["Operations-Priority-Queue"]
)
router.include_router(quality.router, prefix="/quality", tags=["Operations-Quality"])
router.include_router(sla.router, prefix="/sla", tags=["Operations-SLA"])
router.include_router(feedback.router, prefix="/feedback", tags=["Operations-Feedback"])
router.include_router(settings.router, prefix="/settings", tags=["Operations-Settings"])
router.include_router(document.router, prefix="/documents", tags=["Operations-Documents"])

__all__ = ["router"]
