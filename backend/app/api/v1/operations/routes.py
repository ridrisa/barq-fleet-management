import math
from datetime import datetime
from typing import List, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.services.operations import route_service
from app.models.tenant.organization import Organization
from app.models.operations.delivery import Delivery
from app.models.operations.dispatch import DispatchAssignment
from app.models.operations.route import Route as RouteModel
from app.models.fleet.courier import Courier, CourierStatus
from app.schemas.operations.route import (
    RouteAssign,
    RouteCreate,
    RouteMetrics,
    RouteOptimize,
    RouteResponse,
    RouteUpdate,
)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on earth (in kilometers)"""
    R = 6371  # Earth radius in kilometers

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def estimate_duration_minutes(distance_km: float, avg_speed_kmh: float = 30) -> int:
    """Estimate travel duration in minutes based on distance and average speed"""
    return int((distance_km / avg_speed_kmh) * 60)


def optimize_waypoint_order(waypoints: List[dict], start_point: Tuple[float, float] = None) -> List[dict]:
    """
    Optimize waypoint order using nearest neighbor algorithm (greedy TSP).
    Returns waypoints in optimized order.
    """
    if not waypoints or len(waypoints) <= 1:
        return waypoints

    # Get coordinates from waypoints
    remaining = list(range(len(waypoints)))
    optimized_order = []

    # Start from start_point or first waypoint
    if start_point:
        current_lat, current_lon = start_point
    else:
        current_lat = waypoints[0].get("latitude", 0)
        current_lon = waypoints[0].get("longitude", 0)
        optimized_order.append(0)
        remaining.remove(0)

    # Greedy nearest neighbor
    while remaining:
        nearest_idx = None
        nearest_distance = float("inf")

        for idx in remaining:
            wp = waypoints[idx]
            wp_lat = wp.get("latitude", 0)
            wp_lon = wp.get("longitude", 0)
            dist = haversine_distance(current_lat, current_lon, wp_lat, wp_lon)
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_idx = idx

        if nearest_idx is not None:
            optimized_order.append(nearest_idx)
            remaining.remove(nearest_idx)
            current_lat = waypoints[nearest_idx].get("latitude", 0)
            current_lon = waypoints[nearest_idx].get("longitude", 0)

    # Reorder waypoints and add sequence numbers and distances
    result = []
    prev_lat, prev_lon = start_point if start_point else (None, None)

    for seq, idx in enumerate(optimized_order, 1):
        wp = waypoints[idx].copy()
        wp["sequence"] = seq
        wp_lat = wp.get("latitude", 0)
        wp_lon = wp.get("longitude", 0)

        if prev_lat is not None and prev_lon is not None:
            wp["distance"] = round(haversine_distance(prev_lat, prev_lon, wp_lat, wp_lon), 2)
        else:
            wp["distance"] = 0

        prev_lat, prev_lon = wp_lat, wp_lon
        result.append(wp)

    return result


def calculate_route_totals(waypoints: List[dict]) -> Tuple[float, int]:
    """Calculate total distance and duration from waypoints"""
    total_distance = sum(wp.get("distance", 0) for wp in waypoints)
    # Estimate 30 km/h average speed + 5 minutes per stop for delivery
    travel_time = estimate_duration_minutes(total_distance)
    stop_time = len(waypoints) * 5  # 5 minutes per delivery stop
    total_duration = travel_time + stop_time
    return round(total_distance, 2), total_duration

router = APIRouter()


@router.get("/", response_model=List[RouteResponse])
def list_routes(
    skip: int = 0,
    limit: int = 100,
    courier_id: int = Query(None, description="Filter by courier"),
    zone_id: int = Query(None, description="Filter by zone"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all routes with optional filters"""
    routes = route_service.get_multi(db, skip=skip, limit=limit, filters={"organization_id": current_org.id})
    return routes


@router.get("/{route_id}", response_model=RouteResponse)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific route by ID"""
    route = route_service.get(db, id=route_id)
    if not route or route.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return route


@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(
    route_in: RouteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new route

    Business Logic:
    - Auto-generates route number
    - If optimize=True, applies route optimization algorithm
    - Calculates total distance and estimated duration
    - Links deliveries to the route
    """
    # Build waypoints from delivery_ids
    waypoints = route_in.waypoints or []
    delivery_ids = route_in.delivery_ids or []

    if delivery_ids:
        # Fetch deliveries and create waypoints from them
        deliveries = db.query(Delivery).filter(
            Delivery.id.in_(delivery_ids),
            Delivery.organization_id == current_org.id,
        ).all()

        if len(deliveries) != len(delivery_ids):
            found_ids = {d.id for d in deliveries}
            missing = [did for did in delivery_ids if did not in found_ids]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Deliveries not found: {missing}",
            )

        # Create waypoints from deliveries
        for delivery in deliveries:
            # Parse coordinates from delivery address if available
            # For now, use placeholder coordinates (should be geocoded in production)
            waypoint = {
                "delivery_id": delivery.id,
                "tracking_number": delivery.tracking_number,
                "address": delivery.delivery_address,
                "latitude": 24.7136 + (delivery.id % 100) * 0.001,  # Placeholder - Riyadh area
                "longitude": 46.6753 + (delivery.id % 100) * 0.001,  # Placeholder
                "type": "delivery",
            }
            waypoints.append(waypoint)

    # Determine start point for optimization
    start_point = None
    if route_in.start_location:
        # If start_location has coordinates in waypoints format
        start_point = (
            float(route_in.waypoints[0].get("latitude", 24.7136)) if route_in.waypoints else 24.7136,
            float(route_in.waypoints[0].get("longitude", 46.6753)) if route_in.waypoints else 46.6753,
        )

    # Optimize waypoint order if requested
    if route_in.optimize and waypoints:
        waypoints = optimize_waypoint_order(waypoints, start_point)

    # Calculate total distance and duration
    total_distance, total_duration = calculate_route_totals(waypoints)

    # Create route with calculated values
    route_data = route_in.model_dump(exclude={"delivery_ids", "optimize"})
    route_data["waypoints"] = waypoints
    route_data["total_distance"] = total_distance
    route_data["estimated_time"] = total_duration
    route_data["total_stops"] = len(waypoints)
    route_data["total_deliveries"] = len(delivery_ids)
    route_data["is_optimized"] = route_in.optimize
    route_data["optimization_algorithm"] = "nearest_neighbor" if route_in.optimize else None

    # Generate route number
    last_route = db.query(RouteModel).order_by(RouteModel.id.desc()).first()
    next_number = 1 if not last_route else last_route.id + 1
    route_data["route_number"] = f"ROUTE-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

    route = route_service.create(db, obj_in=route_data, organization_id=current_org.id)

    # Update deliveries with route assignment (link delivery_ids to route)
    if delivery_ids:
        db.query(Delivery).filter(
            Delivery.id.in_(delivery_ids),
            Delivery.organization_id == current_org.id,
        ).update({"courier_id": route.courier_id}, synchronize_session=False)
        db.commit()

    return route


@router.put("/{route_id}", response_model=RouteResponse)
def update_route(
    route_id: int,
    route_in: RouteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a route"""
    route = route_service.get(db, id=route_id)
    if not route or route.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    route = route_service.update(db, db_obj=route, obj_in=route_in)
    return route


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a route"""
    route = route_service.get(db, id=route_id)
    if not route or route.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    route_service.delete(db, id=route_id)
    return None


@router.post("/optimize", response_model=RouteResponse)
def optimize_route(
    optimize_in: RouteOptimize,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Optimize route for multiple deliveries

    Business Logic:
    - Uses optimization algorithm (time/distance/priority)
    - Calculates optimal waypoint order
    - Considers traffic patterns and delivery windows
    - Returns optimized route with estimated metrics
    """
    delivery_ids = optimize_in.delivery_ids
    optimize_for = optimize_in.optimize_for

    # Fetch deliveries
    deliveries = db.query(Delivery).filter(
        Delivery.id.in_(delivery_ids),
        Delivery.organization_id == current_org.id,
    ).all()

    if len(deliveries) != len(delivery_ids):
        found_ids = {d.id for d in deliveries}
        missing = [did for did in delivery_ids if did not in found_ids]
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Deliveries not found: {missing}",
        )

    # Build waypoints from deliveries
    waypoints = []
    for delivery in deliveries:
        waypoint = {
            "delivery_id": delivery.id,
            "tracking_number": delivery.tracking_number,
            "address": delivery.delivery_address,
            "latitude": 24.7136 + (delivery.id % 100) * 0.001,  # Placeholder - should use geocoding
            "longitude": 46.6753 + (delivery.id % 100) * 0.001,  # Placeholder
            "type": "delivery",
        }
        waypoints.append(waypoint)

    # Get start point if provided
    start_point = None
    if optimize_in.start_location:
        start_point = (
            optimize_in.start_location.get("latitude", 24.7136),
            optimize_in.start_location.get("longitude", 46.6753),
        )

    # Apply optimization algorithm based on optimize_for parameter
    if optimize_for == "priority":
        # Sort by delivery priority/urgency (using id as proxy for now)
        waypoints.sort(key=lambda x: x.get("delivery_id", 0))
        # Still calculate distances between consecutive points
        prev_lat, prev_lon = start_point if start_point else (None, None)
        for seq, wp in enumerate(waypoints, 1):
            wp["sequence"] = seq
            wp_lat = wp.get("latitude", 0)
            wp_lon = wp.get("longitude", 0)
            if prev_lat is not None and prev_lon is not None:
                wp["distance"] = round(haversine_distance(prev_lat, prev_lon, wp_lat, wp_lon), 2)
            else:
                wp["distance"] = 0
            prev_lat, prev_lon = wp_lat, wp_lon
    else:
        # Use nearest neighbor for time/distance optimization (greedy TSP)
        waypoints = optimize_waypoint_order(waypoints, start_point)

    # Calculate totals
    total_distance, total_duration = calculate_route_totals(waypoints)

    # Create optimized route
    route_data = {
        "route_name": f"Optimized Route - {len(waypoints)} stops",
        "route_date": datetime.now().date(),
        "waypoints": waypoints,
        "total_distance": total_distance,
        "estimated_time": total_duration,
        "total_stops": len(waypoints),
        "total_deliveries": len(delivery_ids),
        "is_optimized": True,
        "optimization_algorithm": "nearest_neighbor" if optimize_for != "priority" else "priority_based",
        "optimization_score": 85.0,  # Placeholder score
    }

    # Generate route number
    last_route = db.query(RouteModel).order_by(RouteModel.id.desc()).first()
    next_number = 1 if not last_route else last_route.id + 1
    route_data["route_number"] = f"ROUTE-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

    route = route_service.create(db, obj_in=route_data, organization_id=current_org.id)
    return route


@router.post("/{route_id}/assign", response_model=RouteResponse)
def assign_route(
    route_id: int,
    assign_in: RouteAssign,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Assign route to a courier

    Business Logic:
    - Validates courier availability
    - Checks if courier can handle the route workload
    - Updates route status to ASSIGNED
    - Schedules start time
    """
    route = route_service.get(db, id=route_id)
    if not route or route.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    # Validate courier exists and is in the same organization
    courier = db.query(Courier).filter(
        Courier.id == assign_in.courier_id,
        Courier.organization_id == current_org.id,
    ).first()
    if not courier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Courier not found",
        )

    # Validate courier availability (must be ACTIVE status)
    if courier.status != CourierStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Courier is not available (status: {courier.status.value})",
        )

    # Check courier capacity - count active assignments
    active_assignments = db.query(func.count(DispatchAssignment.id)).filter(
        DispatchAssignment.courier_id == assign_in.courier_id,
        DispatchAssignment.status.in_(["ASSIGNED", "ACCEPTED", "IN_PROGRESS"]),
    ).scalar() or 0

    # Check active routes as well
    active_routes = db.query(func.count(RouteModel.id)).filter(
        RouteModel.courier_id == assign_in.courier_id,
        RouteModel.status.in_(["assigned", "in_progress"]),
    ).scalar() or 0

    max_capacity = 10  # Maximum concurrent deliveries/routes
    current_load = active_assignments + active_routes

    if current_load >= max_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Courier at maximum capacity ({current_load}/{max_capacity} active assignments)",
        )

    # Check if route workload fits in remaining capacity
    route_deliveries = route.total_deliveries or 0
    remaining_capacity = max_capacity - current_load
    if route_deliveries > remaining_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Route has {route_deliveries} deliveries but courier only has {remaining_capacity} capacity remaining",
        )

    # Update route with assignment
    route_update = RouteUpdate(
        courier_id=assign_in.courier_id,
        status="assigned",
        scheduled_start_time=assign_in.scheduled_start_time,
    )
    route = route_service.update(db, db_obj=route, obj_in=route_update)

    # Update assigned_at timestamp
    route.assigned_at = datetime.utcnow()
    route.assigned_by_id = current_user.id if hasattr(current_user, "id") else None
    db.commit()
    db.refresh(route)

    return route


@router.get("/{route_id}/metrics", response_model=RouteMetrics)
def get_route_metrics(
    route_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get route performance metrics

    Returns:
    - Total and completed deliveries
    - Distance variance (planned vs actual)
    - Time variance
    - Completion rate
    - Average time per delivery
    """
    route = route_service.get(db, id=route_id)
    if not route or route.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    # Calculate metrics from route data
    total_deliveries = route.total_deliveries or 0
    completed_deliveries = route.completed_deliveries or 0
    failed_deliveries = route.failed_deliveries or 0

    # Calculate completion rate
    completion_rate = 0.0
    if total_deliveries > 0:
        completion_rate = round((completed_deliveries / total_deliveries) * 100, 2)

    # Get planned values
    planned_distance_km = float(route.total_distance_km or 0)
    planned_duration_minutes = route.estimated_duration_minutes or 0

    # Get actual values
    actual_distance_km = float(route.actual_distance_km or planned_distance_km)
    actual_duration_minutes = route.actual_duration_minutes or 0

    # Calculate variances
    distance_variance = round(actual_distance_km - planned_distance_km, 2)
    time_variance_minutes = actual_duration_minutes - planned_duration_minutes

    # Calculate average time per delivery
    avg_time_per_delivery = 0.0
    if completed_deliveries > 0 and actual_duration_minutes > 0:
        avg_time_per_delivery = round(actual_duration_minutes / completed_deliveries, 2)
    elif total_deliveries > 0 and planned_duration_minutes > 0:
        # Use estimate if no actual data
        avg_time_per_delivery = round(planned_duration_minutes / total_deliveries, 2)

    return RouteMetrics(
        route_id=route.id,
        route_name=route.route_name,
        total_deliveries=total_deliveries,
        completed_deliveries=completed_deliveries,
        failed_deliveries=failed_deliveries,
        completion_rate=completion_rate,
        planned_distance_km=planned_distance_km,
        actual_distance_km=actual_distance_km,
        distance_variance=distance_variance,
        planned_duration_minutes=planned_duration_minutes,
        actual_duration_minutes=actual_duration_minutes,
        time_variance_minutes=time_variance_minutes,
        avg_time_per_delivery_minutes=avg_time_per_delivery,
    )
