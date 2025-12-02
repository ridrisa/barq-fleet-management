"""
BARQ Fleet Management - Production Configuration

Production environment settings with strict security and optimized performance.
"""
from pydantic import Field

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """
    Production environment configuration.

    All settings are optimized for security and performance.
    Sensitive values MUST be provided via environment variables.
    """

    # Environment
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Logging - structured for log aggregation
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Database - optimized connection pool
    DB_POOL_SIZE: int = Field(default=20)
    DB_MAX_OVERFLOW: int = Field(default=40)
    DB_POOL_TIMEOUT: int = Field(default=30)
    DB_POOL_RECYCLE: int = Field(default=3600)
    DB_ECHO: bool = False

    # Security - strict settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_EXPIRE_MINUTES: int = Field(default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # Rate limiting - strict
    RATE_LIMIT_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW: int = Field(default=60)

    # Redis - production pool
    REDIS_MAX_CONNECTIONS: int = Field(default=50)

    # Cache - aggressive caching
    CACHE_DEFAULT_TTL: int = Field(default=300)
    CACHE_USER_TTL: int = Field(default=600)
    CACHE_ORG_TTL: int = Field(default=1800)
