"""
Unit Tests for Google Routing Service

Tests the GoogleRoutingProvider implementation:
- Caching mechanisms
- API fallback to Haversine estimation
- Distance matrix calculations
- Route planning
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.services.dispatch.google_routing import (
    GoogleRoutingProvider,
    get_google_routing_provider,
)
from app.services.dispatch.routing import (
    DistanceMatrixResult,
    RouteResult,
)
from app.services.dispatch.types import Point


class TestGoogleRoutingProviderInit:
    """Tests for GoogleRoutingProvider initialization"""

    def test_init_with_defaults(self):
        """Provider should initialize with default values"""
        provider = GoogleRoutingProvider()

        assert provider.api_key == "" or provider.api_key is not None
        assert provider.cache_ttl_ms == 20 * 60 * 1000  # 20 minutes in ms
        assert provider.timeout == 30.0
        assert provider._cache == {}

    def test_init_with_custom_api_key(self):
        """Provider should accept custom API key"""
        provider = GoogleRoutingProvider(api_key="test_api_key")
        assert provider.api_key == "test_api_key"

    def test_init_with_custom_cache_ttl(self):
        """Provider should accept custom cache TTL"""
        provider = GoogleRoutingProvider(cache_ttl_minutes=30)
        assert provider.cache_ttl_ms == 30 * 60 * 1000

    def test_init_with_custom_timeout(self):
        """Provider should accept custom timeout"""
        provider = GoogleRoutingProvider(timeout_seconds=60.0)
        assert provider.timeout == 60.0


class TestCellSnapping:
    """Tests for cell-based caching"""

    def test_snap_cell_rounds_coordinates(self):
        """Snap cell should round to 3 decimal places"""
        provider = GoogleRoutingProvider()
        point = Point(lat=24.71364789, lng=46.67531234)

        cell = provider._snap_cell(point)
        assert cell == "24.714,46.675"

    def test_snap_cell_handles_negative_coords(self):
        """Snap cell should handle negative coordinates"""
        provider = GoogleRoutingProvider()
        point = Point(lat=-33.8651, lng=151.2099)

        cell = provider._snap_cell(point)
        assert cell == "-33.865,151.210"

    def test_snap_cell_consistent(self):
        """Same point should always produce same cell"""
        provider = GoogleRoutingProvider()
        point = Point(lat=24.7136, lng=46.6753)

        cell1 = provider._snap_cell(point)
        cell2 = provider._snap_cell(point)
        assert cell1 == cell2


class TestTimeBucketing:
    """Tests for time-based cache bucketing"""

    def test_time_bucket_key_format(self):
        """Time bucket should be based on 15-minute intervals"""
        provider = GoogleRoutingProvider()
        time1 = datetime(2025, 1, 15, 12, 0, 0)

        key = provider._time_bucket_key(time1)
        assert isinstance(key, str)
        assert key.isdigit()

    def test_same_bucket_for_close_times(self):
        """Times within 15 minutes should produce same bucket"""
        provider = GoogleRoutingProvider()
        time1 = datetime(2025, 1, 15, 12, 0, 0)
        time2 = datetime(2025, 1, 15, 12, 10, 0)

        key1 = provider._time_bucket_key(time1)
        key2 = provider._time_bucket_key(time2)
        assert key1 == key2

    def test_different_bucket_for_distant_times(self):
        """Times more than 15 minutes apart should produce different buckets"""
        provider = GoogleRoutingProvider()
        time1 = datetime(2025, 1, 15, 12, 0, 0)
        time2 = datetime(2025, 1, 15, 12, 20, 0)

        key1 = provider._time_bucket_key(time1)
        key2 = provider._time_bucket_key(time2)
        assert key1 != key2


class TestCacheKeyBuilding:
    """Tests for cache key construction"""

    def test_build_cache_key_format(self):
        """Cache key should combine origin, destination, and time bucket"""
        provider = GoogleRoutingProvider()
        origin = Point(lat=24.7136, lng=46.6753)
        destination = Point(lat=24.7580, lng=46.7000)
        departure_time = datetime(2025, 1, 15, 12, 0, 0)

        key = provider._build_cache_key(origin, destination, departure_time)

        # Key should contain origin cell, destination cell, and time bucket
        assert "|" in key
        parts = key.split("|")
        assert len(parts) == 3

    def test_same_inputs_produce_same_key(self):
        """Same inputs should always produce same cache key"""
        provider = GoogleRoutingProvider()
        origin = Point(lat=24.7136, lng=46.6753)
        destination = Point(lat=24.7580, lng=46.7000)
        departure_time = datetime(2025, 1, 15, 12, 0, 0)

        key1 = provider._build_cache_key(origin, destination, departure_time)
        key2 = provider._build_cache_key(origin, destination, departure_time)
        assert key1 == key2

    def test_different_origins_produce_different_keys(self):
        """Different origins should produce different keys"""
        provider = GoogleRoutingProvider()
        origin1 = Point(lat=24.7136, lng=46.6753)
        origin2 = Point(lat=24.8000, lng=46.6753)
        destination = Point(lat=24.7580, lng=46.7000)
        departure_time = datetime(2025, 1, 15, 12, 0, 0)

        key1 = provider._build_cache_key(origin1, destination, departure_time)
        key2 = provider._build_cache_key(origin2, destination, departure_time)
        assert key1 != key2


class TestCacheOperations:
    """Tests for cache get/set operations"""

    def test_get_from_empty_cache_returns_none(self):
        """Getting from empty cache should return None"""
        provider = GoogleRoutingProvider()
        origin = Point(lat=24.7136, lng=46.6753)
        destination = Point(lat=24.7580, lng=46.7000)
        departure_time = datetime.now()

        result = provider._get_from_cache(origin, destination, departure_time)
        assert result is None

    def test_set_and_get_cache(self):
        """Should be able to set and retrieve from cache"""
        provider = GoogleRoutingProvider()
        origin = Point(lat=24.7136, lng=46.6753)
        destination = Point(lat=24.7580, lng=46.7000)
        departure_time = datetime.now()

        provider._set_cache(origin, destination, departure_time, 5.0, 12.0)

        result = provider._get_from_cache(origin, destination, departure_time)
        assert result is not None
        assert result["distance_km"] == 5.0
        assert result["duration_minutes"] == 12.0

    def test_cache_expiry(self):
        """Expired cache entries should not be returned"""
        provider = GoogleRoutingProvider(cache_ttl_minutes=0)  # Immediate expiry
        origin = Point(lat=24.7136, lng=46.6753)
        destination = Point(lat=24.7580, lng=46.7000)
        departure_time = datetime.now()

        provider._set_cache(origin, destination, departure_time, 5.0, 12.0)

        # Force expiry by setting expires_at to past
        key = provider._build_cache_key(origin, destination, departure_time)
        provider._cache[key]["expires_at"] = datetime.now().timestamp() * 1000 - 1000

        result = provider._get_from_cache(origin, destination, departure_time)
        assert result is None


class TestHaversineEstimation:
    """Tests for Haversine-based fallback estimation"""

    def test_estimate_with_haversine_empty_lists(self):
        """Empty lists should return empty result"""
        provider = GoogleRoutingProvider()
        result = provider._estimate_with_haversine([], [])

        assert result.durations_minutes == []
        assert result.distances_km == []

    def test_estimate_with_haversine_single_pair(self):
        """Single origin-destination pair"""
        provider = GoogleRoutingProvider()
        origins = [Point(lat=24.7136, lng=46.6753)]
        destinations = [Point(lat=24.7580, lng=46.6753)]

        result = provider._estimate_with_haversine(origins, destinations)

        assert len(result.distances_km) == 1
        assert len(result.distances_km[0]) == 1
        assert result.distances_km[0][0] > 0

    def test_estimate_with_haversine_custom_speed(self):
        """Custom speed should affect duration calculation"""
        provider = GoogleRoutingProvider()
        origins = [Point(lat=24.7136, lng=46.6753)]
        destinations = [Point(lat=24.7580, lng=46.6753)]  # ~5km

        result_slow = provider._estimate_with_haversine(origins, destinations, speed_kmh=10.0)
        result_fast = provider._estimate_with_haversine(origins, destinations, speed_kmh=50.0)

        # Slower speed should result in longer duration
        assert result_slow.durations_minutes[0][0] > result_fast.durations_minutes[0][0]

    def test_estimate_route_with_haversine(self):
        """Test route estimation fallback"""
        provider = GoogleRoutingProvider()
        origin = Point(lat=24.7136, lng=46.6753)
        waypoints = [
            Point(lat=24.7300, lng=46.6753),
            Point(lat=24.7580, lng=46.6753),
        ]

        result = provider._estimate_route_with_haversine(origin, waypoints)

        assert len(result.legs) == 2
        assert result.polyline is None
        assert result.total_distance_km > 0
        assert result.total_duration_minutes > 0


class TestGetTravelTimes:
    """Tests for get_travel_times method"""

    @pytest.mark.asyncio
    async def test_get_travel_times_empty_origins(self):
        """Empty origins should return empty result"""
        provider = GoogleRoutingProvider(api_key="test_key")
        result = await provider.get_travel_times([], [Point(lat=0, lng=0)], datetime.now())

        assert result.durations_minutes == []
        assert result.distances_km == []

    @pytest.mark.asyncio
    async def test_get_travel_times_empty_destinations(self):
        """Empty destinations should return empty result"""
        provider = GoogleRoutingProvider(api_key="test_key")
        result = await provider.get_travel_times([Point(lat=0, lng=0)], [], datetime.now())

        assert result.durations_minutes == []
        assert result.distances_km == []

    @pytest.mark.asyncio
    async def test_get_travel_times_uses_cache(self):
        """Cached values should be used when available"""
        provider = GoogleRoutingProvider(api_key="test_key")
        origin = Point(lat=24.7136, lng=46.6753)
        destination = Point(lat=24.7580, lng=46.6753)
        departure_time = datetime.now()

        # Pre-populate cache
        provider._set_cache(origin, destination, departure_time, 5.0, 12.0)

        result = await provider.get_travel_times([origin], [destination], departure_time)

        assert result.distances_km[0][0] == 5.0
        assert result.durations_minutes[0][0] == 12.0

    @pytest.mark.asyncio
    async def test_get_travel_times_fallback_no_api_key(self):
        """Should use Haversine fallback when no API key"""
        provider = GoogleRoutingProvider(api_key="")
        origins = [Point(lat=24.7136, lng=46.6753)]
        destinations = [Point(lat=24.7580, lng=46.6753)]

        result = await provider.get_travel_times(origins, destinations, datetime.now())

        # Should still return valid estimates
        assert len(result.distances_km) == 1
        assert len(result.durations_minutes) == 1
        assert result.distances_km[0][0] > 0


class TestGetRoute:
    """Tests for get_route method"""

    @pytest.mark.asyncio
    async def test_get_route_empty_waypoints(self):
        """Empty waypoints should return empty result"""
        provider = GoogleRoutingProvider(api_key="test_key")
        origin = Point(lat=24.7136, lng=46.6753)

        result = await provider.get_route(origin, [], datetime.now())

        assert result.legs == []
        assert result.polyline is None

    @pytest.mark.asyncio
    async def test_get_route_fallback_no_api_key(self):
        """Should use Haversine fallback when no API key"""
        provider = GoogleRoutingProvider(api_key="")
        origin = Point(lat=24.7136, lng=46.6753)
        waypoints = [Point(lat=24.7580, lng=46.6753)]

        result = await provider.get_route(origin, waypoints, datetime.now())

        # Should still return valid route estimate
        assert len(result.legs) == 1
        assert result.polyline is None
        assert result.total_distance_km > 0


class TestSingleton:
    """Tests for singleton instance"""

    def test_get_google_routing_provider_returns_instance(self):
        """Should return a GoogleRoutingProvider instance"""
        provider = get_google_routing_provider()
        assert isinstance(provider, GoogleRoutingProvider)

    def test_get_google_routing_provider_returns_same_instance(self):
        """Should return the same instance on multiple calls"""
        provider1 = get_google_routing_provider()
        provider2 = get_google_routing_provider()
        assert provider1 is provider2
