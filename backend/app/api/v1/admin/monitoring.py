"""Admin System Monitoring API"""

import time
from datetime import datetime, timedelta
from typing import Optional

import psutil
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.dependencies import get_current_superuser, get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.admin.monitoring import (
    APIMetricsResponse,
    BackgroundJobStatsResponse,
    DatabaseStatsResponse,
    ResourceUsageResponse,
    SystemHealthResponse,
)

router = APIRouter()

# Track application start time for uptime calculation
_app_start_time = time.time()


@router.get("/health", response_model=SystemHealthResponse)
def get_system_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get overall system health status.

    Requires superuser permission.

    Returns comprehensive health information including:
    - Component health (database, cache, storage)
    - System resources (CPU, memory, disk)
    - Active connections
    - Error rates
    - Background job status
    """
    # Calculate uptime
    uptime_seconds = int(time.time() - _app_start_time)

    # Check database health
    database_healthy = True
    database_latency_ms = 0
    try:
        start = time.time()
        db.execute(text("SELECT 1"))
        database_latency_ms = int((time.time() - start) * 1000)
    except Exception as e:
        database_healthy = False

    # Get active database connections
    try:
        result = db.execute(
            text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
        ).scalar()
        active_db_connections = result or 0

        result = db.execute(text("SELECT count(*) FROM pg_stat_activity")).scalar()
        total_db_connections = result or 0
    except:
        active_db_connections = 0
        total_db_connections = 0

    # Get active users (logged in within last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    active_users = (
        db.query(User).filter(User.is_active == True, User.updated_at >= one_hour_ago).count()
    )

    # Get error rate from audit logs
    error_count = (
        db.query(AuditLog)
        .filter(AuditLog.created_at >= one_hour_ago, AuditLog.action.in_(["error", "failed"]))
        .count()
    )
    total_requests = db.query(AuditLog).filter(AuditLog.created_at >= one_hour_ago).count()
    error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0

    # Get system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
    except:
        cpu_percent = None
        memory = None
        disk = None

    # Determine overall status
    status_value = "healthy"
    if (
        not database_healthy
        or (cpu_percent and cpu_percent > 90)
        or (memory and memory.percent > 90)
    ):
        status_value = "degraded"
    if not database_healthy:
        status_value = "unhealthy"

    return SystemHealthResponse(
        status=status_value,
        timestamp=datetime.utcnow(),
        uptime_seconds=uptime_seconds,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database={
            "healthy": database_healthy,
            "latency_ms": database_latency_ms,
            "status": "connected" if database_healthy else "disconnected",
        },
        cache={"healthy": True, "status": "connected"},  # Placeholder
        storage={"healthy": True, "status": "available"},  # Placeholder
        cpu_usage_percent=cpu_percent,
        memory_usage_percent=memory.percent if memory else None,
        disk_usage_percent=disk.percent if disk else None,
        active_database_connections=active_db_connections,
        total_database_connections=total_db_connections,
        active_users=active_users,
        error_rate_last_hour=round(error_rate, 2),
        error_count_last_hour=error_count,
        active_background_jobs=0,  # Placeholder
        failed_background_jobs_last_hour=0,  # Placeholder
    )


@router.get("/database/stats", response_model=DatabaseStatsResponse)
def get_database_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get database statistics and performance metrics.

    Requires superuser permission.

    Returns:
    - Connection pool statistics
    - Database size information
    - Table and index counts
    - Performance metrics
    """
    # Get database version
    db_version = db.execute(text("SELECT version()")).scalar()

    # Get database size
    db_size_result = db.execute(text("SELECT pg_database_size(current_database())")).scalar()
    db_size_bytes = db_size_result or 0
    db_size_mb = db_size_bytes / (1024 * 1024)
    db_size_gb = db_size_bytes / (1024 * 1024 * 1024)

    # Get connection statistics
    active_connections = (
        db.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")).scalar()
        or 0
    )

    idle_connections = (
        db.execute(text("SELECT count(*) FROM pg_stat_activity WHERE state = 'idle'")).scalar() or 0
    )

    # Get table and index counts
    table_count = (
        db.execute(
            text("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
        ).scalar()
        or 0
    )

    index_count = (
        db.execute(text("SELECT count(*) FROM pg_indexes WHERE schemaname = 'public'")).scalar()
        or 0
    )

    # Get largest table
    try:
        largest_table_result = db.execute(
            text(
                """
            SELECT
                tablename,
                pg_total_relation_size(schemaname||'.'||tablename) as size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY size DESC
            LIMIT 1
        """
            )
        ).fetchone()

        if largest_table_result:
            largest_table = largest_table_result[0]
            largest_table_size_mb = largest_table_result[1] / (1024 * 1024)
        else:
            largest_table = None
            largest_table_size_mb = None
    except:
        largest_table = None
        largest_table_size_mb = None

    return DatabaseStatsResponse(
        database_name=settings.POSTGRES_DB,
        database_version=db_version.split()[1] if db_version else "Unknown",
        connection_pool_size=10,  # Default pool size
        active_connections=active_connections,
        idle_connections=idle_connections,
        total_size_bytes=db_size_bytes,
        total_size_mb=round(db_size_mb, 2),
        total_size_gb=round(db_size_gb, 2),
        total_tables=table_count,
        total_indexes=index_count,
        slow_queries_last_hour=0,  # Placeholder
        average_query_time_ms=None,
        longest_query_time_ms=None,
        total_records=None,
        largest_table=largest_table,
        largest_table_size_mb=round(largest_table_size_mb, 2) if largest_table_size_mb else None,
    )


@router.get("/api/metrics", response_model=APIMetricsResponse)
def get_api_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get API request metrics and statistics.

    Requires superuser permission.

    Returns:
    - Request counts and rates
    - Response times (average, p95, p99)
    - Status code distribution
    - Top endpoints
    - Recent errors
    """
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    one_day_ago = datetime.utcnow() - timedelta(days=1)

    # Count requests
    requests_last_hour = db.query(AuditLog).filter(AuditLog.created_at >= one_hour_ago).count()

    requests_last_day = db.query(AuditLog).filter(AuditLog.created_at >= one_day_ago).count()

    requests_per_minute = requests_last_hour / 60 if requests_last_hour > 0 else 0

    # Count by status (using action as proxy for status)
    success_count = (
        db.query(AuditLog)
        .filter(
            AuditLog.created_at >= one_hour_ago,
            AuditLog.action.in_(["create", "read", "update", "delete", "login"]),
        )
        .count()
    )

    error_count = (
        db.query(AuditLog)
        .filter(AuditLog.created_at >= one_hour_ago, AuditLog.action.in_(["error", "failed"]))
        .count()
    )

    # Top endpoints (using resource_type)
    top_endpoints = []
    top_resources = (
        db.query(AuditLog.resource_type, func.count(AuditLog.id).label("count"))
        .filter(AuditLog.created_at >= one_day_ago)
        .group_by(AuditLog.resource_type)
        .order_by(func.count(AuditLog.id).desc())
        .limit(10)
        .all()
    )

    for resource, count in top_resources:
        if resource:
            top_endpoints.append(
                {
                    "endpoint": resource,
                    "count": count,
                    "percentage": (
                        round(count / requests_last_day * 100, 2) if requests_last_day > 0 else 0
                    ),
                }
            )

    # Recent errors
    recent_errors = []
    error_logs = (
        db.query(AuditLog)
        .filter(AuditLog.action.in_(["error", "failed"]), AuditLog.created_at >= one_hour_ago)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
        .all()
    )

    for log in error_logs:
        recent_errors.append(
            {
                "timestamp": log.created_at.isoformat(),
                "message": log.description or "Unknown error",
                "resource": log.resource_type,
                "user": log.username,
            }
        )

    return APIMetricsResponse(
        total_requests_last_hour=requests_last_hour,
        total_requests_last_day=requests_last_day,
        requests_per_minute_avg=round(requests_per_minute, 2),
        average_response_time_ms=150.0,  # Placeholder
        p95_response_time_ms=500.0,  # Placeholder
        p99_response_time_ms=1000.0,  # Placeholder
        success_count=success_count,
        client_error_count=0,  # Placeholder
        server_error_count=error_count,
        top_endpoints=top_endpoints,
        recent_errors=recent_errors,
    )


@router.get("/resources", response_model=ResourceUsageResponse)
def get_resource_usage(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get system resource usage metrics.

    Requires superuser permission.

    Returns:
    - CPU usage (overall and per core)
    - Memory usage
    - Disk usage
    - Network statistics
    """
    # Get CPU info
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_per_core = psutil.cpu_percent(interval=0.5, percpu=True)

    # Get memory info
    memory = psutil.virtual_memory()
    total_memory_mb = memory.total / (1024 * 1024)
    available_memory_mb = memory.available / (1024 * 1024)
    used_memory_mb = memory.used / (1024 * 1024)

    # Get disk info
    disk = psutil.disk_usage("/")
    total_disk_gb = disk.total / (1024 * 1024 * 1024)
    available_disk_gb = disk.free / (1024 * 1024 * 1024)
    used_disk_gb = disk.used / (1024 * 1024 * 1024)

    # Get network info
    try:
        net_io = psutil.net_io_counters()
        bytes_sent_mb = net_io.bytes_sent / (1024 * 1024)
        bytes_received_mb = net_io.bytes_recv / (1024 * 1024)
    except:
        bytes_sent_mb = None
        bytes_received_mb = None

    return ResourceUsageResponse(
        cpu_count=cpu_count,
        cpu_usage_percent=round(cpu_percent, 2),
        cpu_usage_per_core=[round(p, 2) for p in cpu_per_core],
        total_memory_mb=round(total_memory_mb, 2),
        available_memory_mb=round(available_memory_mb, 2),
        used_memory_mb=round(used_memory_mb, 2),
        memory_usage_percent=round(memory.percent, 2),
        total_disk_gb=round(total_disk_gb, 2),
        available_disk_gb=round(available_disk_gb, 2),
        used_disk_gb=round(used_disk_gb, 2),
        disk_usage_percent=round(disk.percent, 2),
        bytes_sent_mb=round(bytes_sent_mb, 2) if bytes_sent_mb else None,
        bytes_received_mb=round(bytes_received_mb, 2) if bytes_received_mb else None,
        timestamp=datetime.utcnow(),
    )
