"""
Google Maps Routing Provider Implementation
"""

import logging
from datetime import datetime
from typing import Optional

import httpx

from app.config.settings import settings
from app.services.dispatch.geo import haversine_km
from app.services.dispatch.routing import (
    DistanceMatrixResult,
    RouteLeg,
    RouteResult,
    RoutingProvider,
)
from app.services.dispatch.types import Point

logger = logging.getLogger(__name__)


class GoogleRoutingProvider(RoutingProvider):
    """
    Google Maps API routing provider with caching.

    Implements:
    - Distance Matrix API for travel times
    - Directions API for route planning
    - Cell-based caching to reduce API calls
    """

    DISTANCE_MATRIX_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
    DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_ttl_minutes: int = 20,
        timeout_seconds: float = 30.0
    ):
        self.api_key = api_key or getattr(settings, "GOOGLE_MAPS_API_KEY", "")
        self.cache_ttl_ms = cache_ttl_minutes * 60 * 1000
        self.timeout = timeout_seconds
        self._cache: dict[str, dict] = {}  # CacheKey -> {distance_km, duration_minutes, expires_at}

    def _snap_cell(self, point: Point) -> str:
        """Snap point to grid cell for caching (3 decimal places ~ 110m)"""
        return f"{point.lat:.3f},{point.lng:.3f}"

    def _time_bucket_key(self, departure_time: datetime) -> str:
        """Create time bucket key (15-minute intervals)"""
        bucket = int(departure_time.timestamp() / (15 * 60))
        return str(bucket)

    def _build_cache_key(
        self,
        origin: Point,
        destination: Point,
        departure_time: datetime
    ) -> str:
        """Build cache key from origin, destination, and time bucket"""
        return f"{self._snap_cell(origin)}|{self._snap_cell(destination)}|{self._time_bucket_key(departure_time)}"

    def _get_from_cache(
        self,
        origin: Point,
        destination: Point,
        departure_time: datetime
    ) -> Optional[dict]:
        """Get cached entry if valid"""
        key = self._build_cache_key(origin, destination, departure_time)
        entry = self._cache.get(key)
        if not entry:
            return None
        if entry["expires_at"] < datetime.now().timestamp() * 1000:
            del self._cache[key]
            return None
        return entry

    def _set_cache(
        self,
        origin: Point,
        destination: Point,
        departure_time: datetime,
        distance_km: float,
        duration_minutes: float
    ) -> None:
        """Cache a distance/duration result"""
        key = self._build_cache_key(origin, destination, departure_time)
        self._cache[key] = {
            "distance_km": distance_km,
            "duration_minutes": duration_minutes,
            "expires_at": datetime.now().timestamp() * 1000 + self.cache_ttl_ms,
        }

    async def get_travel_times(
        self,
        origins: list[Point],
        destinations: list[Point],
        departure_time: datetime
    ) -> DistanceMatrixResult:
        """
        Get travel times between origins and destinations using Google Distance Matrix API.
        """
        if not origins or not destinations:
            return DistanceMatrixResult(
                durations_minutes=[],
                distances_km=[]
            )

        # Initialize result matrices
        durations_minutes = [[0.0] * len(destinations) for _ in origins]
        distances_km = [[0.0] * len(destinations) for _ in origins]

        # Check cache for each origin-destination pair
        missing_pairs: list[tuple[int, int]] = []

        for oi, origin in enumerate(origins):
            for di, destination in enumerate(destinations):
                cached = self._get_from_cache(origin, destination, departure_time)
                if cached:
                    durations_minutes[oi][di] = cached["duration_minutes"]
                    distances_km[oi][di] = cached["distance_km"]
                else:
                    missing_pairs.append((oi, di))

        if not missing_pairs:
            return DistanceMatrixResult(
                durations_minutes=durations_minutes,
                distances_km=distances_km
            )

        # If no API key, use Haversine estimation
        if not self.api_key:
            logger.warning("No Google Maps API key - using Haversine estimation")
            return self._estimate_with_haversine(origins, destinations)

        # Call Google Distance Matrix API
        try:
            origins_str = "|".join(f"{p.lat},{p.lng}" for p in origins)
            destinations_str = "|".join(f"{p.lat},{p.lng}" for p in destinations)

            params = {
                "origins": origins_str,
                "destinations": destinations_str,
                "departure_time": str(int(departure_time.timestamp())),
                "key": self.api_key,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.DISTANCE_MATRIX_URL, params=params)
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "OK":
                logger.error(f"Distance Matrix API error: {data.get('status')}")
                return self._estimate_with_haversine(origins, destinations)

            rows = data.get("rows", [])
            if len(rows) != len(origins):
                logger.error("Unexpected Distance Matrix response structure")
                return self._estimate_with_haversine(origins, destinations)

            for oi, row in enumerate(rows):
                elements = row.get("elements", [])
                for di, el in enumerate(elements):
                    if el.get("status") != "OK":
                        # Use Haversine fallback for this pair
                        dist = haversine_km(origins[oi], destinations[di])
                        dur = (dist / 25.0) * 60  # Assume 25 km/h
                        distances_km[oi][di] = dist
                        durations_minutes[oi][di] = dur
                    else:
                        dist_m = el.get("distance", {}).get("value", 0)
                        dur_s = el.get("duration", {}).get("value", 0)
                        dist_km = dist_m / 1000.0
                        dur_min = dur_s / 60.0

                        distances_km[oi][di] = dist_km
                        durations_minutes[oi][di] = dur_min

                        # Cache the result
                        self._set_cache(
                            origins[oi],
                            destinations[di],
                            departure_time,
                            dist_km,
                            dur_min
                        )

        except Exception as e:
            logger.error(f"Distance Matrix API call failed: {e}")
            return self._estimate_with_haversine(origins, destinations)

        return DistanceMatrixResult(
            durations_minutes=durations_minutes,
            distances_km=distances_km
        )

    def _estimate_with_haversine(
        self,
        origins: list[Point],
        destinations: list[Point],
        speed_kmh: float = 25.0
    ) -> DistanceMatrixResult:
        """Fallback: estimate using Haversine distance"""
        durations_minutes = []
        distances_km = []

        for origin in origins:
            dur_row = []
            dist_row = []
            for destination in destinations:
                dist = haversine_km(origin, destination)
                dur = (dist / speed_kmh) * 60 if speed_kmh > 0 else 0
                dist_row.append(dist)
                dur_row.append(dur)
            distances_km.append(dist_row)
            durations_minutes.append(dur_row)

        return DistanceMatrixResult(
            durations_minutes=durations_minutes,
            distances_km=distances_km
        )

    async def get_route(
        self,
        origin: Point,
        waypoints: list[Point],
        departure_time: datetime,
        optimize: bool = False
    ) -> RouteResult:
        """
        Get a route using Google Directions API.
        """
        if not waypoints:
            return RouteResult(legs=[], polyline=None)

        # If no API key, use Haversine estimation
        if not self.api_key:
            logger.warning("No Google Maps API key - using Haversine route estimation")
            return self._estimate_route_with_haversine(origin, waypoints)

        try:
            destination = waypoints[-1]
            intermediate = waypoints[:-1] if len(waypoints) > 1 else []

            params = {
                "origin": f"{origin.lat},{origin.lng}",
                "destination": f"{destination.lat},{destination.lng}",
                "departure_time": str(int(departure_time.timestamp())),
                "key": self.api_key,
            }

            if intermediate:
                waypoint_str = "|".join(f"{p.lat},{p.lng}" for p in intermediate)
                if optimize:
                    waypoint_str = f"optimize:true|{waypoint_str}"
                params["waypoints"] = waypoint_str

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.DIRECTIONS_URL, params=params)
                response.raise_for_status()
                data = response.json()

            if data.get("status") != "OK" or not data.get("routes"):
                logger.error(f"Directions API error: {data.get('status')}")
                return self._estimate_route_with_haversine(origin, waypoints)

            route = data["routes"][0]
            legs: list[RouteLeg] = []

            for leg in route.get("legs", []):
                start_loc = leg.get("start_location", {})
                end_loc = leg.get("end_location", {})
                dist_m = leg.get("distance", {}).get("value", 0)
                dur_s = leg.get("duration", {}).get("value", 0)

                legs.append(RouteLeg(
                    from_point=Point(
                        lat=start_loc.get("lat", 0),
                        lng=start_loc.get("lng", 0)
                    ),
                    to_point=Point(
                        lat=end_loc.get("lat", 0),
                        lng=end_loc.get("lng", 0)
                    ),
                    distance_km=dist_m / 1000.0,
                    duration_minutes=dur_s / 60.0,
                ))

            polyline = route.get("overview_polyline", {}).get("points")

            return RouteResult(legs=legs, polyline=polyline)

        except Exception as e:
            logger.error(f"Directions API call failed: {e}")
            return self._estimate_route_with_haversine(origin, waypoints)

    def _estimate_route_with_haversine(
        self,
        origin: Point,
        waypoints: list[Point],
        speed_kmh: float = 25.0
    ) -> RouteResult:
        """Fallback: estimate route using Haversine distances"""
        legs: list[RouteLeg] = []
        prev_point = origin

        for waypoint in waypoints:
            dist = haversine_km(prev_point, waypoint)
            dur = (dist / speed_kmh) * 60 if speed_kmh > 0 else 0

            legs.append(RouteLeg(
                from_point=prev_point,
                to_point=waypoint,
                distance_km=dist,
                duration_minutes=dur,
            ))
            prev_point = waypoint

        return RouteResult(legs=legs, polyline=None)


# Singleton instance
_google_routing_provider: Optional[GoogleRoutingProvider] = None


def get_google_routing_provider() -> GoogleRoutingProvider:
    """Get or create the Google Routing Provider singleton"""
    global _google_routing_provider
    if _google_routing_provider is None:
        _google_routing_provider = GoogleRoutingProvider()
    return _google_routing_provider
