"""
Performance Monitoring API
Endpoints for performance metrics, health checks, and system monitoring
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import psutil
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.cache import cache_manager
from app.core.database import get_db
from app.core.performance_config import performance_config
from app.middleware.performance import performance_metrics
from app.utils.query_optimizer import n1_detector, query_analyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get("/metrics", summary="Get comprehensive performance metrics")
def get_performance_metrics():
    """
    Get real-time performance metrics

    Returns:
        - API performance metrics
        - Cache statistics
        - Database query statistics
        - System resource usage
        - Performance thresholds
    """
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "api": {
                "requests": performance_metrics.get_metrics(),
                "thresholds": {
                    "response_p95_ms": performance_config.thresholds.api_response_p95,
                    "response_p99_ms": performance_config.thresholds.api_response_p99,
                },
            },
            "cache": {
                "stats": cache_manager.get_stats(),
                "thresholds": {
                    "hit_rate_min": performance_config.thresholds.cache_hit_ratio_min,
                },
            },
            "database": {
                "queries": query_analyzer.get_stats(),
                "thresholds": {
                    "avg_query_ms": performance_config.thresholds.db_query_avg,
                    "p95_query_ms": performance_config.thresholds.db_query_p95,
                },
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_mb": memory.total / (1024 * 1024),
                    "available_mb": memory.available / (1024 * 1024),
                    "percent": memory.percent,
                },
                "disk": {
                    "total_gb": disk.total / (1024 * 1024 * 1024),
                    "free_gb": disk.free / (1024 * 1024 * 1024),
                    "percent": disk.percent,
                },
                "thresholds": {
                    "cpu_max_percent": performance_config.thresholds.cpu_usage_max * 100,
                    "memory_max_percent": performance_config.thresholds.memory_usage_max * 100,
                },
            },
            "status": _evaluate_health(),
        }
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}


@router.get("/health", summary="System health check")
def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive health check

    Checks:
    - Database connectivity
    - Redis connectivity
    - System resources
    - Performance thresholds
    """
    health_status = {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "checks": {}}

    # Database check
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful",
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}",
        }

    # Redis check
    try:
        cache_stats = cache_manager.get_stats()
        if cache_stats.get("redis_cache", {}).get("connected"):
            health_status["checks"]["redis"] = {
                "status": "healthy",
                "message": "Redis connection successful",
            }
        else:
            health_status["status"] = "degraded"
            health_status["checks"]["redis"] = {
                "status": "degraded",
                "message": "Redis not connected",
            }
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["checks"]["redis"] = {
            "status": "degraded",
            "message": f"Redis check failed: {str(e)}",
        }

    # System resources check
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent

        cpu_threshold = performance_config.thresholds.cpu_usage_max * 100
        memory_threshold = performance_config.thresholds.memory_usage_max * 100

        if cpu_percent > cpu_threshold or memory_percent > memory_threshold:
            health_status["status"] = "degraded"
            health_status["checks"]["resources"] = {
                "status": "degraded",
                "message": f"High resource usage (CPU: {cpu_percent}%, Memory: {memory_percent}%)",
            }
        else:
            health_status["checks"]["resources"] = {
                "status": "healthy",
                "message": f"Resources within limits (CPU: {cpu_percent}%, Memory: {memory_percent}%)",
            }
    except Exception as e:
        health_status["checks"]["resources"] = {
            "status": "unknown",
            "message": f"Resource check failed: {str(e)}",
        }

    return health_status


@router.get("/slow-queries", summary="Get slow queries report")
def get_slow_queries(limit: int = Query(10, ge=1, le=100)):
    """
    Get slowest database queries

    Args:
        limit: Maximum number of queries to return (1-100)

    Returns:
        List of slow queries with execution time
    """
    try:
        slow_queries = query_analyzer.get_slow_queries(limit=limit)

        return {
            "total_slow_queries": len(slow_queries),
            "threshold_ms": performance_config.monitoring.slow_query_threshold * 1000,
            "queries": [
                {
                    "statement": query["statement"],
                    "duration_ms": query["duration"] * 1000,
                    "timestamp": datetime.fromtimestamp(query["timestamp"]).isoformat(),
                }
                for query in slow_queries
            ],
        }
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        return {"error": str(e), "queries": []}


@router.get("/cache/stats", summary="Get detailed cache statistics")
def get_cache_stats():
    """
    Get detailed cache statistics

    Returns:
        - Cache hit/miss rates
        - Memory cache stats
        - Redis cache stats
    """
    try:
        return cache_manager.get_stats()
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}


@router.post("/cache/clear", summary="Clear cache (use with caution)")
def clear_cache(namespace: Optional[str] = Query(None, description="Cache namespace to clear")):
    """
    Clear cache (entire cache or specific namespace)

    Args:
        namespace: Optional namespace to clear (e.g., 'users', 'organizations')

    Warning:
        This will impact performance until cache is repopulated
    """
    try:
        if namespace:
            cache_manager.delete_pattern(namespace, "*")
            message = f"Cache cleared for namespace: {namespace}"
        else:
            cache_manager.redis_cache.client.flushdb()
            cache_manager.memory_cache.clear()
            message = "All cache cleared"

        logger.warning(f"Cache clear requested: {message}")

        return {"status": "success", "message": message, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {"status": "error", "message": str(e)}


@router.post("/query-analyzer/reset", summary="Reset query analyzer statistics")
def reset_query_analyzer():
    """
    Reset query analyzer statistics

    Useful for starting fresh performance measurements
    """
    try:
        query_analyzer.reset_stats()
        performance_metrics.reset()

        return {
            "status": "success",
            "message": "Query analyzer and performance metrics reset",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error resetting query analyzer: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/configuration", summary="Get performance configuration")
def get_performance_configuration():
    """
    Get current performance configuration settings

    Returns:
        All performance configuration values
    """
    return {
        "environment": performance_config.environment,
        "is_production": performance_config.is_production,
        "database": {
            "pool_size": performance_config.database.pool_size,
            "max_overflow": performance_config.database.max_overflow,
            "pool_timeout": performance_config.database.pool_timeout,
            "enable_read_replicas": performance_config.database.enable_read_replicas,
        },
        "cache": {
            "redis_url": (
                performance_config.cache.redis_url.split("@")[-1]
                if "@" in performance_config.cache.redis_url
                else "localhost"
            ),
            "default_ttl": performance_config.cache.default_ttl,
            "enable_memory_cache": performance_config.cache.enable_memory_cache,
            "memory_cache_size": performance_config.cache.memory_cache_size,
        },
        "api": {
            "enable_compression": performance_config.api.enable_compression,
            "enable_rate_limiting": performance_config.api.enable_rate_limiting,
            "enable_deduplication": performance_config.api.enable_deduplication,
        },
        "background_jobs": {
            "worker_concurrency": performance_config.background_jobs.worker_concurrency,
            "task_soft_time_limit": performance_config.background_jobs.task_soft_time_limit,
            "task_time_limit": performance_config.background_jobs.task_time_limit,
        },
        "monitoring": {
            "enable_profiling": performance_config.monitoring.enable_profiling,
            "slow_query_threshold": performance_config.monitoring.slow_query_threshold,
        },
        "thresholds": {
            "api_response_p95_ms": performance_config.thresholds.api_response_p95,
            "db_query_avg_ms": performance_config.thresholds.db_query_avg,
            "cache_hit_ratio_min": performance_config.thresholds.cache_hit_ratio_min,
            "cpu_usage_max": performance_config.thresholds.cpu_usage_max,
            "memory_usage_max": performance_config.thresholds.memory_usage_max,
        },
    }


@router.get("/n1-queries", summary="Get N+1 query detection patterns")
def get_n1_query_patterns():
    """
    Get detected N+1 query patterns

    Returns:
        Query patterns that may indicate N+1 problems
    """
    try:
        patterns = n1_detector.get_patterns()

        # Filter patterns that exceed threshold
        suspicious_patterns = {
            pattern: count for pattern, count in patterns.items() if count >= n1_detector.threshold
        }

        return {
            "threshold": n1_detector.threshold,
            "total_patterns": len(patterns),
            "suspicious_patterns": len(suspicious_patterns),
            "patterns": [
                {
                    "pattern": pattern[:200],  # Truncate long patterns
                    "count": count,
                    "severity": "high" if count >= n1_detector.threshold * 2 else "medium",
                }
                for pattern, count in sorted(
                    suspicious_patterns.items(), key=lambda x: x[1], reverse=True
                )
            ],
        }
    except Exception as e:
        logger.error(f"Error getting N+1 patterns: {e}")
        return {"error": str(e), "patterns": []}


def _evaluate_health() -> str:
    """
    Evaluate overall system health based on metrics

    Returns:
        Health status: "healthy", "degraded", or "unhealthy"
    """
    try:
        # Check cache hit rate
        cache_stats = cache_manager.get_stats()
        hit_rate = cache_stats.get("hit_rate", 0)

        if hit_rate < performance_config.thresholds.cache_hit_ratio_min:
            return "degraded"

        # Check CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent

        if cpu_percent > performance_config.thresholds.cpu_usage_max * 100:
            return "degraded"

        if memory_percent > performance_config.thresholds.memory_usage_max * 100:
            return "degraded"

        # Check error rate
        api_metrics = performance_metrics.get_metrics()
        error_rate = api_metrics.get("error_rate", 0)

        if error_rate > performance_config.thresholds.max_error_rate:
            return "degraded"

        return "healthy"

    except Exception as e:
        logger.error(f"Error evaluating health: {e}")
        return "unknown"


__all__ = ["router"]
