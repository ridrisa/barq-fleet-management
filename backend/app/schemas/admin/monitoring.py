"""System Monitoring Schemas"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SystemHealthResponse(BaseModel):
    """Schema for system health status"""

    status: str = Field(..., description="Overall system status (healthy, degraded, unhealthy)")
    timestamp: datetime
    uptime_seconds: int
    version: str
    environment: str

    # Component health
    database: Dict[str, Any] = Field(..., description="Database health status")
    cache: Dict[str, Any] = Field(..., description="Cache health status")
    storage: Dict[str, Any] = Field(..., description="Storage health status")

    # System resources
    cpu_usage_percent: Optional[float]
    memory_usage_percent: Optional[float]
    disk_usage_percent: Optional[float]

    # Active connections
    active_database_connections: int
    total_database_connections: int
    active_users: int

    # Error rates
    error_rate_last_hour: float
    error_count_last_hour: int

    # Background jobs
    active_background_jobs: int
    failed_background_jobs_last_hour: int


class DatabaseStatsResponse(BaseModel):
    """Schema for database statistics"""

    # Connection info
    database_name: str
    database_version: str
    connection_pool_size: int
    active_connections: int
    idle_connections: int

    # Size info
    total_size_bytes: int
    total_size_mb: float
    total_size_gb: float

    # Table statistics
    total_tables: int
    total_indexes: int

    # Performance metrics
    slow_queries_last_hour: int
    average_query_time_ms: Optional[float]
    longest_query_time_ms: Optional[float]

    # Data statistics
    total_records: Optional[int]
    largest_table: Optional[str]
    largest_table_size_mb: Optional[float]


class APIMetricsResponse(BaseModel):
    """Schema for API metrics"""

    # Request statistics
    total_requests_last_hour: int
    total_requests_last_day: int
    requests_per_minute_avg: float

    # Response times
    average_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float

    # Status codes
    success_count: int  # 2xx
    client_error_count: int  # 4xx
    server_error_count: int  # 5xx

    # Popular endpoints
    top_endpoints: List[Dict[str, Any]] = Field(
        default_factory=list, description="Top 10 most called endpoints"
    )

    # Error details
    recent_errors: List[Dict[str, Any]] = Field(
        default_factory=list, description="Recent error details"
    )


class ResourceUsageResponse(BaseModel):
    """Schema for resource usage metrics"""

    # CPU
    cpu_count: int
    cpu_usage_percent: float
    cpu_usage_per_core: List[float]

    # Memory
    total_memory_mb: float
    available_memory_mb: float
    used_memory_mb: float
    memory_usage_percent: float

    # Disk
    total_disk_gb: float
    available_disk_gb: float
    used_disk_gb: float
    disk_usage_percent: float

    # Network
    bytes_sent_mb: Optional[float]
    bytes_received_mb: Optional[float]

    # Timestamp
    timestamp: datetime


class BackgroundJobStatsResponse(BaseModel):
    """Schema for background job statistics"""

    total_jobs: int
    active_jobs: int
    pending_jobs: int
    completed_jobs_last_hour: int
    failed_jobs_last_hour: int

    # Job types
    job_types: Dict[str, int] = Field(default_factory=dict, description="Count of jobs by type")

    # Recent failures
    recent_failures: List[Dict[str, Any]] = Field(
        default_factory=list, description="Recent failed jobs"
    )


class ErrorLogResponse(BaseModel):
    """Schema for error log entry"""

    id: int
    timestamp: datetime
    level: str
    message: str
    exception_type: Optional[str]
    exception_message: Optional[str]
    traceback: Optional[str]
    user_id: Optional[int]
    endpoint: Optional[str]
    request_method: Optional[str]
    request_path: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]


class ErrorLogListResponse(BaseModel):
    """Schema for paginated error log list"""

    items: List[ErrorLogResponse]
    total: int
    skip: int
    limit: int
