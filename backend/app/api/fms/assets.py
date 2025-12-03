"""
FMS Assets API Routes
Provides endpoints for vehicle/asset tracking data from machinettalk.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.fms import get_fms_client

router = APIRouter()


@router.get("/")
async def get_assets(
    page_size: int = Query(100, ge=1, le=500, description="Items per page"),
    page_index: int = Query(1, ge=1, description="Page index (1-based)"),
    current_user: User = Depends(get_current_user),
):
    """
    Get all tracked vehicles/assets from FMS.
    Returns real-time GPS data including location, speed, and status.
    """
    client = get_fms_client()
    result = client.get_assets(page_size=page_size, page_index=page_index)

    if result.get("error"):
        raise HTTPException(
            status_code=502, detail=result.get("message", "FMS service unavailable")
        )

    return result


@router.get("/{asset_id}")
async def get_asset_by_id(
    asset_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Get vehicle/asset details by ID.
    Includes current GPS position, driver info, and device status.
    """
    client = get_fms_client()
    result = client.get_asset_by_id(asset_id)

    if result.get("error"):
        raise HTTPException(
            status_code=502 if "unavailable" in str(result.get("message", "")).lower() else 404,
            detail=result.get("message", "Asset not found"),
        )

    return result


@router.get("/plate/{plate_number}")
async def get_asset_by_plate(
    plate_number: str,
    current_user: User = Depends(get_current_user),
):
    """
    Get vehicle/asset by plate number.
    Useful for looking up vehicles by their license plate.
    """
    client = get_fms_client()
    result = client.get_asset_by_plate(plate_number)

    if result.get("error"):
        raise HTTPException(
            status_code=502 if "unavailable" in str(result.get("message", "")).lower() else 404,
            detail=result.get("message", "Asset not found"),
        )

    return result


@router.get("/{asset_id}/history")
async def get_location_history(
    asset_id: int,
    from_time: str = Query(..., description="Start time (ISO format or MMddYYYY HH:mm:ss)"),
    to_time: str = Query(..., description="End time (ISO format or MMddYYYY HH:mm:ss)"),
    current_user: User = Depends(get_current_user),
):
    """
    Get location history for a vehicle.
    Returns GPS track points within the specified time range (max 24 hours).
    """
    client = get_fms_client()
    result = client.get_location_history(asset_id, from_time, to_time)

    if result.get("error"):
        raise HTTPException(
            status_code=502, detail=result.get("message", "Failed to get location history")
        )

    return result


@router.get("/search/nearby")
async def search_nearby_assets(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(5, ge=0.1, le=100, description="Search radius in kilometers"),
    current_user: User = Depends(get_current_user),
):
    """
    Find vehicles near a specific location.
    Returns assets within the specified radius, sorted by distance.
    """
    import math

    client = get_fms_client()
    result = client.get_assets(page_size=500, page_index=1)

    if result.get("error"):
        raise HTTPException(status_code=502, detail="FMS service unavailable")

    assets = result.get("result", [])
    nearby = []

    for asset in assets:
        tracking = asset.get("Trackingunit", {})
        device_log = tracking.get("DeviceLog", {})
        asset_lat = device_log.get("Latitude")
        asset_lng = device_log.get("Longitude")

        if asset_lat and asset_lng:
            # Haversine formula for distance
            R = 6371  # Earth radius in km
            lat1, lat2 = math.radians(latitude), math.radians(asset_lat)
            dlat = math.radians(asset_lat - latitude)
            dlng = math.radians(asset_lng - longitude)

            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c

            if distance <= radius_km:
                nearby.append({**asset, "distance_km": round(distance, 2)})

    # Sort by distance
    nearby.sort(key=lambda x: x.get("distance_km", float("inf")))

    return {
        "result": nearby,
        "totalCount": len(nearby),
        "center": {"latitude": latitude, "longitude": longitude},
        "radius_km": radius_km,
    }
