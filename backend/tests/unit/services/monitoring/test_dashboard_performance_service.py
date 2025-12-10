"""
Unit Tests for Dashboard Performance Service

Tests optimized dashboard functionality:
- Cache key generation
- Dashboard stats with caching
- Top couriers retrieval
- Cache invalidation
- Utilization calculations
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock

from app.services.dashboard_performance_service import (
    DashboardPerformanceService,
    dashboard_service,
)


# ==================== Fixtures ====================

@pytest.fixture
def service():
    """Create DashboardPerformanceService instance"""
    return DashboardPerformanceService()


@pytest.fixture
def mock_db():
    """Create mock database session"""
    return MagicMock()


@pytest.fixture
def mock_cache():
    """Mock cache manager"""
    with patch('app.services.dashboard_performance_service.cache_manager') as mock:
        mock.get.return_value = None  # Default cache miss
        yield mock


@pytest.fixture
def mock_courier_stats():
    """Mock courier statistics query result"""
    stats = MagicMock()
    stats.total = 100
    stats.active = 75
    stats.inactive = 15
    stats.on_leave = 5
    stats.onboarding = 3
    stats.suspended = 2
    stats.with_vehicle = 70
    stats.ajeer = 30
    stats.inhouse = 50
    stats.freelancer = 20
    stats.ecommerce = 40
    stats.food = 30
    stats.warehouse = 20
    stats.barq = 10
    return stats


@pytest.fixture
def mock_vehicle_stats():
    """Mock vehicle statistics query result"""
    stats = MagicMock()
    stats.total = 80
    stats.available = 20
    stats.assigned = 50
    stats.maintenance = 5
    stats.out_of_service = 5
    return stats


# ==================== Cache Key Tests ====================

class TestCacheKey:
    """Tests for cache key generation"""

    def test_make_cache_key(self, service):
        """Should create organization-scoped cache key"""
        key = service._make_cache_key(123, "dashboard_stats")
        assert key == "org_123:dashboard_stats"

    def test_make_cache_key_different_orgs(self, service):
        """Should create different keys for different orgs"""
        key1 = service._make_cache_key(1, "stats")
        key2 = service._make_cache_key(2, "stats")
        assert key1 != key2

    def test_make_cache_key_with_suffix(self, service):
        """Should include key suffix"""
        key = service._make_cache_key(1, "top_couriers_10")
        assert "top_couriers_10" in key


# ==================== Dashboard Stats Tests ====================

class TestGetDashboardStats:
    """Tests for get_dashboard_stats method"""

    def test_cache_hit(self, service, mock_db, mock_cache):
        """Should return cached stats when available"""
        cached_data = {"total_couriers": 100, "cached": True}
        mock_cache.get.return_value = cached_data

        result = service.get_dashboard_stats(mock_db, org_id=1)

        assert result == cached_data
        mock_cache.get.assert_called_once()

    def test_cache_miss_calculates_stats(self, service, mock_db, mock_cache, mock_courier_stats, mock_vehicle_stats):
        """Should calculate stats on cache miss"""
        mock_cache.get.return_value = None

        # Mock database queries
        mock_db.query.return_value.filter.return_value.one.side_effect = [
            mock_courier_stats,
            mock_vehicle_stats,
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50

        with patch.object(service, '_calculate_dashboard_stats', return_value={"calculated": True}) as mock_calc:
            result = service.get_dashboard_stats(mock_db, org_id=1)

        mock_calc.assert_called_once_with(mock_db, 1)
        mock_cache.set.assert_called_once()

    def test_stats_cached_with_correct_ttl(self, service, mock_db, mock_cache):
        """Should cache stats with correct TTL"""
        mock_cache.get.return_value = None

        with patch.object(service, '_calculate_dashboard_stats', return_value={"stats": True}):
            service.get_dashboard_stats(mock_db, org_id=1)

        # Verify cache set was called with correct TTL
        call_args = mock_cache.set.call_args
        assert call_args[0][3] == service.STATS_CACHE_TTL


# ==================== Calculate Dashboard Stats Tests ====================

class TestCalculateDashboardStats:
    """Tests for _calculate_dashboard_stats method"""

    def test_returns_complete_stats_structure(self, service, mock_db, mock_courier_stats, mock_vehicle_stats):
        """Should return complete stats structure"""
        mock_db.query.return_value.filter.return_value.one.side_effect = [
            mock_courier_stats,
            mock_vehicle_stats,
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50

        result = service._calculate_dashboard_stats(mock_db, org_id=1)

        # Verify required fields
        assert "total_couriers" in result
        assert "total_vehicles" in result
        assert "active_couriers" in result
        assert "courier_utilization" in result
        assert "vehicle_utilization" in result
        assert "sponsorship_breakdown" in result
        assert "project_breakdown" in result
        assert "insights" in result

    def test_utilization_calculations(self, service, mock_db, mock_courier_stats, mock_vehicle_stats):
        """Should calculate utilization percentages correctly"""
        mock_db.query.return_value.filter.return_value.one.side_effect = [
            mock_courier_stats,
            mock_vehicle_stats,
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50

        result = service._calculate_dashboard_stats(mock_db, org_id=1)

        # 75 active / 100 total = 75%
        assert result["courier_utilization"] == 75.0
        # 50 assigned / 80 total = 62.5%
        assert result["vehicle_utilization"] == 62.5

    def test_zero_division_protection(self, service, mock_db):
        """Should handle zero totals without division error"""
        zero_courier_stats = MagicMock()
        zero_courier_stats.total = 0
        zero_courier_stats.active = 0
        zero_courier_stats.inactive = 0
        zero_courier_stats.on_leave = 0
        zero_courier_stats.onboarding = 0
        zero_courier_stats.suspended = 0
        zero_courier_stats.with_vehicle = 0
        zero_courier_stats.ajeer = 0
        zero_courier_stats.inhouse = 0
        zero_courier_stats.freelancer = 0
        zero_courier_stats.ecommerce = 0
        zero_courier_stats.food = 0
        zero_courier_stats.warehouse = 0
        zero_courier_stats.barq = 0

        zero_vehicle_stats = MagicMock()
        zero_vehicle_stats.total = 0
        zero_vehicle_stats.available = 0
        zero_vehicle_stats.assigned = 0
        zero_vehicle_stats.maintenance = 0
        zero_vehicle_stats.out_of_service = 0

        mock_db.query.return_value.filter.return_value.one.side_effect = [
            zero_courier_stats,
            zero_vehicle_stats,
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0

        result = service._calculate_dashboard_stats(mock_db, org_id=1)

        assert result["courier_utilization"] == 0
        assert result["vehicle_utilization"] == 0

    def test_sponsorship_breakdown(self, service, mock_db, mock_courier_stats, mock_vehicle_stats):
        """Should include correct sponsorship breakdown"""
        mock_db.query.return_value.filter.return_value.one.side_effect = [
            mock_courier_stats,
            mock_vehicle_stats,
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50

        result = service._calculate_dashboard_stats(mock_db, org_id=1)

        assert result["sponsorship_breakdown"]["ajeer"] == 30
        assert result["sponsorship_breakdown"]["inhouse"] == 50
        assert result["sponsorship_breakdown"]["freelancer"] == 20

    def test_project_breakdown(self, service, mock_db, mock_courier_stats, mock_vehicle_stats):
        """Should include correct project breakdown"""
        mock_db.query.return_value.filter.return_value.one.side_effect = [
            mock_courier_stats,
            mock_vehicle_stats,
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50

        result = service._calculate_dashboard_stats(mock_db, org_id=1)

        assert result["project_breakdown"]["ecommerce"] == 40
        assert result["project_breakdown"]["food"] == 30
        assert result["project_breakdown"]["warehouse"] == 20
        assert result["project_breakdown"]["barq"] == 10

    def test_insights_fleet_health(self, service, mock_db, mock_courier_stats, mock_vehicle_stats):
        """Should determine fleet health correctly"""
        mock_db.query.return_value.filter.return_value.one.side_effect = [
            mock_courier_stats,
            mock_vehicle_stats,
        ]
        mock_db.query.return_value.filter.return_value.scalar.return_value = 50

        result = service._calculate_dashboard_stats(mock_db, org_id=1)

        # Vehicle utilization > 50%, so should be "good"
        assert result["insights"]["fleet_health"] == "good"


# ==================== Top Couriers Tests ====================

class TestGetTopCouriers:
    """Tests for get_top_couriers method"""

    def test_cache_hit(self, service, mock_db, mock_cache):
        """Should return cached top couriers"""
        cached_data = [{"rank": 1, "name": "Test Courier"}]
        mock_cache.get.return_value = cached_data

        result = service.get_top_couriers(mock_db, org_id=1, limit=5)

        assert result == cached_data

    def test_queries_active_couriers_only(self, service, mock_db, mock_cache):
        """Should only query active couriers"""
        mock_cache.get.return_value = None
        mock_courier = MagicMock()
        mock_courier.id = 1
        mock_courier.barq_id = 123
        mock_courier.full_name = "Test Courier"
        mock_courier.performance_score = Decimal("95.5")
        mock_courier.total_deliveries = 500
        mock_courier.city = "Riyadh"
        mock_courier.project_type = MagicMock()
        mock_courier.project_type.value = "ecommerce"

        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_courier]

        result = service.get_top_couriers(mock_db, org_id=1)

        assert len(result) == 1
        assert result[0]["name"] == "Test Courier"

    def test_respects_limit_parameter(self, service, mock_db, mock_cache):
        """Should respect limit parameter"""
        mock_cache.get.return_value = None
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        service.get_top_couriers(mock_db, org_id=1, limit=10)

        # Verify limit was applied
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.assert_called_with(10)

    def test_result_structure(self, service, mock_db, mock_cache):
        """Should return correct result structure"""
        mock_cache.get.return_value = None
        mock_courier = MagicMock()
        mock_courier.id = 1
        mock_courier.barq_id = 123
        mock_courier.full_name = "Top Courier"
        mock_courier.performance_score = Decimal("98.0")
        mock_courier.total_deliveries = 1000
        mock_courier.city = "Jeddah"
        mock_courier.project_type = MagicMock()
        mock_courier.project_type.value = "food"

        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_courier]

        result = service.get_top_couriers(mock_db, org_id=1)

        assert result[0]["rank"] == 1
        assert result[0]["id"] == 1
        assert result[0]["barq_id"] == 123
        assert result[0]["name"] == "Top Courier"
        assert result[0]["performance_score"] == 98.0
        assert result[0]["total_deliveries"] == 1000
        assert result[0]["city"] == "Jeddah"
        assert result[0]["project_type"] == "food"

    def test_handles_null_performance_score(self, service, mock_db, mock_cache):
        """Should handle null performance score"""
        mock_cache.get.return_value = None
        mock_courier = MagicMock()
        mock_courier.id = 1
        mock_courier.barq_id = 123
        mock_courier.full_name = "Test"
        mock_courier.performance_score = None
        mock_courier.total_deliveries = None
        mock_courier.city = None
        mock_courier.project_type = None

        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_courier]

        result = service.get_top_couriers(mock_db, org_id=1)

        assert result[0]["performance_score"] == 0
        assert result[0]["total_deliveries"] == 0

    def test_caches_results(self, service, mock_db, mock_cache):
        """Should cache results with correct TTL"""
        mock_cache.get.return_value = None
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        service.get_top_couriers(mock_db, org_id=1, limit=5)

        call_args = mock_cache.set.call_args
        assert call_args[0][3] == service.CHARTS_CACHE_TTL


# ==================== Cache Invalidation Tests ====================

class TestInvalidateDashboardCache:
    """Tests for invalidate_dashboard_cache method"""

    def test_invalidates_org_cache(self, service, mock_cache):
        """Should delete all cache entries for organization"""
        service.invalidate_dashboard_cache(org_id=123)

        mock_cache.delete_pattern.assert_called_once_with("dashboard", "org_123:*")

    def test_different_orgs_independent(self, service, mock_cache):
        """Should only invalidate specified org's cache"""
        service.invalidate_dashboard_cache(org_id=1)
        service.invalidate_dashboard_cache(org_id=2)

        calls = mock_cache.delete_pattern.call_args_list
        assert calls[0][0] == ("dashboard", "org_1:*")
        assert calls[1][0] == ("dashboard", "org_2:*")


# ==================== Cache TTL Constants Tests ====================

class TestCacheTTLConstants:
    """Tests for cache TTL constants"""

    def test_stats_cache_ttl(self, service):
        """Stats cache should be 5 minutes"""
        assert service.STATS_CACHE_TTL == 300

    def test_charts_cache_ttl(self, service):
        """Charts cache should be 10 minutes"""
        assert service.CHARTS_CACHE_TTL == 600

    def test_alerts_cache_ttl(self, service):
        """Alerts cache should be 3 minutes"""
        assert service.ALERTS_CACHE_TTL == 180


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have a singleton instance"""
        assert dashboard_service is not None

    def test_singleton_is_instance(self):
        """Should be a DashboardPerformanceService instance"""
        assert isinstance(dashboard_service, DashboardPerformanceService)
