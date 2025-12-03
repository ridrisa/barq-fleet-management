"""System Monitoring and Health Check Service

Provides comprehensive system monitoring:
- Health checks
- Performance metrics
- Error tracking
- Resource usage monitoring
- Uptime tracking
"""

import platform
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import psutil
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.models.fleet.courier import Courier
from app.models.fleet.vehicle import Vehicle
from app.models.user import User


class SystemMonitoringService:
    """
    Service for system monitoring and health checks

    Monitors:
    - Database health
    - System resources (CPU, memory, disk)
    - Application uptime
    - API response times
    - Error rates
    """

    def __init__(self):
        self.start_time = datetime.utcnow()

    def get_health_status(self, db: Session) -> Dict[str, Any]:
        """
        Get comprehensive health status

        Returns:
            Dictionary with health status for all components
        """
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "components": {
                "database": self._check_database_health(db),
                "system": self._check_system_resources(),
                "application": self._check_application_health(db),
            },
        }

    def _check_database_health(self, db: Session) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            # Test database connection
            start_time = datetime.utcnow()
            db.execute(text("SELECT 1"))
            response_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Get database size
            size_query = text(
                """
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """
            )
            size_result = db.execute(size_query).fetchone()
            database_size = size_result[0] if size_result else "Unknown"

            # Get active connections
            connections_query = text(
                """
                SELECT count(*) FROM pg_stat_activity
                WHERE datname = current_database()
            """
            )
            active_connections = db.execute(connections_query).scalar()

            return {
                "status": "healthy",
                "response_time_ms": round(response_time_ms, 2),
                "database_size": database_size,
                "active_connections": active_connections,
                "message": "Database is operational",
            }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "message": "Database connection failed"}

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)

            # Determine health status
            status = "healthy"
            warnings = []

            if cpu_percent > 80:
                status = "warning"
                warnings.append(f"High CPU usage: {cpu_percent}%")

            if memory_percent > 85:
                status = "warning"
                warnings.append(f"High memory usage: {memory_percent}%")

            if disk_percent > 85:
                status = "warning"
                warnings.append(f"Low disk space: {disk_percent}% used")

            return {
                "status": status,
                "cpu": {"usage_percent": cpu_percent, "core_count": psutil.cpu_count()},
                "memory": {
                    "usage_percent": memory_percent,
                    "available_gb": round(memory_available_gb, 2),
                    "total_gb": round(memory.total / (1024**3), 2),
                },
                "disk": {
                    "usage_percent": disk_percent,
                    "free_gb": round(disk_free_gb, 2),
                    "total_gb": round(disk.total / (1024**3), 2),
                },
                "warnings": warnings,
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to check system resources",
            }

    def _check_application_health(self, db: Session) -> Dict[str, Any]:
        """Check application-level health metrics"""
        try:
            # Count key entities
            total_users = db.query(func.count(User.id)).scalar() or 0
            total_couriers = db.query(func.count(Courier.id)).scalar() or 0
            total_vehicles = db.query(func.count(Vehicle.id)).scalar() or 0

            return {
                "status": "healthy",
                "metrics": {
                    "total_users": total_users,
                    "total_couriers": total_couriers,
                    "total_vehicles": total_vehicles,
                },
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            }

        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }

    def get_uptime(self) -> Dict[str, Any]:
        """Get application uptime"""
        uptime_delta = datetime.utcnow() - self.start_time

        return {
            "started_at": self.start_time.isoformat(),
            "current_time": datetime.utcnow().isoformat(),
            "uptime_seconds": uptime_delta.total_seconds(),
            "uptime_hours": uptime_delta.total_seconds() / 3600,
            "uptime_days": uptime_delta.days,
            "uptime_human": str(uptime_delta).split(".")[0],
        }

    def get_performance_metrics(self, db: Session) -> Dict[str, Any]:
        """Get application performance metrics"""
        try:
            # Database query performance (average response time for simple query)
            db_metrics = []
            for _ in range(5):
                start = datetime.utcnow()
                db.execute(text("SELECT COUNT(*) FROM users"))
                duration = (datetime.utcnow() - start).total_seconds() * 1000
                db_metrics.append(duration)

            avg_db_response = sum(db_metrics) / len(db_metrics)

            return {
                "database": {
                    "avg_query_time_ms": round(avg_db_response, 2),
                    "min_query_time_ms": round(min(db_metrics), 2),
                    "max_query_time_ms": round(max(db_metrics), 2),
                },
                "system": self._check_system_resources(),
            }

        except Exception as e:
            return {"error": str(e), "message": "Failed to get performance metrics"}


# Singleton instance
system_monitoring_service = SystemMonitoringService()
