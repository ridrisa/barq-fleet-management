"""
Unit Tests for System Monitoring Service

Tests system monitoring functionality:
- Health status checks
- Database health
- System resources (CPU, memory, disk)
- Application health
- System info
- Uptime tracking
- Performance metrics
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, PropertyMock

from app.services.system_monitoring_service import SystemMonitoringService, system_monitoring_service


# ==================== Fixtures ====================

@pytest.fixture
def service():
    """Create SystemMonitoringService instance"""
    return SystemMonitoringService()


@pytest.fixture
def mock_db():
    """Create mock database session"""
    return MagicMock()


@pytest.fixture
def mock_psutil():
    """Mock psutil module"""
    with patch('app.services.system_monitoring_service.psutil') as mock:
        # CPU
        mock.cpu_percent.return_value = 45.0
        mock.cpu_count.return_value = 8

        # Memory
        mock_memory = MagicMock()
        mock_memory.percent = 60.0
        mock_memory.available = 8 * (1024**3)  # 8 GB
        mock_memory.total = 16 * (1024**3)  # 16 GB
        mock.virtual_memory.return_value = mock_memory

        # Disk
        mock_disk = MagicMock()
        mock_disk.percent = 50.0
        mock_disk.free = 100 * (1024**3)  # 100 GB
        mock_disk.total = 500 * (1024**3)  # 500 GB
        mock.disk_usage.return_value = mock_disk

        yield mock


# ==================== Initialization Tests ====================

class TestInit:
    """Tests for service initialization"""

    def test_start_time_set(self, service):
        """Should set start time on initialization"""
        assert hasattr(service, 'start_time')
        assert isinstance(service.start_time, datetime)

    def test_start_time_is_recent(self, service):
        """Start time should be recent"""
        now = datetime.utcnow()
        assert (now - service.start_time).total_seconds() < 60


# ==================== Health Status Tests ====================

class TestGetHealthStatus:
    """Tests for get_health_status method"""

    def test_returns_complete_structure(self, service, mock_db, mock_psutil):
        """Should return complete health structure"""
        mock_db.execute.return_value.fetchone.return_value = ["10 MB"]
        mock_db.execute.return_value.scalar.return_value = 5

        result = service.get_health_status(mock_db)

        assert "status" in result
        assert "timestamp" in result
        assert "uptime_seconds" in result
        assert "components" in result
        assert "database" in result["components"]
        assert "system" in result["components"]
        assert "application" in result["components"]

    def test_healthy_status(self, service, mock_db, mock_psutil):
        """Should return healthy status"""
        mock_db.execute.return_value.fetchone.return_value = ["10 MB"]
        mock_db.execute.return_value.scalar.return_value = 5
        mock_db.query.return_value.scalar.return_value = 100

        result = service.get_health_status(mock_db)

        assert result["status"] == "healthy"

    def test_includes_uptime(self, service, mock_db, mock_psutil):
        """Should include uptime in seconds"""
        mock_db.execute.return_value.fetchone.return_value = ["10 MB"]
        mock_db.execute.return_value.scalar.return_value = 5
        mock_db.query.return_value.scalar.return_value = 100

        result = service.get_health_status(mock_db)

        assert result["uptime_seconds"] >= 0


# ==================== Database Health Tests ====================

class TestCheckDatabaseHealth:
    """Tests for _check_database_health method"""

    def test_healthy_database(self, service, mock_db):
        """Should return healthy for working database"""
        mock_db.execute.return_value.fetchone.return_value = ["50 MB"]
        mock_db.execute.return_value.scalar.return_value = 10

        result = service._check_database_health(mock_db)

        assert result["status"] == "healthy"
        assert "response_time_ms" in result
        assert "database_size" in result
        assert "active_connections" in result

    def test_database_response_time(self, service, mock_db):
        """Should measure response time"""
        mock_db.execute.return_value.fetchone.return_value = ["50 MB"]
        mock_db.execute.return_value.scalar.return_value = 10

        result = service._check_database_health(mock_db)

        assert result["response_time_ms"] >= 0

    def test_database_error_unhealthy(self, service, mock_db):
        """Should return unhealthy on database error"""
        mock_db.execute.side_effect = Exception("Connection failed")

        result = service._check_database_health(mock_db)

        assert result["status"] == "unhealthy"
        assert "error" in result


# ==================== System Resources Tests ====================

class TestCheckSystemResources:
    """Tests for _check_system_resources method"""

    def test_healthy_resources(self, service, mock_psutil):
        """Should return healthy for normal resource usage"""
        result = service._check_system_resources()

        assert result["status"] == "healthy"
        assert "cpu" in result
        assert "memory" in result
        assert "disk" in result

    def test_cpu_metrics(self, service, mock_psutil):
        """Should include CPU metrics"""
        result = service._check_system_resources()

        assert result["cpu"]["usage_percent"] == 45.0
        assert result["cpu"]["core_count"] == 8

    def test_memory_metrics(self, service, mock_psutil):
        """Should include memory metrics"""
        result = service._check_system_resources()

        assert result["memory"]["usage_percent"] == 60.0
        assert result["memory"]["available_gb"] == 8.0
        assert result["memory"]["total_gb"] == 16.0

    def test_disk_metrics(self, service, mock_psutil):
        """Should include disk metrics"""
        result = service._check_system_resources()

        assert result["disk"]["usage_percent"] == 50.0
        assert result["disk"]["free_gb"] == 100.0
        assert result["disk"]["total_gb"] == 500.0

    def test_warning_high_cpu(self, service, mock_psutil):
        """Should warn on high CPU usage"""
        mock_psutil.cpu_percent.return_value = 85.0

        result = service._check_system_resources()

        assert result["status"] == "warning"
        assert any("CPU" in w for w in result["warnings"])

    def test_warning_high_memory(self, service, mock_psutil):
        """Should warn on high memory usage"""
        mock_memory = MagicMock()
        mock_memory.percent = 90.0
        mock_memory.available = 2 * (1024**3)
        mock_memory.total = 16 * (1024**3)
        mock_psutil.virtual_memory.return_value = mock_memory

        result = service._check_system_resources()

        assert result["status"] == "warning"
        assert any("memory" in w for w in result["warnings"])

    def test_warning_low_disk(self, service, mock_psutil):
        """Should warn on low disk space"""
        mock_disk = MagicMock()
        mock_disk.percent = 90.0
        mock_disk.free = 50 * (1024**3)
        mock_disk.total = 500 * (1024**3)
        mock_psutil.disk_usage.return_value = mock_disk

        result = service._check_system_resources()

        assert result["status"] == "warning"
        assert any("disk" in w for w in result["warnings"])

    def test_error_on_exception(self, service, mock_psutil):
        """Should return error status on exception"""
        mock_psutil.cpu_percent.side_effect = Exception("Failed to get CPU")

        result = service._check_system_resources()

        assert result["status"] == "error"
        assert "error" in result


# ==================== Application Health Tests ====================

class TestCheckApplicationHealth:
    """Tests for _check_application_health method"""

    def test_healthy_application(self, service, mock_db):
        """Should return healthy for working application"""
        mock_db.query.return_value.scalar.side_effect = [100, 50, 30]

        result = service._check_application_health(mock_db)

        assert result["status"] == "healthy"
        assert "metrics" in result
        assert "uptime_seconds" in result

    def test_entity_counts(self, service, mock_db):
        """Should include entity counts"""
        mock_db.query.return_value.scalar.side_effect = [100, 50, 30]

        result = service._check_application_health(mock_db)

        assert result["metrics"]["total_users"] == 100
        assert result["metrics"]["total_couriers"] == 50
        assert result["metrics"]["total_vehicles"] == 30

    def test_handles_null_counts(self, service, mock_db):
        """Should handle null counts"""
        mock_db.query.return_value.scalar.side_effect = [None, None, None]

        result = service._check_application_health(mock_db)

        assert result["metrics"]["total_users"] == 0
        assert result["metrics"]["total_couriers"] == 0
        assert result["metrics"]["total_vehicles"] == 0

    def test_unhealthy_on_error(self, service, mock_db):
        """Should return unhealthy on error"""
        mock_db.query.side_effect = Exception("Query failed")

        result = service._check_application_health(mock_db)

        assert result["status"] == "unhealthy"
        assert "error" in result


# ==================== System Info Tests ====================

class TestGetSystemInfo:
    """Tests for get_system_info method"""

    def test_returns_system_info(self, service):
        """Should return system information"""
        with patch('app.services.system_monitoring_service.platform') as mock_platform:
            mock_platform.system.return_value = "Linux"
            mock_platform.release.return_value = "5.15.0"
            mock_platform.version.return_value = "#1 SMP"
            mock_platform.machine.return_value = "x86_64"
            mock_platform.processor.return_value = "Intel"
            mock_platform.python_version.return_value = "3.11.0"
            mock_platform.node.return_value = "server1"

            result = service.get_system_info()

        assert result["platform"] == "Linux"
        assert result["platform_release"] == "5.15.0"
        assert result["architecture"] == "x86_64"
        assert result["python_version"] == "3.11.0"
        assert result["hostname"] == "server1"

    def test_includes_all_fields(self, service):
        """Should include all system info fields"""
        result = service.get_system_info()

        assert "platform" in result
        assert "platform_release" in result
        assert "platform_version" in result
        assert "architecture" in result
        assert "processor" in result
        assert "python_version" in result
        assert "hostname" in result


# ==================== Uptime Tests ====================

class TestGetUptime:
    """Tests for get_uptime method"""

    def test_returns_uptime_info(self, service):
        """Should return uptime information"""
        result = service.get_uptime()

        assert "started_at" in result
        assert "current_time" in result
        assert "uptime_seconds" in result
        assert "uptime_hours" in result
        assert "uptime_days" in result
        assert "uptime_human" in result

    def test_uptime_calculation(self, service):
        """Should calculate uptime correctly"""
        # Set a known start time
        service.start_time = datetime.utcnow() - timedelta(hours=2)

        result = service.get_uptime()

        # Should be approximately 2 hours (7200 seconds)
        assert 7100 < result["uptime_seconds"] < 7300
        assert 1.9 < result["uptime_hours"] < 2.1

    def test_uptime_days_calculation(self, service):
        """Should calculate uptime days correctly"""
        service.start_time = datetime.utcnow() - timedelta(days=5)

        result = service.get_uptime()

        assert result["uptime_days"] == 5

    def test_human_readable_format(self, service):
        """Should provide human readable uptime"""
        service.start_time = datetime.utcnow() - timedelta(hours=1, minutes=30)

        result = service.get_uptime()

        # Should be in format like "1:30:00"
        assert ":" in result["uptime_human"]


# ==================== Performance Metrics Tests ====================

class TestGetPerformanceMetrics:
    """Tests for get_performance_metrics method"""

    def test_returns_metrics(self, service, mock_db, mock_psutil):
        """Should return performance metrics"""
        mock_db.execute.return_value = MagicMock()

        result = service.get_performance_metrics(mock_db)

        assert "database" in result
        assert "system" in result

    def test_database_query_metrics(self, service, mock_db, mock_psutil):
        """Should include database query metrics"""
        mock_db.execute.return_value = MagicMock()

        result = service.get_performance_metrics(mock_db)

        assert "avg_query_time_ms" in result["database"]
        assert "min_query_time_ms" in result["database"]
        assert "max_query_time_ms" in result["database"]

    def test_system_metrics_included(self, service, mock_db, mock_psutil):
        """Should include system metrics"""
        mock_db.execute.return_value = MagicMock()

        result = service.get_performance_metrics(mock_db)

        assert "cpu" in result["system"]
        assert "memory" in result["system"]
        assert "disk" in result["system"]

    def test_error_handling(self, service, mock_db, mock_psutil):
        """Should handle errors gracefully"""
        mock_db.execute.side_effect = Exception("Query failed")

        result = service.get_performance_metrics(mock_db)

        assert "error" in result
        assert "message" in result


# ==================== Thresholds Tests ====================

class TestResourceThresholds:
    """Tests for resource threshold behavior"""

    def test_cpu_threshold_80(self, service, mock_psutil):
        """CPU warning should trigger at 80%"""
        mock_psutil.cpu_percent.return_value = 79.0
        result1 = service._check_system_resources()

        mock_psutil.cpu_percent.return_value = 81.0
        result2 = service._check_system_resources()

        assert result1["status"] == "healthy"
        assert result2["status"] == "warning"

    def test_memory_threshold_85(self, service, mock_psutil):
        """Memory warning should trigger at 85%"""
        mock_memory = MagicMock()
        mock_memory.available = 4 * (1024**3)
        mock_memory.total = 16 * (1024**3)

        mock_memory.percent = 84.0
        mock_psutil.virtual_memory.return_value = mock_memory
        result1 = service._check_system_resources()

        mock_memory.percent = 86.0
        result2 = service._check_system_resources()

        assert result1["status"] == "healthy"
        assert result2["status"] == "warning"

    def test_disk_threshold_85(self, service, mock_psutil):
        """Disk warning should trigger at 85%"""
        mock_disk = MagicMock()
        mock_disk.free = 100 * (1024**3)
        mock_disk.total = 500 * (1024**3)

        mock_disk.percent = 84.0
        mock_psutil.disk_usage.return_value = mock_disk
        result1 = service._check_system_resources()

        mock_disk.percent = 86.0
        result2 = service._check_system_resources()

        assert result1["status"] == "healthy"
        assert result2["status"] == "warning"


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have a singleton instance"""
        assert system_monitoring_service is not None

    def test_singleton_is_instance(self):
        """Should be a SystemMonitoringService instance"""
        assert isinstance(system_monitoring_service, SystemMonitoringService)

    def test_singleton_has_start_time(self):
        """Singleton should have start time set"""
        assert hasattr(system_monitoring_service, 'start_time')
