"""
Performance Configuration Module
Centralized performance tuning settings for BARQ Fleet Management
"""
import os
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class DatabaseConfig:
    """Database performance configuration"""
    # Connection pool settings
    pool_size: int = int(os.getenv("DB_POOL_SIZE", "20"))
    max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    pool_recycle: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    pool_pre_ping: bool = True

    # Query optimization
    echo_queries: bool = os.getenv("DB_ECHO", "false").lower() == "true"
    query_timeout: int = int(os.getenv("DB_QUERY_TIMEOUT", "30000"))  # milliseconds

    # Read replica support
    enable_read_replicas: bool = os.getenv("DB_READ_REPLICAS_ENABLED", "false").lower() == "true"
    read_replica_urls: list[str] = field(default_factory=lambda: os.getenv("DB_READ_REPLICA_URLS", "").split(",") if os.getenv("DB_READ_REPLICA_URLS") else [])

    # Lazy loading configuration
    lazy_loading: bool = True
    expire_on_commit: bool = False


@dataclass
class CacheConfig:
    """Caching layer configuration"""
    # Redis connection
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_max_connections: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    redis_socket_timeout: int = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
    redis_socket_connect_timeout: int = int(os.getenv("REDIS_CONNECT_TIMEOUT", "5"))

    # Cache TTL (Time To Live) settings
    default_ttl: int = int(os.getenv("CACHE_DEFAULT_TTL", "300"))  # 5 minutes
    user_ttl: int = int(os.getenv("CACHE_USER_TTL", "600"))  # 10 minutes
    organization_ttl: int = int(os.getenv("CACHE_ORG_TTL", "1800"))  # 30 minutes
    static_data_ttl: int = int(os.getenv("CACHE_STATIC_TTL", "3600"))  # 1 hour

    # Multi-level caching
    enable_memory_cache: bool = True
    memory_cache_size: int = int(os.getenv("MEMORY_CACHE_SIZE", "1000"))
    memory_cache_ttl: int = int(os.getenv("MEMORY_CACHE_TTL", "60"))  # 1 minute

    # Cache warming
    enable_cache_warming: bool = os.getenv("CACHE_WARMING_ENABLED", "false").lower() == "true"

    # Cache invalidation
    enable_cache_tags: bool = True


@dataclass
class APIConfig:
    """API performance configuration"""
    # Compression
    enable_compression: bool = True
    compression_level: int = 6
    min_compression_size: int = 1024  # bytes

    # Response caching
    enable_response_cache: bool = True
    response_cache_ttl: int = int(os.getenv("API_CACHE_TTL", "60"))

    # Rate limiting
    enable_rate_limiting: bool = True
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

    # Request deduplication
    enable_deduplication: bool = True
    deduplication_window: int = 5  # seconds

    # Connection management
    keep_alive_timeout: int = 65
    max_concurrent_requests: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "1000"))


@dataclass
class BackgroundJobsConfig:
    """Background jobs configuration (Celery)"""
    broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # Task settings
    task_soft_time_limit: int = int(os.getenv("CELERY_SOFT_TIME_LIMIT", "300"))  # 5 minutes
    task_time_limit: int = int(os.getenv("CELERY_TIME_LIMIT", "600"))  # 10 minutes
    task_max_retries: int = int(os.getenv("CELERY_MAX_RETRIES", "3"))
    task_default_retry_delay: int = int(os.getenv("CELERY_RETRY_DELAY", "60"))  # seconds

    # Worker settings
    worker_concurrency: int = int(os.getenv("CELERY_WORKER_CONCURRENCY", "4"))
    worker_prefetch_multiplier: int = int(os.getenv("CELERY_PREFETCH_MULTIPLIER", "4"))

    # Result expiration
    result_expires: int = int(os.getenv("CELERY_RESULT_EXPIRES", "3600"))  # 1 hour

    # Task routing
    enable_task_routing: bool = True
    high_priority_queue: str = "high_priority"
    default_queue: str = "default"
    low_priority_queue: str = "low_priority"


@dataclass
class FileHandlingConfig:
    """File handling performance configuration"""
    # Upload settings
    chunk_size: int = int(os.getenv("FILE_CHUNK_SIZE", "8192"))  # 8KB
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB

    # Streaming
    enable_streaming: bool = True
    stream_buffer_size: int = int(os.getenv("STREAM_BUFFER_SIZE", "65536"))  # 64KB

    # Compression
    enable_compression: bool = True
    compression_formats: list[str] = field(default_factory=lambda: ["gzip", "zip"])

    # CDN integration
    enable_cdn: bool = os.getenv("CDN_ENABLED", "false").lower() == "true"
    cdn_url: Optional[str] = os.getenv("CDN_URL")
    cdn_access_key: Optional[str] = os.getenv("CDN_ACCESS_KEY")
    cdn_secret_key: Optional[str] = os.getenv("CDN_SECRET_KEY")


@dataclass
class MonitoringConfig:
    """Monitoring and profiling configuration"""
    # Request profiling
    enable_profiling: bool = os.getenv("PROFILING_ENABLED", "false").lower() == "true"
    profile_slow_queries: bool = True
    slow_query_threshold: float = float(os.getenv("SLOW_QUERY_THRESHOLD", "0.1"))  # 100ms

    # Database query logging
    log_queries: bool = os.getenv("LOG_QUERIES", "false").lower() == "true"
    log_slow_queries_only: bool = True

    # Memory profiling
    enable_memory_profiling: bool = os.getenv("MEMORY_PROFILING_ENABLED", "false").lower() == "true"
    memory_profiling_interval: int = 300  # seconds

    # Performance metrics
    enable_metrics: bool = True
    metrics_port: int = int(os.getenv("METRICS_PORT", "9090"))

    # Health checks
    health_check_interval: int = 30  # seconds


@dataclass
class MemoryConfig:
    """Memory optimization configuration"""
    # Object pooling
    enable_object_pooling: bool = True
    pool_max_size: int = int(os.getenv("OBJECT_POOL_SIZE", "100"))

    # Garbage collection
    gc_threshold_0: int = 700
    gc_threshold_1: int = 10
    gc_threshold_2: int = 10

    # Memory limits
    max_memory_per_worker: int = int(os.getenv("MAX_MEMORY_MB", "512"))  # MB
    enable_memory_limits: bool = True

    # Large object handling
    large_object_threshold: int = int(os.getenv("LARGE_OBJECT_THRESHOLD", "1048576"))  # 1MB


@dataclass
class PerformanceThresholds:
    """Performance monitoring thresholds and alerts"""
    # API response times (milliseconds)
    api_response_p50: float = 50.0
    api_response_p95: float = 100.0
    api_response_p99: float = 200.0

    # Database query times (milliseconds)
    db_query_avg: float = 50.0
    db_query_p95: float = 100.0
    db_query_p99: float = 200.0

    # Cache performance
    cache_hit_ratio_min: float = 0.90  # 90%

    # System resources
    cpu_usage_max: float = 0.70  # 70%
    memory_usage_max: float = 0.80  # 80%

    # Throughput
    min_throughput_rps: int = 1000  # requests per second

    # Error rates
    max_error_rate: float = 0.01  # 1%


class PerformanceConfig:
    """Main performance configuration class"""

    def __init__(self):
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.api = APIConfig()
        self.background_jobs = BackgroundJobsConfig()
        self.file_handling = FileHandlingConfig()
        self.monitoring = MonitoringConfig()
        self.memory = MemoryConfig()
        self.thresholds = PerformanceThresholds()

        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment.lower() == "production"
        self.is_development = self.environment.lower() == "development"

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a performance feature is enabled"""
        feature_flags = {
            "compression": self.api.enable_compression,
            "caching": self.cache.enable_memory_cache,
            "profiling": self.monitoring.enable_profiling,
            "rate_limiting": self.api.enable_rate_limiting,
            "background_jobs": True,
            "read_replicas": self.database.enable_read_replicas,
        }
        return feature_flags.get(feature, False)

    def get_cache_ttl(self, cache_type: str) -> int:
        """Get cache TTL for specific cache type"""
        ttl_map = {
            "user": self.cache.user_ttl,
            "organization": self.cache.organization_ttl,
            "static": self.cache.static_data_ttl,
            "default": self.cache.default_ttl,
        }
        return ttl_map.get(cache_type, self.cache.default_ttl)

    def validate_config(self) -> list[str]:
        """Validate performance configuration and return warnings"""
        warnings = []

        if self.is_production:
            if self.database.pool_size < 10:
                warnings.append("Database pool size is low for production")

            if not self.cache.enable_memory_cache:
                warnings.append("Memory cache is disabled in production")

            if self.monitoring.enable_profiling:
                warnings.append("Profiling should be disabled in production")

            if self.database.echo_queries:
                warnings.append("Query echoing should be disabled in production")

        if self.database.pool_size > self.database.max_overflow:
            warnings.append("max_overflow should be greater than pool_size")

        return warnings


# Global performance configuration instance
performance_config = PerformanceConfig()


# Validate configuration on startup
_warnings = performance_config.validate_config()
if _warnings:
    import logging
    logger = logging.getLogger(__name__)
    for warning in _warnings:
        logger.warning(f"Performance config warning: {warning}")
