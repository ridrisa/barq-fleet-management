"""
Unit Tests for BigQuery Client Service

Tests BigQuery integration functionality:
- Client initialization
- Query execution
- Courier data retrieval
- Performance metrics
- Health checks
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Dict, List

from app.services.integrations.bigquery_client import BigQueryClient, bigquery_client


# ==================== Fixtures ====================

@pytest.fixture
def mock_bigquery():
    """Mock BigQuery client"""
    with patch('app.services.integrations.bigquery_client.bigquery') as mock_bq:
        yield mock_bq


@pytest.fixture
def client(mock_bigquery):
    """Create BigQueryClient instance with mocked dependencies"""
    with patch('app.services.integrations.bigquery_client.settings') as mock_settings:
        mock_settings.BIGQUERY_PROJECT_ID = "test-project"
        mock_settings.BIGQUERY_DATASET = "test_dataset"
        mock_settings.BIGQUERY_CREDENTIALS_PATH = None

        client = BigQueryClient()
        # Mock the client property
        client._client = MagicMock()
        return client


# ==================== Initialization Tests ====================

class TestBigQueryClientInit:
    """Tests for BigQueryClient initialization"""

    def test_init_default_values(self, mock_bigquery):
        """Should initialize with default values from settings"""
        with patch('app.services.integrations.bigquery_client.settings') as mock_settings:
            mock_settings.BIGQUERY_PROJECT_ID = "my-project"
            mock_settings.BIGQUERY_DATASET = "my_dataset"
            mock_settings.BIGQUERY_CREDENTIALS_PATH = None

            client = BigQueryClient()

            assert client._project_id == "my-project"
            assert client._dataset == "my_dataset"
            assert client._client is None


class TestTableRef:
    """Tests for table_ref property"""

    def test_table_ref_format(self, client):
        """Should return proper table reference"""
        client._project_id = "test-project"
        client._dataset = "test_dataset"

        assert client.table_ref == "test-project.test_dataset.ultimate"


# ==================== Query Tests ====================

class TestQuery:
    """Tests for query method"""

    def test_query_simple(self, client):
        """Should execute simple query"""
        mock_result = [{"count": 100}]
        client._client.query.return_value.result.return_value = [MagicMock(**{"__iter__": lambda s: iter(mock_result)})]

        # Mock row iteration
        mock_rows = [MagicMock()]
        mock_rows[0].__iter__ = lambda s: iter([("count", 100)])
        mock_rows[0].items = lambda: [("count", 100)]
        client._client.query.return_value.result.return_value = mock_rows

        result = client.query("SELECT COUNT(*) FROM table")

        client._client.query.assert_called_once()

    def test_query_with_params(self, client):
        """Should execute query with parameters"""
        mock_rows = []
        client._client.query.return_value.result.return_value = mock_rows

        result = client.query(
            "SELECT * FROM table WHERE status = @status",
            params={"status": "Active"}
        )

        client._client.query.assert_called_once()


# ==================== Get Courier Tests ====================

class TestGetCourierByBarqId:
    """Tests for get_courier_by_barq_id method"""

    def test_get_courier_found(self, client):
        """Should return courier data when found"""
        mock_row = MagicMock()
        mock_row.__iter__ = lambda s: iter([("BARQ_ID", 123), ("Name", "Test Courier")])
        mock_row.items = lambda: [("BARQ_ID", 123), ("Name", "Test Courier")]
        client._client.query.return_value.result.return_value = [mock_row]

        result = client.get_courier_by_barq_id(123)

        assert result is not None

    def test_get_courier_not_found(self, client):
        """Should return None when courier not found"""
        client._client.query.return_value.result.return_value = []

        result = client.get_courier_by_barq_id(999)

        assert result is None


# ==================== Get All Couriers Tests ====================

class TestGetAllCouriers:
    """Tests for get_all_couriers method"""

    def test_get_all_couriers_no_filters(self, client):
        """Should get all couriers without filters"""
        client._client.query.return_value.result.return_value = []

        result = client.get_all_couriers()

        client._client.query.assert_called_once()

    def test_get_all_couriers_with_status_filter(self, client):
        """Should filter by status"""
        client._client.query.return_value.result.return_value = []

        result = client.get_all_couriers(status="Active")

        client._client.query.assert_called_once()

    def test_get_all_couriers_with_city_filter(self, client):
        """Should filter by city"""
        client._client.query.return_value.result.return_value = []

        result = client.get_all_couriers(city="Riyadh")

        client._client.query.assert_called_once()

    def test_get_all_couriers_pagination(self, client):
        """Should respect pagination parameters"""
        client._client.query.return_value.result.return_value = []

        result = client.get_all_couriers(skip=20, limit=10)

        client._client.query.assert_called_once()


# ==================== Performance Metrics Tests ====================

class TestGetPerformanceMetrics:
    """Tests for get_performance_metrics method"""

    def test_get_performance_metrics(self, client):
        """Should get performance metrics"""
        client._client.query.return_value.result.return_value = []

        result = client.get_performance_metrics()

        client._client.query.assert_called_once()

    def test_get_performance_metrics_custom_status(self, client):
        """Should filter by custom status"""
        client._client.query.return_value.result.return_value = []

        result = client.get_performance_metrics(status="Inactive")

        client._client.query.assert_called_once()


# ==================== Performance Summary Tests ====================

class TestGetPerformanceSummary:
    """Tests for get_performance_summary method"""

    def test_get_performance_summary_success(self, client):
        """Should return summary statistics"""
        mock_row = MagicMock()
        mock_row.__iter__ = lambda s: iter([
            ("total_couriers", 100),
            ("active_couriers", 80),
        ])
        mock_row.items = lambda: [
            ("total_couriers", 100),
            ("active_couriers", 80),
        ]
        client._client.query.return_value.result.return_value = [mock_row]

        result = client.get_performance_summary()

        assert result is not None

    def test_get_performance_summary_empty(self, client):
        """Should return empty dict when no data"""
        client._client.query.return_value.result.return_value = []

        result = client.get_performance_summary()

        assert result == {}


# ==================== City Breakdown Tests ====================

class TestGetCityBreakdown:
    """Tests for get_city_breakdown method"""

    def test_get_city_breakdown(self, client):
        """Should return breakdown by city"""
        client._client.query.return_value.result.return_value = []

        result = client.get_city_breakdown()

        assert isinstance(result, list)


# ==================== Platform Breakdown Tests ====================

class TestGetPlatformBreakdown:
    """Tests for get_platform_breakdown method"""

    def test_get_platform_breakdown(self, client):
        """Should return breakdown by platform"""
        client._client.query.return_value.result.return_value = []

        result = client.get_platform_breakdown()

        assert isinstance(result, list)


# ==================== Search Couriers Tests ====================

class TestSearchCouriers:
    """Tests for search_couriers method"""

    def test_search_by_name(self, client):
        """Should search by courier name"""
        client._client.query.return_value.result.return_value = []

        result = client.search_couriers("Ahmad")

        client._client.query.assert_called_once()

    def test_search_with_limit(self, client):
        """Should respect limit parameter"""
        client._client.query.return_value.result.return_value = []

        result = client.search_couriers("Ahmad", limit=5)

        client._client.query.assert_called_once()


# ==================== Payroll Data Tests ====================

class TestGetCourierPayrollData:
    """Tests for get_courier_payroll_data method"""

    def test_get_payroll_data(self, client):
        """Should get payroll data for period"""
        client._client.query.return_value.result.return_value = []

        result = client.get_courier_payroll_data(
            start_date="2025-01-25",
            end_date="2025-02-24"
        )

        assert isinstance(result, list)

    def test_get_payroll_data_with_barq_ids(self, client):
        """Should filter by BARQ IDs"""
        client._client.query.return_value.result.return_value = []

        result = client.get_courier_payroll_data(
            start_date="2025-01-25",
            end_date="2025-02-24",
            barq_ids=[123, 456, 789]
        )

        client._client.query.assert_called_once()


# ==================== Targets Tests ====================

class TestGetCourierTargets:
    """Tests for get_courier_targets method"""

    def test_get_targets_success(self, client):
        """Should get targets for month"""
        client._client.query.return_value.result.return_value = []

        result = client.get_courier_targets(month=1, year=2025)

        assert isinstance(result, list)

    def test_get_targets_error(self, client):
        """Should return empty list on error"""
        client._client.query.side_effect = Exception("Query failed")

        result = client.get_courier_targets(month=1, year=2025)

        assert result == []


# ==================== Health Check Tests ====================

class TestHealthCheck:
    """Tests for health_check method"""

    def test_health_check_healthy(self, client):
        """Should return healthy status"""
        mock_row = MagicMock()
        mock_row.__getitem__ = lambda s, k: 100
        client._client.query.return_value.result.return_value = [mock_row]

        result = client.health_check()

        assert result["status"] == "healthy"

    def test_health_check_unhealthy(self, client):
        """Should return unhealthy on error"""
        client._client.query.side_effect = Exception("Connection failed")

        result = client.health_check()

        assert result["status"] == "unhealthy"
        assert "error" in result


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have singleton instance"""
        assert bigquery_client is not None
