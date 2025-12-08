"""
Routing Provider Interface
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.services.dispatch.types import Point


@dataclass
class DistanceMatrixResult:
    """Result from distance matrix API"""
    durations_minutes: list[list[float]] = field(default_factory=list)  # [origin_i][dest_j]
    distances_km: list[list[float]] = field(default_factory=list)       # [origin_i][dest_j]


@dataclass
class RouteLeg:
    """A single leg in a route"""
    from_point: Point
    to_point: Point
    distance_km: float
    duration_minutes: float


@dataclass
class RouteResult:
    """Result from route/directions API"""
    legs: list[RouteLeg] = field(default_factory=list)
    polyline: Optional[str] = None

    @property
    def total_distance_km(self) -> float:
        return sum(leg.distance_km for leg in self.legs)

    @property
    def total_duration_minutes(self) -> float:
        return sum(leg.duration_minutes for leg in self.legs)


class RoutingProvider(ABC):
    """Abstract interface for routing/directions services"""

    @abstractmethod
    async def get_travel_times(
        self,
        origins: list[Point],
        destinations: list[Point],
        departure_time: datetime
    ) -> DistanceMatrixResult:
        """
        Get travel times and distances between multiple origins and destinations.

        Args:
            origins: List of origin points
            destinations: List of destination points
            departure_time: Departure time for traffic consideration

        Returns:
            Matrix of durations and distances
        """
        pass

    @abstractmethod
    async def get_route(
        self,
        origin: Point,
        waypoints: list[Point],
        departure_time: datetime,
        optimize: bool = False
    ) -> RouteResult:
        """
        Get a route from origin through waypoints.

        Args:
            origin: Starting point
            waypoints: List of waypoints to visit
            departure_time: Departure time
            optimize: Whether to optimize waypoint order

        Returns:
            Route with legs and optional polyline
        """
        pass
