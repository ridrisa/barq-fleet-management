"""
Unit Tests for Routing Service

Tests the routing provider interface and data structures:
- DistanceMatrixResult
- RouteLeg
- RouteResult
- RoutingProvider interface
"""

import pytest
from datetime import datetime

from app.services.dispatch.routing import (
    DistanceMatrixResult,
    RouteLeg,
    RouteResult,
    RoutingProvider,
)
from app.services.dispatch.types import Point


class TestDistanceMatrixResult:
    """Tests for DistanceMatrixResult dataclass"""

    def test_empty_result(self):
        """Empty result should have empty lists"""
        result = DistanceMatrixResult()
        assert result.durations_minutes == []
        assert result.distances_km == []

    def test_result_with_data(self):
        """Result should properly store matrix data"""
        durations = [[10.0, 20.0], [15.0, 25.0]]
        distances = [[5.0, 10.0], [7.5, 12.5]]

        result = DistanceMatrixResult(
            durations_minutes=durations,
            distances_km=distances
        )

        assert result.durations_minutes == durations
        assert result.distances_km == distances

    def test_single_origin_destination(self):
        """Result with single origin and destination"""
        result = DistanceMatrixResult(
            durations_minutes=[[15.0]],
            distances_km=[[5.0]]
        )

        assert result.durations_minutes[0][0] == 15.0
        assert result.distances_km[0][0] == 5.0

    def test_multiple_origins_single_destination(self):
        """Result with multiple origins and single destination"""
        result = DistanceMatrixResult(
            durations_minutes=[[10.0], [15.0], [20.0]],
            distances_km=[[5.0], [7.5], [10.0]]
        )

        assert len(result.durations_minutes) == 3
        assert len(result.durations_minutes[0]) == 1

    def test_asymmetric_matrix(self):
        """Result with asymmetric matrix (2 origins, 3 destinations)"""
        result = DistanceMatrixResult(
            durations_minutes=[[10.0, 15.0, 20.0], [12.0, 17.0, 22.0]],
            distances_km=[[5.0, 7.5, 10.0], [6.0, 8.5, 11.0]]
        )

        assert len(result.durations_minutes) == 2
        assert len(result.durations_minutes[0]) == 3


class TestRouteLeg:
    """Tests for RouteLeg dataclass"""

    def test_route_leg_creation(self):
        """RouteLeg should store all properties correctly"""
        from_point = Point(lat=24.7136, lng=46.6753)
        to_point = Point(lat=24.7580, lng=46.6753)

        leg = RouteLeg(
            from_point=from_point,
            to_point=to_point,
            distance_km=5.0,
            duration_minutes=12.0
        )

        assert leg.from_point == from_point
        assert leg.to_point == to_point
        assert leg.distance_km == 5.0
        assert leg.duration_minutes == 12.0

    def test_route_leg_with_zero_values(self):
        """RouteLeg should accept zero distance and duration"""
        from_point = Point(lat=24.7136, lng=46.6753)
        to_point = Point(lat=24.7136, lng=46.6753)  # Same point

        leg = RouteLeg(
            from_point=from_point,
            to_point=to_point,
            distance_km=0.0,
            duration_minutes=0.0
        )

        assert leg.distance_km == 0.0
        assert leg.duration_minutes == 0.0


class TestRouteResult:
    """Tests for RouteResult dataclass"""

    def test_empty_route(self):
        """Empty route should have no legs"""
        result = RouteResult()
        assert result.legs == []
        assert result.polyline is None

    def test_route_with_single_leg(self):
        """Route with single leg"""
        leg = RouteLeg(
            from_point=Point(lat=24.7136, lng=46.6753),
            to_point=Point(lat=24.7580, lng=46.6753),
            distance_km=5.0,
            duration_minutes=12.0
        )

        result = RouteResult(legs=[leg])

        assert len(result.legs) == 1
        assert result.legs[0] == leg

    def test_route_with_polyline(self):
        """Route should store polyline"""
        result = RouteResult(
            legs=[],
            polyline="encoded_polyline_string"
        )

        assert result.polyline == "encoded_polyline_string"

    def test_total_distance_empty(self):
        """Empty route should have zero total distance"""
        result = RouteResult()
        assert result.total_distance_km == 0.0

    def test_total_distance_single_leg(self):
        """Total distance with single leg"""
        leg = RouteLeg(
            from_point=Point(lat=24.7136, lng=46.6753),
            to_point=Point(lat=24.7580, lng=46.6753),
            distance_km=5.0,
            duration_minutes=12.0
        )

        result = RouteResult(legs=[leg])
        assert result.total_distance_km == 5.0

    def test_total_distance_multiple_legs(self):
        """Total distance should sum all leg distances"""
        leg1 = RouteLeg(
            from_point=Point(lat=24.7136, lng=46.6753),
            to_point=Point(lat=24.7300, lng=46.6753),
            distance_km=3.0,
            duration_minutes=8.0
        )
        leg2 = RouteLeg(
            from_point=Point(lat=24.7300, lng=46.6753),
            to_point=Point(lat=24.7580, lng=46.6753),
            distance_km=2.0,
            duration_minutes=4.0
        )
        leg3 = RouteLeg(
            from_point=Point(lat=24.7580, lng=46.6753),
            to_point=Point(lat=24.8000, lng=46.6753),
            distance_km=4.5,
            duration_minutes=10.0
        )

        result = RouteResult(legs=[leg1, leg2, leg3])
        assert result.total_distance_km == 9.5  # 3.0 + 2.0 + 4.5

    def test_total_duration_empty(self):
        """Empty route should have zero total duration"""
        result = RouteResult()
        assert result.total_duration_minutes == 0.0

    def test_total_duration_single_leg(self):
        """Total duration with single leg"""
        leg = RouteLeg(
            from_point=Point(lat=24.7136, lng=46.6753),
            to_point=Point(lat=24.7580, lng=46.6753),
            distance_km=5.0,
            duration_minutes=12.0
        )

        result = RouteResult(legs=[leg])
        assert result.total_duration_minutes == 12.0

    def test_total_duration_multiple_legs(self):
        """Total duration should sum all leg durations"""
        leg1 = RouteLeg(
            from_point=Point(lat=24.7136, lng=46.6753),
            to_point=Point(lat=24.7300, lng=46.6753),
            distance_km=3.0,
            duration_minutes=8.0
        )
        leg2 = RouteLeg(
            from_point=Point(lat=24.7300, lng=46.6753),
            to_point=Point(lat=24.7580, lng=46.6753),
            distance_km=2.0,
            duration_minutes=4.0
        )
        leg3 = RouteLeg(
            from_point=Point(lat=24.7580, lng=46.6753),
            to_point=Point(lat=24.8000, lng=46.6753),
            distance_km=4.5,
            duration_minutes=10.0
        )

        result = RouteResult(legs=[leg1, leg2, leg3])
        assert result.total_duration_minutes == 22.0  # 8.0 + 4.0 + 10.0


class TestRoutingProviderInterface:
    """Tests for RoutingProvider abstract interface"""

    def test_routing_provider_is_abstract(self):
        """RoutingProvider should be an abstract class"""
        with pytest.raises(TypeError):
            RoutingProvider()  # type: ignore

    def test_routing_provider_requires_get_travel_times(self):
        """Subclass must implement get_travel_times"""
        class IncompleteProvider(RoutingProvider):
            async def get_route(self, origin, waypoints, departure_time, optimize=False):
                return RouteResult()

        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_routing_provider_requires_get_route(self):
        """Subclass must implement get_route"""
        class IncompleteProvider(RoutingProvider):
            async def get_travel_times(self, origins, destinations, departure_time):
                return DistanceMatrixResult()

        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_complete_routing_provider_implementation(self):
        """Complete implementation should work"""
        class CompleteProvider(RoutingProvider):
            async def get_travel_times(self, origins, destinations, departure_time):
                return DistanceMatrixResult()

            async def get_route(self, origin, waypoints, departure_time, optimize=False):
                return RouteResult()

        provider = CompleteProvider()
        assert isinstance(provider, RoutingProvider)
