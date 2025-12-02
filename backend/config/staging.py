"""
BARQ Fleet Management - Staging Configuration

Staging environment settings - production-like but with enhanced logging.
"""
from .base import BaseConfig


class StagingConfig(BaseConfig):
    """Staging environment configuration."""

    # Environment
    ENVIRONMENT: str = "staging"
    DEBUG: bool = False

    # Logging - detailed but structured
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "json"

    # Database - production-like pool
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_ECHO: bool = False

    # Security - tighter than development
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Rate limiting - production-like
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
