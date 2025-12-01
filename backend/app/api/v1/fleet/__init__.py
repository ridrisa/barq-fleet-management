"""Fleet Management API routes"""

from fastapi import APIRouter
from app.api.v1.fleet import (
    couriers,
    vehicles,
    assignments,
    vehicle_logs,
    maintenance,
    inspections,
    accident_logs,
)

# Create main fleet router
fleet_router = APIRouter()

# Include all sub-routers
fleet_router.include_router(couriers.router, prefix="/couriers", tags=["fleet-couriers"])
fleet_router.include_router(vehicles.router, prefix="/vehicles", tags=["fleet-vehicles"])
fleet_router.include_router(assignments.router, prefix="/assignments", tags=["fleet-assignments"])
fleet_router.include_router(vehicle_logs.router, prefix="/vehicle-logs", tags=["fleet-vehicle-logs"])
fleet_router.include_router(maintenance.router, prefix="/maintenance", tags=["fleet-maintenance"])
fleet_router.include_router(inspections.router, prefix="/inspections", tags=["fleet-inspections"])
fleet_router.include_router(accident_logs.router, prefix="/accident-logs", tags=["fleet-accident-logs"])

__all__ = ["fleet_router"]
