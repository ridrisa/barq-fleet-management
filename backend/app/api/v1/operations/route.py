"""Route Management API Routes"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from datetime import date

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.operations import (
    RouteCreate, RouteUpdate, RouteResponse
)
from app.services.operations import route_service


router = APIRouter()


@router.get("/", response_model=List[RouteResponse])
def get_routes(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    route_date: Optional[date] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of routes with filtering

    Filters:
    - courier_id: Filter by courier ID
    - route_date: Filter by specific date
    - start_date, end_date: Filter by date range
    """
    # Filter by specific date
    if route_date:
        return route_service.get_by_date(
            db, route_date=route_date, skip=skip, limit=limit
        )

    # Filter by date range
    if start_date and end_date:
        return route_service.get_by_date_range(
            db,
            start_date=start_date,
            end_date=end_date,
            courier_id=courier_id,
            skip=skip,
            limit=limit
        )

    # Filter by courier
    if courier_id:
        return route_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit
        )

    return route_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED)
def create_route(
    route_in: RouteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new route"""
    # Check if route already exists for courier on this date
    if route_in.courier_id:
        existing = route_service.get_route_for_courier_date(
            db, courier_id=route_in.courier_id, route_date=route_in.date
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Route already exists for this courier on this date"
            )

    return route_service.create(db, obj_in=route_in)


@router.get("/upcoming", response_model=List[RouteResponse])
def get_upcoming_routes(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get upcoming routes (today and future)"""
    return route_service.get_upcoming_routes(
        db, courier_id=courier_id, skip=skip, limit=limit
    )


@router.get("/statistics", response_model=dict)
def get_route_statistics(
    db: Session = Depends(get_db),
    courier_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """Get route statistics"""
    return route_service.get_statistics(
        db,
        courier_id=courier_id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/{route_id}", response_model=RouteResponse)
def get_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get route by ID"""
    route = route_service.get(db, id=route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.put("/{route_id}", response_model=RouteResponse)
def update_route(
    route_id: int,
    route_in: RouteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update route"""
    route = route_service.get(db, id=route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    return route_service.update(db, db_obj=route, obj_in=route_in)


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_route(
    route_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete route"""
    route = route_service.get(db, id=route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    route_service.delete(db, id=route_id)
    return None


@router.patch("/{route_id}/optimize", response_model=RouteResponse)
def optimize_route(
    route_id: int,
    optimized_waypoints: List[Dict] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update route with optimized waypoints"""
    route = route_service.optimize_route(
        db, route_id=route_id, optimized_waypoints=optimized_waypoints
    )
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.post("/{route_id}/waypoints", response_model=RouteResponse)
def add_waypoint(
    route_id: int,
    waypoint: Dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a waypoint to route"""
    route = route_service.add_waypoint(
        db, route_id=route_id, waypoint=waypoint
    )
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route


@router.delete("/{route_id}/waypoints/{waypoint_index}", response_model=RouteResponse)
def remove_waypoint(
    route_id: int,
    waypoint_index: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a waypoint from route"""
    route = route_service.remove_waypoint(
        db, route_id=route_id, waypoint_index=waypoint_index
    )
    if not route:
        raise HTTPException(
            status_code=404,
            detail="Route not found or invalid waypoint index"
        )
    return route
