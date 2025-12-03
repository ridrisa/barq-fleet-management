"""
Production-Ready CORS Configuration

This module provides comprehensive CORS (Cross-Origin Resource Sharing) configuration:
- Environment-based allowed origins
- Configurable methods and headers
- Credential handling
- Preflight caching
- Security-first defaults

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

from typing import List, Optional

from fastapi.middleware.cors import CORSMiddleware

from app.core.security_config import security_config


class CORSConfig:
    """
    CORS configuration manager

    Provides security-focused CORS settings based on environment
    """

    def __init__(self):
        self.config = security_config.cors

    @property
    def allow_origins(self) -> List[str]:
        """
        Get allowed origins

        Returns:
            List of allowed origin URLs
        """
        return self.config.allow_origins

    @property
    def allow_credentials(self) -> bool:
        """
        Allow credentials in CORS requests

        Returns:
            True if credentials allowed
        """
        return self.config.allow_credentials

    @property
    def allow_methods(self) -> List[str]:
        """
        Get allowed HTTP methods

        Returns:
            List of allowed HTTP methods
        """
        return self.config.allow_methods

    @property
    def allow_headers(self) -> List[str]:
        """
        Get allowed request headers

        Returns:
            List of allowed headers
        """
        return self.config.allow_headers

    @property
    def expose_headers(self) -> List[str]:
        """
        Get headers exposed to browser

        Returns:
            List of headers to expose
        """
        return self.config.expose_headers

    @property
    def max_age(self) -> int:
        """
        Get preflight cache duration

        Returns:
            Max age in seconds
        """
        return self.config.max_age

    def get_cors_middleware_kwargs(self) -> dict:
        """
        Get kwargs for FastAPI CORSMiddleware

        Returns:
            Dictionary of middleware configuration
        """
        return {
            "allow_origins": self.allow_origins,
            "allow_credentials": self.allow_credentials,
            "allow_methods": self.allow_methods,
            "allow_headers": self.allow_headers,
            "expose_headers": self.expose_headers,
            "max_age": self.max_age,
        }


def get_cors_middleware() -> CORSMiddleware:
    """
    Get configured CORS middleware instance

    Returns:
        Configured CORSMiddleware instance
    """
    cors_config = CORSConfig()

    # Get configuration
    config_kwargs = cors_config.get_cors_middleware_kwargs()

    # Return middleware class (to be added to app)
    return CORSMiddleware, config_kwargs


def validate_origin(origin: str) -> bool:
    """
    Validate if origin is allowed

    Args:
        origin: Origin URL to validate

    Returns:
        True if origin is allowed, False otherwise
    """
    allowed_origins = security_config.cors.allow_origins

    # Check for wildcard
    if "*" in allowed_origins:
        return True

    # Exact match
    if origin in allowed_origins:
        return True

    # Check with trailing slash
    if f"{origin}/" in allowed_origins or origin.rstrip("/") in allowed_origins:
        return True

    return False


# Pre-defined CORS configurations for common scenarios


class DevelopmentCORS:
    """CORS configuration for development environment"""

    allow_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    allow_credentials = True
    allow_methods = ["*"]
    allow_headers = ["*"]
    expose_headers = ["X-Request-ID", "X-RateLimit-Remaining"]
    max_age = 600


class ProductionCORS:
    """CORS configuration for production environment"""

    # Should be configured via environment variables
    allow_origins = []  # Must be explicitly set
    allow_credentials = True
    allow_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    allow_headers = [
        "Accept",
        "Accept-Language",
        "Content-Type",
        "Authorization",
        "X-CSRF-Token",
        "X-Request-ID",
    ]
    expose_headers = [
        "X-Request-ID",
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Reset",
    ]
    max_age = 3600  # 1 hour


class RestrictiveCORS:
    """Most restrictive CORS configuration"""

    allow_origins = []  # No origins by default
    allow_credentials = False
    allow_methods = ["GET", "POST"]
    allow_headers = ["Content-Type", "Authorization"]
    expose_headers = []
    max_age = 300  # 5 minutes


def get_cors_config_for_environment(environment: str = None) -> dict:
    """
    Get CORS configuration based on environment

    Args:
        environment: Environment name (development, staging, production)

    Returns:
        Dictionary of CORS configuration
    """
    if environment is None:
        environment = security_config.environment

    env = environment.lower()

    if env == "development":
        config_class = DevelopmentCORS
    elif env == "production":
        config_class = ProductionCORS
    else:
        # Staging or other environments use production settings
        config_class = ProductionCORS

    return {
        "allow_origins": config_class.allow_origins,
        "allow_credentials": config_class.allow_credentials,
        "allow_methods": config_class.allow_methods,
        "allow_headers": config_class.allow_headers,
        "expose_headers": config_class.expose_headers,
        "max_age": config_class.max_age,
    }
