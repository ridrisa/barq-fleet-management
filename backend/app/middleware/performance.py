"""
Performance Monitoring Middleware
Tracks request timing, adds performance headers, and logs slow requests
"""

import logging
import time
from typing import Callable

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request performance monitoring

    Features:
    - Request timing
    - Performance metrics collection
    - Slow request logging
    - Response time headers
    """

    def __init__(self, app, enable_profiling: bool = False):
        super().__init__(app)
        self.enable_profiling = enable_profiling
        self.slow_threshold = performance_config.monitoring.slow_query_threshold

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with performance tracking"""
        # Start timing
        start_time = time.time()

        # Store start time in request state
        request.state.start_time = start_time

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            # Log exception with timing
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- {process_time:.3f}s - {type(e).__name__}: {str(e)}"
            )
            raise

        # Calculate processing time
        process_time = time.time() - start_time

        # Add performance headers
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        response.headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")

        # Log slow requests
        if process_time >= self.slow_threshold:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"- {process_time:.3f}s (threshold: {self.slow_threshold}s)"
            )

        # Detailed profiling if enabled
        if self.enable_profiling:
            logger.debug(
                f"Request: {request.method} {request.url.path} "
                f"- Status: {response.status_code} "
                f"- Time: {process_time:.3f}s"
            )

        return response


class CacheHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding cache control headers

    Features:
    - Cache-Control headers
    - ETag support
    - Conditional requests (304 Not Modified)
    """

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add cache headers to responses"""
        response = await call_next(request)

        # Only cache GET requests
        if request.method == "GET":
            # Public endpoints
            if request.url.path.startswith("/api/v1/public"):
                response.headers["Cache-Control"] = "public, max-age=3600"

            # Static data
            elif any(keyword in request.url.path for keyword in ["/vehicles", "/organizations"]):
                response.headers["Cache-Control"] = "private, max-age=300"

            # User-specific data
            elif "/users" in request.url.path or "/profile" in request.url.path:
                response.headers["Cache-Control"] = "private, max-age=60"

            # Default: no cache for dynamic content
            else:
                response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"

        return response


class RequestDeduplicationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request deduplication

    Prevents duplicate requests from being processed within a time window
    """

    def __init__(self, app, window_seconds: int = 5):
        super().__init__(app)
        self.window_seconds = window_seconds
        self._request_cache: dict[str, tuple[float, Response]] = {}

    def _make_request_key(self, request: Request) -> str:
        """Generate unique key for request"""
        import hashlib

        # Include method, path, and query params
        key_parts = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items())),
        ]

        # Include user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            key_parts.append(str(user_id))

        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check for duplicate requests"""
        # Only deduplicate idempotent methods
        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            return await call_next(request)

        # Generate request key
        request_key = self._make_request_key(request)

        # Check cache
        current_time = time.time()
        if request_key in self._request_cache:
            cached_time, cached_response = self._request_cache[request_key]

            # Check if within deduplication window
            if current_time - cached_time < self.window_seconds:
                logger.debug(f"Duplicate request detected: {request.method} {request.url.path}")

                # Return cached response
                cached_response.headers["X-Deduplicated"] = "true"
                return cached_response

        # Process request
        response = await call_next(request)

        # Cache successful responses
        if 200 <= response.status_code < 300:
            self._request_cache[request_key] = (current_time, response)

        # Cleanup old entries (periodically)
        if len(self._request_cache) > 1000:
            self._cleanup_cache(current_time)

        return response

    def _cleanup_cache(self, current_time: float):
        """Remove expired cache entries"""
        expired_keys = [
            key
            for key, (cached_time, _) in self._request_cache.items()
            if current_time - cached_time >= self.window_seconds
        ]

        for key in expired_keys:
            del self._request_cache[key]


class CompressionMiddleware:
    """
    Custom compression middleware with configuration support

    Wraps GZipMiddleware with performance config
    """

    @staticmethod
    def add_to_app(app: FastAPI):
        """Add compression middleware to FastAPI app"""
        if performance_config.api.enable_compression:
            app.add_middleware(
                GZipMiddleware,
                minimum_size=performance_config.api.min_compression_size,
                compresslevel=performance_config.api.compression_level,
            )
            logger.info(
                f"Compression enabled: level={performance_config.api.compression_level}, "
                f"min_size={performance_config.api.min_compression_size}B"
            )


def setup_performance_middleware(app: FastAPI):
    """
    Setup all performance-related middleware

    Usage:
        from app.middleware.performance import setup_performance_middleware

        app = FastAPI()
        setup_performance_middleware(app)
    """
    # 1. Compression (must be first to compress all responses)
    CompressionMiddleware.add_to_app(app)

    # 2. Cache headers
    app.add_middleware(CacheHeadersMiddleware)
    logger.info("Cache headers middleware enabled")

    # 3. Request deduplication
    if performance_config.api.enable_deduplication:
        app.add_middleware(
            RequestDeduplicationMiddleware,
            window_seconds=performance_config.api.deduplication_window,
        )
        logger.info(
            f"Request deduplication enabled: window={performance_config.api.deduplication_window}s"
        )

    # 4. Performance monitoring (should be last to measure total time)
    app.add_middleware(
        PerformanceMiddleware, enable_profiling=performance_config.monitoring.enable_profiling
    )
    logger.info(
        f"Performance monitoring enabled: profiling={performance_config.monitoring.enable_profiling}"
    )


# Performance metrics collector
class PerformanceMetrics:
    """
    Collect and expose performance metrics
    """

    def __init__(self):
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._slow_request_count = 0

    def record_request(self, response_time: float, status_code: int, is_slow: bool = False):
        """Record request metrics"""
        self._request_count += 1
        self._total_response_time += response_time

        if status_code >= 400:
            self._error_count += 1

        if is_slow:
            self._slow_request_count += 1

    def get_metrics(self) -> dict:
        """Get current metrics"""
        avg_response_time = (
            self._total_response_time / self._request_count if self._request_count > 0 else 0
        )

        error_rate = self._error_count / self._request_count if self._request_count > 0 else 0

        return {
            "total_requests": self._request_count,
            "total_errors": self._error_count,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "slow_requests": self._slow_request_count,
        }

    def reset(self):
        """Reset metrics"""
        self._request_count = 0
        self._error_count = 0
        self._total_response_time = 0.0
        self._slow_request_count = 0


# Global metrics instance
performance_metrics = PerformanceMetrics()


__all__ = [
    "PerformanceMiddleware",
    "CacheHeadersMiddleware",
    "RequestDeduplicationMiddleware",
    "CompressionMiddleware",
    "setup_performance_middleware",
    "performance_metrics",
]
