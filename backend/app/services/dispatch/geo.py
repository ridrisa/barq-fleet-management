"""
Geographic Utility Functions
"""

import math
from datetime import datetime, timedelta

from app.services.dispatch.types import Point

EARTH_RADIUS_KM = 6371.0


def haversine_km(a: Point, b: Point) -> float:
    """
    Calculate the great-circle distance between two points
    on the Earth using the Haversine formula.

    Args:
        a: First point (lat/lng)
        b: Second point (lat/lng)

    Returns:
        Distance in kilometers
    """
    lat1_rad = math.radians(a.lat)
    lat2_rad = math.radians(b.lat)
    d_lat = math.radians(b.lat - a.lat)
    d_lng = math.radians(b.lng - a.lng)

    h = (
        math.sin(d_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(h), math.sqrt(1 - h))

    return EARTH_RADIUS_KM * c


def add_minutes(dt: datetime, minutes: float) -> datetime:
    """
    Add minutes to a datetime.

    Args:
        dt: Base datetime
        minutes: Minutes to add (can be fractional)

    Returns:
        New datetime with minutes added
    """
    return dt + timedelta(minutes=minutes)


def estimate_travel_time_minutes(
    distance_km: float,
    speed_kmh: float = 25.0
) -> float:
    """
    Estimate travel time based on distance and average speed.

    Args:
        distance_km: Distance in kilometers
        speed_kmh: Average speed in km/h

    Returns:
        Estimated travel time in minutes
    """
    if speed_kmh <= 0:
        return 0.0
    return (distance_km / speed_kmh) * 60.0


def point_in_radius(
    center: Point,
    point: Point,
    radius_km: float
) -> bool:
    """
    Check if a point is within a radius of a center point.

    Args:
        center: Center point
        point: Point to check
        radius_km: Radius in kilometers

    Returns:
        True if point is within radius
    """
    return haversine_km(center, point) <= radius_km
