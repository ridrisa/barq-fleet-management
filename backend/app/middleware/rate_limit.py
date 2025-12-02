"""
Rate Limiting Middleware

This module provides comprehensive rate limiting including:
- Per-user rate limits
- Per-IP rate limits
- Per-endpoint rate limits
- Configurable limits for different routes
- Redis-based distributed rate limiting
- Rate limit headers in responses

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import time
from typing import Callable, Optional, Dict, Tuple
from functools import wraps

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.security_config import security_config


# In-memory storage for development (use Redis in production)
class InMemoryStorage:
    """Simple in-memory rate limit storage (for development only)"""

    def __init__(self):
        self._storage: Dict[str, Tuple[int, float]] = {}

    def get(self, key: str) -> Optional[int]:
        """Get current count for key"""
        if key in self._storage:
            count, timestamp = self._storage[key]
            return count
        return None

    def set(self, key: str, count: int, expire: int):
        """Set count with expiration"""
        self._storage[key] = (count, time.time() + expire)

    def incr(self, key: str) -> int:
        """Increment counter"""
        if key in self._storage:
            count, timestamp = self._storage[key]
            if time.time() > timestamp:
                # Expired, reset
                self._storage[key] = (1, timestamp)
                return 1
            else:
                self._storage[key] = (count + 1, timestamp)
                return count + 1
        else:
            self._storage[key] = (1, time.time() + 60)  # Default 60s window
            return 1

    def cleanup(self):
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._storage.items()
            if current_time > timestamp
        ]
        for key in expired_keys:
            del self._storage[key]


# Global storage instance
_storage = InMemoryStorage()


def get_identifier(request: Request) -> str:
    """
    Get unique identifier for rate limiting

    Priority:
    1. User ID (if authenticated)
    2. API Key (if present)
    3. IP Address

    Args:
        request: FastAPI request object

    Returns:
        Unique identifier string
    """
    # Check for authenticated user
    if hasattr(request.state, 'user') and request.state.user:
        return f"user:{request.state.user.id}"

    # Check for API key
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"apikey:{api_key[:16]}"

    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"


# Initialize limiter
limiter = Limiter(
    key_func=get_identifier,
    default_limits=[security_config.rate_limit.default_limit] if security_config.rate_limit.enabled else [],
    storage_uri=security_config.rate_limit.storage_uri,
    strategy="fixed-window",
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware

    Features:
    - Automatic rate limiting based on identifier
    - Different limits for different endpoints
    - Rate limit headers in responses
    - Configurable exemptions
    """

    # Endpoints with custom rate limits
    CUSTOM_LIMITS = {
        "/api/v1/auth/login": "5/minute",
        "/api/v1/auth/register": "3/minute",
        "/api/v1/auth/forgot-password": "3/hour",
        "/api/v1/auth/verify-email": "5/hour",
        "/api/v1/users/me": "100/minute",
        "/api/v1/export": "10/hour",
    }

    # Exempt endpoints (no rate limiting)
    EXEMPT_ENDPOINTS = {
        "/health",
        "/",
        "/api/v1/docs",
        "/api/v1/openapi.json",
    }

    def __init__(self, app):
        super().__init__(app)
        self.enabled = security_config.rate_limit.enabled

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with rate limiting"""

        if not self.enabled:
            return await call_next(request)

        # Check if endpoint is exempt
        if request.url.path in self.EXEMPT_ENDPOINTS:
            return await call_next(request)

        # Get identifier
        identifier = get_identifier(request)

        # Get rate limit for this endpoint
        limit_string = self._get_limit_for_path(request.url.path)
        limit, window = self._parse_limit_string(limit_string)

        # Check rate limit
        key = f"ratelimit:{identifier}:{request.url.path}"
        current_count = _storage.incr(key)

        if current_count == 1:
            # First request, set expiration
            _storage.set(key, 1, window)

        # Check if limit exceeded
        if current_count > limit:
            retry_after = window  # Simplified, could calculate exact time

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                }
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, limit - current_count)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)

        return response

    def _get_limit_for_path(self, path: str) -> str:
        """Get rate limit for specific path"""
        # Check exact match
        if path in self.CUSTOM_LIMITS:
            return self.CUSTOM_LIMITS[path]

        # Check prefix match for dynamic routes
        for pattern, limit in self.CUSTOM_LIMITS.items():
            if pattern.endswith('*') and path.startswith(pattern[:-1]):
                return limit

        # Return default limit
        return security_config.rate_limit.default_limit

    def _parse_limit_string(self, limit_string: str) -> Tuple[int, int]:
        """
        Parse limit string (e.g., "100/minute") to (limit, window_seconds)

        Args:
            limit_string: Limit string

        Returns:
            Tuple of (limit, window in seconds)
        """
        try:
            count, period = limit_string.split('/')
            count = int(count)

            period_map = {
                'second': 1,
                'minute': 60,
                'hour': 3600,
                'day': 86400,
            }

            window = period_map.get(period, 60)
            return count, window

        except:
            # Default to 100/minute
            return 100, 60


class EndpointRateLimiter:
    """
    Decorator for endpoint-specific rate limiting

    Usage:
        @app.get("/api/resource")
        @rate_limit("10/minute")
        async def get_resource():
            ...
    """

    def __init__(self, limit: str):
        """
        Initialize rate limiter

        Args:
            limit: Rate limit string (e.g., "10/minute", "100/hour")
        """
        self.limit = limit

    def __call__(self, func: Callable) -> Callable:
        """Decorator wrapper"""

        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            if not security_config.rate_limit.enabled:
                return await func(*args, request=request, **kwargs)

            if request is None:
                # Try to find request in kwargs
                request = kwargs.get('request')

            if request is None:
                # Cannot rate limit without request
                return await func(*args, **kwargs)

            # Get identifier
            identifier = get_identifier(request)

            # Parse limit
            limit_value, window = self._parse_limit(self.limit)

            # Check rate limit
            key = f"endpoint:{identifier}:{func.__name__}"
            current_count = _storage.incr(key)

            if current_count == 1:
                _storage.set(key, 1, window)

            if current_count > limit_value:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Maximum {self.limit}",
                    headers={"Retry-After": str(window)}
                )

            return await func(*args, request=request, **kwargs)

        return wrapper

    def _parse_limit(self, limit_string: str) -> Tuple[int, int]:
        """Parse limit string to (count, seconds)"""
        try:
            count, period = limit_string.split('/')
            count = int(count)

            period_map = {
                'second': 1,
                'minute': 60,
                'hour': 3600,
                'day': 86400,
            }

            return count, period_map.get(period, 60)
        except:
            return 100, 60


def rate_limit(limit: str):
    """
    Rate limit decorator

    Args:
        limit: Rate limit string (e.g., "10/minute")

    Example:
        @router.post("/login")
        @rate_limit("5/minute")
        async def login(request: Request):
            ...
    """
    return EndpointRateLimiter(limit)


class BurstRateLimiter:
    """
    Burst rate limiter with token bucket algorithm

    Allows bursts but maintains average rate over time
    """

    def __init__(self, rate: int, burst: int, window: int = 60):
        """
        Initialize burst rate limiter

        Args:
            rate: Average requests per window
            burst: Maximum burst size
            window: Time window in seconds
        """
        self.rate = rate
        self.burst = burst
        self.window = window

    async def check(self, identifier: str) -> bool:
        """
        Check if request is allowed

        Args:
            identifier: Unique identifier

        Returns:
            True if allowed, False if rate limited
        """
        key = f"burst:{identifier}"

        # Get current tokens
        current_tokens = _storage.get(key)

        if current_tokens is None:
            # First request, initialize with burst capacity
            _storage.set(key, self.burst - 1, self.window)
            return True

        if current_tokens > 0:
            # Tokens available
            _storage.set(key, current_tokens - 1, self.window)
            return True

        # No tokens available
        return False


# Cleanup task (should be run periodically)
def cleanup_rate_limit_storage():
    """Cleanup expired rate limit entries"""
    _storage.cleanup()


# Export rate limit exception handler
def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "error_code": "RATE_LIMIT_EXCEEDED"
        },
        headers={
            "Retry-After": "60"  # Default retry after 60 seconds
        }
    )
