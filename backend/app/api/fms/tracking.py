"""
FMS Tracking API Routes
Provides endpoints for real-time tracking and streaming from machinettalk.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import asyncio
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.fms import get_fms_client

router = APIRouter()


@router.get("/status")
async def get_fms_status(
    current_user: User = Depends(get_current_user),
):
    """
    Get FMS system status.
    Returns connectivity and system health information.
    """
    client = get_fms_client()
    result = client.get_status()

    if result.get("error"):
        return {
            "status": "disconnected",
            "message": result.get("message", "FMS unavailable"),
            "fms_url": client.base_url
        }

    return {
        "status": "connected",
        "fms_status": result,
        "fms_url": client.base_url
    }


@router.get("/health")
async def get_fms_health(
    current_user: User = Depends(get_current_user),
):
    """
    Get FMS health check.
    """
    client = get_fms_client()
    result = client.get_health()

    if result.get("error"):
        return {
            "healthy": False,
            "message": result.get("message", "FMS unavailable")
        }

    return {
        "healthy": True,
        "details": result
    }


@router.get("/stream-url")
async def get_stream_url(
    current_user: User = Depends(get_current_user),
):
    """
    Get the SSE stream URL for real-time vehicle updates.
    Frontend can use this URL to establish an EventSource connection.
    """
    client = get_fms_client()
    return {
        "stream_url": client.get_stream_url(),
        "type": "server-sent-events",
        "description": "Real-time vehicle position updates"
    }


@router.get("/live")
async def stream_live_data(
    current_user: User = Depends(get_current_user),
):
    """
    Proxy SSE stream from FMS.
    Streams real-time vehicle position updates.
    """
    client = get_fms_client()
    stream_url = client.get_stream_url()

    async def event_generator():
        async with httpx.AsyncClient() as http_client:
            try:
                async with http_client.stream("GET", stream_url, timeout=None) as response:
                    async for line in response.aiter_lines():
                        if line:
                            yield f"{line}\n"
            except Exception as e:
                yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/summary")
async def get_fleet_summary(
    current_user: User = Depends(get_current_user),
):
    """
    Get a summary of fleet tracking status.
    Returns counts of active, idle, and offline vehicles.
    """
    client = get_fms_client()
    result = client.get_assets(page_size=500, page_index=1)  # FMS uses 1-based pagination

    if result.get("error"):
        raise HTTPException(
            status_code=502,
            detail=result.get("message", "FMS service unavailable")
        )

    # Handle null/empty result
    assets = result.get("result") or []
    if not isinstance(assets, list):
        assets = []

    # Categorize assets by status
    summary = {
        "total": len(assets),
        "active": 0,
        "idle": 0,
        "offline": 0,
        "moving": 0,
        "stationary": 0,
        "unknown": 0
    }

    speed_threshold = 5  # km/h - consider vehicle moving if speed > this

    def safe_float(val, default=0.0):
        """Safely convert value to float."""
        if val is None:
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    for asset in assets:
        status = (asset.get("AssetLastStatus") or "").lower()
        tracking = asset.get("Trackingunit") or {}
        device_log = tracking.get("DeviceLog") or {}
        speed = safe_float(device_log.get("Speed"), 0)

        # Categorize by connection status
        if "offline" in status or "disconnected" in status:
            summary["offline"] += 1
        elif "idle" in status or "parked" in status:
            summary["idle"] += 1
        else:
            summary["active"] += 1

        # Categorize by movement
        if speed > speed_threshold:
            summary["moving"] += 1
        elif device_log.get("Latitude"):
            summary["stationary"] += 1
        else:
            summary["unknown"] += 1

    # Calculate average speed of moving vehicles
    moving_speeds = []
    for asset in assets:
        tracking = asset.get("Trackingunit") or {}
        device_log = tracking.get("DeviceLog") or {}
        speed = safe_float(device_log.get("Speed"), 0)
        if speed > speed_threshold:
            moving_speeds.append(speed)

    summary["avg_speed_kmh"] = round(sum(moving_speeds) / len(moving_speeds), 1) if moving_speeds else 0

    return summary


@router.get("/vehicles/{vehicle_id}/current")
async def get_vehicle_current_position(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
):
    """
    Get the current position and status of a specific vehicle.
    Returns real-time GPS data, speed, and driver info.
    """
    client = get_fms_client()
    result = client.get_asset_by_id(vehicle_id)

    if result.get("error"):
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found or FMS unavailable"
        )

    # Extract relevant tracking data
    tracking = result.get("Trackingunit", {})
    device_log = tracking.get("DeviceLog", {})
    driver = tracking.get("Driver", {})

    return {
        "vehicle_id": result.get("Id"),
        "name": result.get("AssetName"),
        "name_ar": result.get("AssetNameAr"),
        "plate_number": result.get("PlateNumber"),
        "status": result.get("AssetLastStatus"),
        "position": {
            "latitude": device_log.get("Latitude"),
            "longitude": device_log.get("Longitude"),
            "altitude": device_log.get("Altitude"),
            "direction": device_log.get("Direction"),
            "timestamp": device_log.get("GPSDate")
        },
        "speed": {
            "current_kmh": device_log.get("Speed"),
            "mileage_km": device_log.get("Mileage")
        },
        "signal_strength": device_log.get("SignalStrength"),
        "driver": {
            "id": driver.get("DriverId"),
            "name": driver.get("DriverName"),
            "badge": driver.get("BadgeNumber"),
            "license": driver.get("LicenseNumber"),
            "contact": driver.get("ContactNumber")
        } if driver else None
    }
