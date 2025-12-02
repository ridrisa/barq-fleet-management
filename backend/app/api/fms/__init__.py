"""
FMS API Routes
Provides proxy endpoints to machinettalk FMS for GPS tracking and fleet monitoring.
"""
from fastapi import APIRouter
from app.api.fms import assets, geofences, placemarks, tracking, sync

router = APIRouter()

router.include_router(assets.router, prefix="/assets", tags=["FMS Assets"])
router.include_router(geofences.router, prefix="/geofences", tags=["FMS Geofences"])
router.include_router(placemarks.router, prefix="/placemarks", tags=["FMS Placemarks"])
router.include_router(tracking.router, prefix="/tracking", tags=["FMS Tracking"])
router.include_router(sync.router, prefix="/sync", tags=["FMS Sync"])

__all__ = ["router"]
