"""
FMS Geofences API Routes
Provides endpoints for geofence/zone management from machinettalk.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.deps import get_current_user
from app.models.user import User
from app.services.fms import get_fms_client

router = APIRouter()


@router.get("/")
async def get_geofences(
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    page_index: int = Query(0, ge=0, description="Page index"),
    current_user: User = Depends(get_current_user),
):
    """
    Get all geofences/zones.
    Returns zone boundaries, speed limits, and metadata.
    """
    client = get_fms_client()
    result = client.get_geofences(page_size=page_size, page_index=page_index)

    if result.get("error"):
        raise HTTPException(
            status_code=502,
            detail=result.get("message", "FMS service unavailable")
        )

    return result


@router.get("/{zone_id}")
async def get_geofence_by_id(
    zone_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Get geofence details by ID.
    Includes zone boundaries, speed limits, and department info.
    """
    client = get_fms_client()
    result = client.get_geofence_by_id(zone_id)

    if result.get("error"):
        raise HTTPException(
            status_code=502 if "unavailable" in str(result.get("message", "")).lower() else 404,
            detail=result.get("message", "Geofence not found")
        )

    return result
