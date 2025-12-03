"""
FMS Sync API Routes
Provides endpoints for syncing FMS data with BARQ database.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.fms.sync import get_sync_service

router = APIRouter()


@router.post("/run")
async def run_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run FMS sync to match assets with BARQ couriers and vehicles.

    This operation:
    1. Fetches all FMS assets
    2. Matches by BARQ ID (FMS PlateNumber) or iqama number (FMS IDNumber)
    3. Links couriers and vehicles to FMS asset IDs
    4. Updates mileage and GPS device info for vehicles
    """
    sync_service = get_sync_service(db)
    result = sync_service.sync_all_assets()

    return {
        "success": True,
        "message": "FMS sync completed",
        "stats": result
    }


@router.get("/preview")
async def preview_sync(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Preview FMS assets and their potential matches without syncing.
    Shows what will be matched when sync is run.
    """
    sync_service = get_sync_service(db)
    assets = sync_service.get_all_fms_assets(max_pages=1)[:limit]

    preview_results = []
    for asset in assets:
        result = {
            "fms_asset_id": asset.get("Id"),
            "asset_name": asset.get("AssetName"),
            "barq_id": asset.get("PlateNumber"),
        }

        # Check potential matches
        courier = sync_service.match_courier_by_barq_id(asset.get("PlateNumber"))
        if not courier:
            tracking_unit = asset.get("Trackingunit", {})
            driver = tracking_unit.get("Driver", {})
            if driver.get("IDNumber"):
                courier = sync_service.match_courier_by_iqama(driver.get("IDNumber"))

        if courier:
            result["courier_match"] = {
                "id": courier.id,
                "name": courier.full_name,
                "barq_id": courier.barq_id,
                "already_linked": courier.fms_asset_id == asset.get("Id")
            }

        vehicle = sync_service.match_vehicle_by_plate(asset.get("AssetName"))
        if vehicle:
            result["vehicle_match"] = {
                "id": vehicle.id,
                "plate_number": vehicle.plate_number,
                "already_linked": vehicle.fms_asset_id == asset.get("Id")
            }

        preview_results.append(result)

    return {
        "total_fms_assets": len(assets),
        "preview": preview_results
    }


@router.get("/live-locations")
async def get_live_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get real-time locations for all couriers/assets.

    Returns position data including:
    - GPS coordinates (lat/lng)
    - Speed
    - Direction
    - Driver info
    """
    sync_service = get_sync_service(db)
    locations = sync_service.get_all_couriers_live_locations()

    return {
        "count": len(locations),
        "locations": locations
    }


@router.get("/courier/{courier_id}/location")
async def get_courier_location(
    courier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get real-time location for a specific courier.
    """
    sync_service = get_sync_service(db)
    location = sync_service.get_courier_live_location(courier_id)

    if not location:
        raise HTTPException(
            status_code=404,
            detail="Courier not found or not linked to FMS"
        )

    return location


@router.get("/stats")
async def get_sync_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get synchronization statistics.
    Shows how many couriers and vehicles are linked to FMS.
    """
    from app.models.fleet.courier import Courier
    from app.models.fleet.vehicle import Vehicle

    total_couriers = db.query(Courier).count()
    linked_couriers = db.query(Courier).filter(Courier.fms_asset_id.isnot(None)).count()

    total_vehicles = db.query(Vehicle).count()
    linked_vehicles = db.query(Vehicle).filter(Vehicle.fms_asset_id.isnot(None)).count()

    sync_service = get_sync_service(db)
    fms_assets = sync_service.get_all_fms_assets(max_pages=1)

    return {
        "couriers": {
            "total": total_couriers,
            "linked_to_fms": linked_couriers,
            "unlinked": total_couriers - linked_couriers,
            "link_percentage": round((linked_couriers / total_couriers * 100) if total_couriers > 0 else 0, 1)
        },
        "vehicles": {
            "total": total_vehicles,
            "linked_to_fms": linked_vehicles,
            "unlinked": total_vehicles - linked_vehicles,
            "link_percentage": round((linked_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0, 1)
        },
        "fms": {
            "total_assets": len(fms_assets) if fms_assets else 0
        }
    }
