"""
Unit Tests for Geo Service

Tests geographic utility functions including:
- Haversine distance calculation
- Time estimation
- Point-in-radius check
"""

import pytest
from datetime import datetime, timedelta

from app.services.dispatch.geo import (
    haversine_km,
    add_minutes,
    estimate_travel_time_minutes,
    point_in_radius,
    EARTH_RADIUS_KM,
)
from app.services.dispatch.types import Point


class TestHaversineDistance:
    """Tests for the haversine_km function"""

    def test_same_point_returns_zero(self):
        """Distance between same point should be zero"""
        point = Point(lat=24.7136, lng=46.6753)  # Riyadh
        distance = haversine_km(point, point)
        assert distance == pytest.approx(0.0, abs=0.001)

    def test_known_distance_riyadh_jeddah(self):
        """Test known distance between Riyadh and Jeddah (~950 km)"""
        riyadh = Point(lat=24.7136, lng=46.6753)
        jeddah = Point(lat=21.4858, lng=39.1925)

        distance = haversine_km(riyadh, jeddah)
        # Actual distance is approximately 850-950 km
        assert 800 < distance < 1000

    def test_known_distance_short(self):
        """Test short distance between nearby points (~5 km)"""
        # Two points approximately 5 km apart in Riyadh
        point1 = Point(lat=24.7136, lng=46.6753)
        point2 = Point(lat=24.7580, lng=46.6753)  # ~5km north

        distance = haversine_km(point1, point2)
        assert 4 < distance < 6

    def test_distance_is_symmetric(self):
        """Distance A->B should equal B->A"""
        point_a = Point(lat=24.7136, lng=46.6753)
        point_b = Point(lat=21.4858, lng=39.1925)

        distance_ab = haversine_km(point_a, point_b)
        distance_ba = haversine_km(point_b, point_a)

        assert distance_ab == pytest.approx(distance_ba, abs=0.001)

    def test_distance_across_equator(self):
        """Test distance calculation across the equator"""
        north = Point(lat=10.0, lng=0.0)
        south = Point(lat=-10.0, lng=0.0)

        distance = haversine_km(north, south)
        # 20 degrees latitude ≈ 2,222 km
        assert 2200 < distance < 2300

    def test_distance_across_prime_meridian(self):
        """Test distance calculation across the prime meridian"""
        east = Point(lat=0.0, lng=10.0)
        west = Point(lat=0.0, lng=-10.0)

        distance = haversine_km(east, west)
        # 20 degrees longitude at equator ≈ 2,222 km
        assert 2200 < distance < 2300

    def test_very_small_distance(self):
        """Test very small distance (meters apart)"""
        point1 = Point(lat=24.713600, lng=46.675300)
        point2 = Point(lat=24.713610, lng=46.675310)  # ~1 meter apart

        distance = haversine_km(point1, point2)
        assert 0 < distance < 0.01  # Less than 10 meters in km

    def test_antipodal_points(self):
        """Test distance for antipodal points (opposite sides of Earth)"""
        point1 = Point(lat=0.0, lng=0.0)
        point2 = Point(lat=0.0, lng=180.0)

        distance = haversine_km(point1, point2)
        # Half the Earth's circumference ≈ 20,015 km
        expected_half_circumference = EARTH_RADIUS_KM * 3.14159
        assert distance == pytest.approx(expected_half_circumference, rel=0.01)


class TestAddMinutes:
    """Tests for the add_minutes function"""

    def test_add_positive_minutes(self):
        """Adding positive minutes should advance time"""
        base_time = datetime(2025, 1, 15, 12, 0, 0)
        result = add_minutes(base_time, 30)

        assert result == datetime(2025, 1, 15, 12, 30, 0)

    def test_add_zero_minutes(self):
        """Adding zero minutes should return same time"""
        base_time = datetime(2025, 1, 15, 12, 0, 0)
        result = add_minutes(base_time, 0)

        assert result == base_time

    def test_add_fractional_minutes(self):
        """Adding fractional minutes should work correctly"""
        base_time = datetime(2025, 1, 15, 12, 0, 0)
        result = add_minutes(base_time, 30.5)  # 30 minutes 30 seconds

        expected = base_time + timedelta(minutes=30.5)
        assert result == expected

    def test_add_minutes_crossing_hour(self):
        """Adding minutes that cross hour boundary"""
        base_time = datetime(2025, 1, 15, 12, 45, 0)
        result = add_minutes(base_time, 30)

        assert result == datetime(2025, 1, 15, 13, 15, 0)

    def test_add_minutes_crossing_day(self):
        """Adding minutes that cross day boundary"""
        base_time = datetime(2025, 1, 15, 23, 45, 0)
        result = add_minutes(base_time, 30)

        assert result == datetime(2025, 1, 16, 0, 15, 0)

    def test_add_large_minutes(self):
        """Adding large number of minutes (hours worth)"""
        base_time = datetime(2025, 1, 15, 12, 0, 0)
        result = add_minutes(base_time, 120)  # 2 hours

        assert result == datetime(2025, 1, 15, 14, 0, 0)


class TestEstimateTravelTime:
    """Tests for the estimate_travel_time_minutes function"""

    def test_zero_distance_returns_zero(self):
        """Zero distance should return zero time"""
        time = estimate_travel_time_minutes(0.0)
        assert time == 0.0

    def test_default_speed(self):
        """Test with default speed (25 km/h)"""
        # 25 km at 25 km/h = 1 hour = 60 minutes
        time = estimate_travel_time_minutes(25.0)
        assert time == pytest.approx(60.0)

    def test_custom_speed(self):
        """Test with custom speed"""
        # 50 km at 50 km/h = 1 hour = 60 minutes
        time = estimate_travel_time_minutes(50.0, speed_kmh=50.0)
        assert time == pytest.approx(60.0)

    def test_short_distance(self):
        """Test short distance estimation"""
        # 5 km at 25 km/h = 0.2 hours = 12 minutes
        time = estimate_travel_time_minutes(5.0)
        assert time == pytest.approx(12.0)

    def test_zero_speed_returns_zero(self):
        """Zero speed should return zero (avoid division by zero)"""
        time = estimate_travel_time_minutes(10.0, speed_kmh=0.0)
        assert time == 0.0

    def test_negative_speed_returns_zero(self):
        """Negative speed should return zero"""
        time = estimate_travel_time_minutes(10.0, speed_kmh=-10.0)
        assert time == 0.0

    def test_fractional_result(self):
        """Test calculation returns fractional minutes"""
        # 1 km at 25 km/h = 0.04 hours = 2.4 minutes
        time = estimate_travel_time_minutes(1.0)
        assert time == pytest.approx(2.4)


class TestPointInRadius:
    """Tests for the point_in_radius function"""

    def test_same_point_is_in_radius(self):
        """Same point should always be in radius"""
        center = Point(lat=24.7136, lng=46.6753)
        assert point_in_radius(center, center, 1.0) is True

    def test_point_inside_radius(self):
        """Point clearly inside radius should return True"""
        center = Point(lat=24.7136, lng=46.6753)
        nearby = Point(lat=24.7140, lng=46.6760)  # ~60 meters away

        assert point_in_radius(center, nearby, 1.0) is True

    def test_point_outside_radius(self):
        """Point clearly outside radius should return False"""
        center = Point(lat=24.7136, lng=46.6753)
        far = Point(lat=24.8000, lng=46.7500)  # ~12 km away

        assert point_in_radius(center, far, 5.0) is False

    def test_point_exactly_on_radius(self):
        """Point exactly on radius boundary should return True (<=)"""
        center = Point(lat=24.7136, lng=46.6753)
        # Use haversine to find exact point
        on_boundary = Point(lat=24.7586, lng=46.6753)  # ~5km north

        distance = haversine_km(center, on_boundary)
        assert point_in_radius(center, on_boundary, distance) is True

    def test_point_just_inside_radius(self):
        """Point just inside radius should return True"""
        center = Point(lat=24.7136, lng=46.6753)
        # Point approximately 4.9 km away
        nearby = Point(lat=24.7580, lng=46.6753)

        assert point_in_radius(center, nearby, 5.0) is True

    def test_point_just_outside_radius(self):
        """Point just outside radius should return False"""
        center = Point(lat=24.7136, lng=46.6753)
        # Point approximately 5.1 km away
        far = Point(lat=24.7600, lng=46.6753)

        distance = haversine_km(center, far)
        assert point_in_radius(center, far, distance - 0.1) is False

    def test_zero_radius(self):
        """Zero radius should only include exact point"""
        center = Point(lat=24.7136, lng=46.6753)
        same = Point(lat=24.7136, lng=46.6753)
        different = Point(lat=24.7137, lng=46.6753)

        assert point_in_radius(center, same, 0.0) is True
        assert point_in_radius(center, different, 0.0) is False

    def test_large_radius(self):
        """Large radius should include distant points"""
        riyadh = Point(lat=24.7136, lng=46.6753)
        jeddah = Point(lat=21.4858, lng=39.1925)

        # Jeddah is ~850-900 km from Riyadh
        assert point_in_radius(riyadh, jeddah, 1000.0) is True
        assert point_in_radius(riyadh, jeddah, 800.0) is False
