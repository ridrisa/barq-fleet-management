"""Route Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date

from app.services.base import CRUDBase
from app.models.operations.route import Route
from app.schemas.operations.route import RouteCreate, RouteUpdate


class RouteService(CRUDBase[Route, RouteCreate, RouteUpdate]):
    """Service for route management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Route]:
        """
        Get routes for a specific courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of route records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date(
        self,
        db: Session,
        *,
        route_date: date,
        skip: int = 0,
        limit: int = 100
    ) -> List[Route]:
        """
        Get routes for a specific date

        Args:
            db: Database session
            route_date: Date to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of route records
        """
        return (
            db.query(self.model)
            .filter(self.model.date == route_date)
            .order_by(self.model.route_name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Route]:
        """
        Get routes within a date range

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of route records
        """
        query = db.query(self.model).filter(
            and_(
                self.model.date >= start_date,
                self.model.date <= end_date
            )
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return (
            query.order_by(self.model.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_route_for_courier_date(
        self,
        db: Session,
        *,
        courier_id: int,
        route_date: date
    ) -> Optional[Route]:
        """
        Get route for a specific courier on a specific date

        Args:
            db: Database session
            courier_id: ID of the courier
            route_date: Date of the route

        Returns:
            Route record or None
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.courier_id == courier_id,
                    self.model.date == route_date
                )
            )
            .first()
        )

    def optimize_route(
        self,
        db: Session,
        *,
        route_id: int,
        optimized_waypoints: List[Dict]
    ) -> Optional[Route]:
        """
        Update route with optimized waypoints

        Args:
            db: Database session
            route_id: ID of the route
            optimized_waypoints: List of optimized waypoint dictionaries

        Returns:
            Updated route or None if not found
        """
        route = self.get(db, id=route_id)
        if not route:
            return None

        # Calculate total distance from waypoints if provided
        total_distance = sum(
            waypoint.get("distance", 0)
            for waypoint in optimized_waypoints
        )

        # Calculate estimated time (assuming average speed)
        # Example: 30 km/h average speed
        estimated_time = int((total_distance / 30) * 60) if total_distance > 0 else 0

        update_data = {
            "waypoints": optimized_waypoints,
            "total_distance": total_distance,
            "estimated_time": estimated_time
        }

        return self.update(db, db_obj=route, obj_in=update_data)

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get route statistics

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with route statistics
        """
        query = db.query(self.model)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if start_date:
            query = query.filter(self.model.date >= start_date)
        if end_date:
            query = query.filter(self.model.date <= end_date)

        routes = query.all()

        total_routes = len(routes)
        total_distance = sum(route.total_distance or 0 for route in routes)
        total_time = sum(route.estimated_time or 0 for route in routes)

        # Count waypoints
        total_waypoints = sum(
            len(route.waypoints) if route.waypoints else 0
            for route in routes
        )

        return {
            "total_routes": total_routes,
            "total_distance_km": total_distance,
            "total_estimated_time_minutes": total_time,
            "total_waypoints": total_waypoints,
            "average_distance_per_route": total_distance / total_routes if total_routes > 0 else 0,
            "average_waypoints_per_route": total_waypoints / total_routes if total_routes > 0 else 0,
            "average_time_per_route": total_time / total_routes if total_routes > 0 else 0
        }

    def add_waypoint(
        self,
        db: Session,
        *,
        route_id: int,
        waypoint: Dict
    ) -> Optional[Route]:
        """
        Add a waypoint to a route

        Args:
            db: Database session
            route_id: ID of the route
            waypoint: Waypoint dictionary with location data

        Returns:
            Updated route or None if not found
        """
        route = self.get(db, id=route_id)
        if not route:
            return None

        current_waypoints = route.waypoints or []
        current_waypoints.append(waypoint)

        # Recalculate totals
        total_distance = sum(
            wp.get("distance", 0)
            for wp in current_waypoints
        )
        estimated_time = int((total_distance / 30) * 60) if total_distance > 0 else 0

        update_data = {
            "waypoints": current_waypoints,
            "total_distance": total_distance,
            "estimated_time": estimated_time
        }

        return self.update(db, db_obj=route, obj_in=update_data)

    def remove_waypoint(
        self,
        db: Session,
        *,
        route_id: int,
        waypoint_index: int
    ) -> Optional[Route]:
        """
        Remove a waypoint from a route

        Args:
            db: Database session
            route_id: ID of the route
            waypoint_index: Index of waypoint to remove

        Returns:
            Updated route or None if not found or invalid index
        """
        route = self.get(db, id=route_id)
        if not route or not route.waypoints:
            return None

        current_waypoints = route.waypoints
        if waypoint_index < 0 or waypoint_index >= len(current_waypoints):
            return None

        current_waypoints.pop(waypoint_index)

        # Recalculate totals
        total_distance = sum(
            wp.get("distance", 0)
            for wp in current_waypoints
        )
        estimated_time = int((total_distance / 30) * 60) if total_distance > 0 else 0

        update_data = {
            "waypoints": current_waypoints,
            "total_distance": total_distance,
            "estimated_time": estimated_time
        }

        return self.update(db, db_obj=route, obj_in=update_data)

    def get_upcoming_routes(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Route]:
        """
        Get upcoming routes (today and future)

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of upcoming route records
        """
        query = db.query(self.model).filter(
            self.model.date >= date.today()
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return (
            query.order_by(self.model.date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )


route_service = RouteService(Route)
