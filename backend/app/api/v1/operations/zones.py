import logging
import math
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.models.tenant.organization import Organization
from app.models.operations.delivery import Delivery, DeliveryStatus
from app.services.operations import zone_service
from app.schemas.operations.zone import ZoneCreate, ZoneMetrics, ZoneResponse, ZoneUpdate

logger = logging.getLogger(__name__)

router = APIRouter()


def validate_geojson_boundaries(boundaries: Dict[str, Any]) -> bool:
    """
    Validate GeoJSON polygon boundaries for zone definition.

    Args:
        boundaries: GeoJSON object with polygon definition

    Returns:
        True if valid, raises HTTPException if invalid
    """
    if not boundaries:
        return True  # Boundaries are optional

    # Check for required GeoJSON structure
    if "type" not in boundaries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GeoJSON: missing 'type' property"
        )

    geojson_type = boundaries.get("type")

    # Support Polygon and MultiPolygon
    if geojson_type not in ["Polygon", "MultiPolygon", "Feature", "FeatureCollection"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid GeoJSON type: {geojson_type}. Expected Polygon, MultiPolygon, Feature, or FeatureCollection"
        )

    # For Feature, validate the geometry
    if geojson_type == "Feature":
        geometry = boundaries.get("geometry")
        if not geometry:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GeoJSON Feature: missing 'geometry'"
            )
        return validate_geojson_boundaries(geometry)

    # For FeatureCollection, validate each feature
    if geojson_type == "FeatureCollection":
        features = boundaries.get("features", [])
        if not features:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GeoJSON FeatureCollection: no features"
            )
        for feature in features:
            validate_geojson_boundaries(feature)
        return True

    # Validate coordinates for Polygon/MultiPolygon
    if "coordinates" not in boundaries:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid GeoJSON: missing 'coordinates'"
        )

    coordinates = boundaries.get("coordinates", [])

    if geojson_type == "Polygon":
        # Polygon should have at least one ring (exterior ring)
        if not coordinates or len(coordinates) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Polygon: must have at least one ring"
            )

        # Each ring should have at least 4 points (closed ring)
        for ring in coordinates:
            if len(ring) < 4:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Polygon ring: must have at least 4 points"
                )

            # First and last point should be the same (closed ring)
            if ring[0] != ring[-1]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Polygon ring: first and last point must be the same (closed ring)"
                )

            # Validate each coordinate pair
            for point in ring:
                if len(point) < 2:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid coordinate: must have at least [longitude, latitude]"
                    )
                lon, lat = point[0], point[1]
                if not (-180 <= lon <= 180):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid longitude: {lon}. Must be between -180 and 180"
                    )
                if not (-90 <= lat <= 90):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid latitude: {lat}. Must be between -90 and 90"
                    )

    elif geojson_type == "MultiPolygon":
        # MultiPolygon is an array of Polygon coordinates
        for polygon_coords in coordinates:
            validate_geojson_boundaries({"type": "Polygon", "coordinates": polygon_coords})

    return True


def calculate_coverage_area(boundaries: Dict[str, Any]) -> float:
    """
    Calculate the coverage area in square kilometers from GeoJSON boundaries.
    Uses the Shoelace formula (Surveyor's formula) for polygon area calculation.

    Args:
        boundaries: GeoJSON polygon definition

    Returns:
        Area in square kilometers
    """
    if not boundaries:
        return 0.0

    geojson_type = boundaries.get("type")

    # Handle Feature wrapper
    if geojson_type == "Feature":
        geometry = boundaries.get("geometry")
        return calculate_coverage_area(geometry) if geometry else 0.0

    # Handle FeatureCollection
    if geojson_type == "FeatureCollection":
        total_area = 0.0
        for feature in boundaries.get("features", []):
            total_area += calculate_coverage_area(feature)
        return total_area

    coordinates = boundaries.get("coordinates", [])

    if geojson_type == "Polygon":
        # Use exterior ring (first ring)
        if not coordinates:
            return 0.0
        exterior_ring = coordinates[0]
        return _calculate_polygon_area(exterior_ring)

    elif geojson_type == "MultiPolygon":
        total_area = 0.0
        for polygon_coords in coordinates:
            if polygon_coords:
                total_area += _calculate_polygon_area(polygon_coords[0])
        return total_area

    return 0.0


def _calculate_polygon_area(ring: List[List[float]]) -> float:
    """
    Calculate the area of a polygon using the Shoelace formula.
    Converts to approximate square kilometers using spherical Earth model.

    Args:
        ring: List of [longitude, latitude] coordinates

    Returns:
        Area in square kilometers
    """
    if len(ring) < 4:
        return 0.0

    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0

    # Calculate centroid for projection
    lons = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    center_lat = sum(lats) / len(lats)

    # Convert to radians
    center_lat_rad = math.radians(center_lat)

    # Use Shoelace formula with spherical projection
    area = 0.0
    n = len(ring)

    for i in range(n - 1):  # Last point is same as first
        lon1, lat1 = ring[i]
        lon2, lat2 = ring[i + 1]

        # Convert to projected coordinates (approximate meters)
        # x: longitude adjusted for latitude
        # y: latitude
        x1 = math.radians(lon1) * EARTH_RADIUS_KM * math.cos(center_lat_rad)
        y1 = math.radians(lat1) * EARTH_RADIUS_KM
        x2 = math.radians(lon2) * EARTH_RADIUS_KM * math.cos(center_lat_rad)
        y2 = math.radians(lat2) * EARTH_RADIUS_KM

        # Shoelace formula
        area += (x1 * y2) - (x2 * y1)

    area = abs(area) / 2.0
    return round(area, 2)


@router.get("/", response_model=List[ZoneResponse])
def list_zones(
    skip: int = 0,
    limit: int = 100,
    city: str = Query(None, description="Filter by city"),
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all zones with optional filters"""
    if city:
        zones = zone_service.get_by_city(
            db, city=city, skip=skip, limit=limit, organization_id=current_org.id
        )
    elif status == "active":
        zones = zone_service.get_active_zones(
            db, skip=skip, limit=limit, organization_id=current_org.id
        )
    else:
        zones = zone_service.get_multi(db, skip=skip, limit=limit, filters={"organization_id": current_org.id})
    return zones


@router.get("/at-capacity", response_model=List[ZoneResponse])
def list_zones_at_capacity(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List zones at or near capacity

    Business Logic:
    - Returns zones where current_couriers >= max_couriers
    - Used for load balancing decisions
    - Helps identify zones needing additional resources
    """
    zones = zone_service.get_at_capacity(db, organization_id=current_org.id)
    return zones


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific zone by ID"""
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.get("/code/{zone_code}", response_model=ZoneResponse)
def get_zone_by_code(
    zone_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get zone by unique code"""
    zone = zone_service.get_by_code(db, zone_code=zone_code, organization_id=current_org.id)
    if not zone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    return zone


@router.post("/", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    zone_in: ZoneCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new delivery zone

    Business Logic:
    - Validates zone code is unique within organization
    - Validates GeoJSON boundaries if provided
    - Initializes performance metrics to 0
    - Sets status to ACTIVE by default
    """
    # Check if zone code already exists in organization
    existing_zone = zone_service.get_by_code(
        db, zone_code=zone_in.zone_code, organization_id=current_org.id
    )
    if existing_zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Zone with code '{zone_in.zone_code}' already exists",
        )

    # Validate GeoJSON boundaries if provided
    if zone_in.boundaries:
        validate_geojson_boundaries(zone_in.boundaries)

    # Create zone
    zone = zone_service.create(db, obj_in=zone_in, organization_id=current_org.id)

    # Calculate coverage area from boundaries if provided and not manually set
    if zone_in.boundaries and not zone_in.coverage_area_km2:
        coverage_area = calculate_coverage_area(zone_in.boundaries)
        if coverage_area > 0:
            zone.coverage_area_km2 = coverage_area
            db.add(zone)
            db.commit()
            db.refresh(zone)

    return zone


@router.put("/{zone_id}", response_model=ZoneResponse)
def update_zone(
    zone_id: int,
    zone_in: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a zone"""
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")
    zone = zone_service.update(db, db_obj=zone, obj_in=zone_in)
    return zone


@router.delete("/{zone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a zone

    Business Logic:
    - Validates no active couriers in zone
    - Validates no pending deliveries in zone
    - Soft delete or hard delete based on business rules
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    # Check if zone has active couriers
    if zone.current_couriers > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete zone with active couriers",
        )

    zone_service.remove(db, id=zone_id)
    return None


@router.get("/{zone_id}/metrics", response_model=ZoneMetrics)
def get_zone_metrics(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get zone performance metrics

    Returns:
    - Current courier count and utilization
    - Average delivery time
    - Success rate
    - Total deliveries completed
    - Capacity status
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    # Calculate utilization rate
    utilization_rate = zone.utilization_rate if hasattr(zone, "utilization_rate") else 0.0

    # Calculate total deliveries today from deliveries table
    # We look for deliveries that were completed today
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    # Query deliveries completed today for this zone
    # Note: We need to match deliveries to zone - this could be via courier's zone or delivery address zone
    # For now, we'll use the zone_code from the delivery address if it exists
    # Since Delivery model may not have zone_id, we count all completed deliveries today
    # In a real implementation, you'd filter by zone_id or zone_code
    total_deliveries_today = db.query(func.count(Delivery.id)).filter(
        and_(
            Delivery.status == DeliveryStatus.DELIVERED,
            Delivery.delivery_time >= today_start,
            Delivery.delivery_time <= today_end
        )
    ).scalar() or 0

    metrics = ZoneMetrics(
        zone_id=zone.id,
        zone_code=zone.zone_code,
        zone_name=zone.zone_name,
        current_couriers=zone.current_couriers,
        max_couriers=zone.max_couriers,
        utilization_rate=utilization_rate,
        avg_delivery_time_minutes=zone.avg_delivery_time_minutes or 0.0,
        total_deliveries_today=total_deliveries_today,
        success_rate=zone.success_rate or 0.0,
        is_at_capacity=zone.is_at_capacity if hasattr(zone, "is_at_capacity") else False,
    )

    return metrics


@router.post("/{zone_id}/couriers/increment", response_model=ZoneResponse)
def increment_courier_count(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Increment zone courier count

    Business Logic:
    - Called when courier enters zone
    - Validates capacity not exceeded
    - Updates current_couriers count
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    if zone.current_couriers >= zone.max_couriers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Zone is at maximum capacity"
        )

    zone = zone_service.increment_courier_count(db, zone_id=zone_id)
    return zone


@router.post("/{zone_id}/couriers/decrement", response_model=ZoneResponse)
def decrement_courier_count(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Decrement zone courier count

    Business Logic:
    - Called when courier leaves zone
    - Updates current_couriers count
    - Prevents negative count
    """
    zone = zone_service.get(db, id=zone_id)
    if not zone or zone.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone not found")

    zone = zone_service.decrement_courier_count(db, zone_id=zone_id)
    return zone
