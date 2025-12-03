from fastapi import APIRouter

from app.api.v1.operations import cod, delivery, document, feedback, incidents, routes

router = APIRouter()

router.include_router(delivery.router, prefix="/deliveries", tags=["Deliveries"])
router.include_router(routes.router, prefix="/routes", tags=["Routes"])
router.include_router(cod.router, prefix="/cod", tags=["COD"])
router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
router.include_router(document.router, prefix="/documents", tags=["Operations Documents"])
router.include_router(feedback.router, prefix="/feedback", tags=["Customer Feedback"])

__all__ = ["router"]
