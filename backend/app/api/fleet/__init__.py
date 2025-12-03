from fastapi import APIRouter

from app.api.fleet import (
    accident_logs,
    assignments,
    courier_performance,
    couriers,
    documents,
    fuel_logs,
    inspections,
    maintenance,
    vehicle_logs,
    vehicles,
)

router = APIRouter()

router.include_router(couriers.router, prefix="/couriers", tags=["couriers"])
router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
router.include_router(inspections.router, prefix="/inspections", tags=["inspections"])
router.include_router(accident_logs.router, prefix="/accident-logs", tags=["accident-logs"])
router.include_router(vehicle_logs.router, prefix="/vehicle-logs", tags=["vehicle-logs"])
router.include_router(fuel_logs.router, prefix="/fuel-logs", tags=["fuel-logs"])
router.include_router(
    courier_performance.router, prefix="/courier-performance", tags=["courier-performance"]
)
router.include_router(documents.router, prefix="/documents", tags=["documents"])

__all__ = ["router"]
