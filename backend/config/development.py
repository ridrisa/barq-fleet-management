"""
BARQ Fleet Management - Development Configuration

Development-specific settings with verbose logging and relaxed security.
"""
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Logging - verbose for debugging
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "text"  # Human-readable in development

    # Database - allow local connections
    DB_ECHO: bool = True  # Log SQL queries

    # Security - relaxed for development
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Rate limiting - more permissive
    RATE_LIMIT_REQUESTS: int = 1000
    RATE_LIMIT_WINDOW: int = 60

    # CORS - allow local development servers
    BACKEND_CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://localhost:8080,"
        "http://127.0.0.1:3000,"
        "http://127.0.0.1:5173"
    )
