from fastapi import APIRouter
from app.api.v1.operations import delivery, route, cod, incident, document

router = APIRouter()

router.include_router(delivery.router, prefix="/deliveries", tags=["Deliveries"])
router.include_router(route.router, prefix="/routes", tags=["Routes"])
router.include_router(cod.router, prefix="/cod", tags=["COD"])
router.include_router(incident.router, prefix="/incidents", tags=["Incidents"])
router.include_router(document.router, prefix="/documents", tags=["Operations Documents"])

__all__ = ["router"]
