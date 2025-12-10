"""
Performance Monitoring Middleware
Tracks request timing, adds performance headers, and logs slow requests

Note: Uses pure ASGI middleware instead of BaseHTTPMiddleware to avoid
Content-Length issues with GZipMiddleware compression.
"""

import logging
import time
from typing import Callable, Any

from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send, Message

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)


class PerformanceMiddleware:
    """
    Pure ASGI Middleware for request performance monitoring

    Features:
    - Request timing
    - Performance metrics collection
    - Slow request logging
    - Response time headers (added via custom send wrapper)

    Note: Uses pure ASGI to avoid BaseHTTPMiddleware buffering issues with GZip.
    """

    def __init__(self, app: ASGIApp, enable_profiling: bool = False):
        self.app = app
        self.enable_profiling = enable_profiling
        self.slow_threshold = performance_config.monitoring.slow_query_threshold

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        request = Request(scope)

        # Store start time in request state
        scope.setdefault("state", {})
        scope["state"]["start_time"] = start_time

        status_code = 0
        headers_sent = False

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code, headers_sent

            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
                process_time = time.time() - start_time

                # Add performance headers
                headers = list(message.get("headers", []))
                headers.append((b"x-process-time", f"{process_time:.3f}".encode()))

                request_id = scope.get("state", {}).get("request_id", "unknown")
                headers.append((b"x-request-id", str(request_id).encode()))

                message = {
                    "type": message["type"],
                    "status": status_code,
                    "headers": headers,
                }
                headers_sent = True

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- {process_time:.3f}s - {type(e).__name__}: {str(e)}"
            )
            raise
        finally:
            process_time = time.time() - start_time

            # Log slow requests
            if process_time >= self.slow_threshold:
                logger.warning(
                    f"Slow request detected: {request.method} {request.url.path} "
                    f"- {process_time:.3f}s (threshold: {self.slow_threshold}s)"
                )

            # Detailed profiling if enabled
            if self.enable_profiling and headers_sent:
                logger.debug(
                    f"Request: {request.method} {request.url.path} "
                    f"- Status: {status_code} "
                    f"- Time: {process_time:.3f}s"
                )


class CacheHeadersMiddleware:
    """
    Pure ASGI Middleware for adding cache control headers

    Features:
    - Cache-Control headers
    - Proper header injection without buffering

    Note: Uses pure ASGI to avoid BaseHTTPMiddleware buffering issues with GZip.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start" and request.method == "GET":
                headers = list(message.get("headers", []))
                path = request.url.path

                # Determine cache policy
                if path.startswith("/api/v1/public"):
                    cache_control = b"public, max-age=3600"
                elif any(keyword in path for keyword in ["/vehicles", "/organizations"]):
                    cache_control = b"private, max-age=300"
                elif "/users" in path or "/profile" in path:
                    cache_control = b"private, max-age=60"
                else:
                    cache_control = b"no-cache, no-store, must-revalidate"
                    headers.append((b"pragma", b"no-cache"))
                    headers.append((b"expires", b"0"))

                headers.append((b"cache-control", cache_control))

                message = {
                    "type": message["type"],
                    "status": message.get("status", 200),
                    "headers": headers,
                }

            await send(message)

        await self.app(scope, receive, send_wrapper)


class RequestDeduplicationMiddleware:
    """
    Pure ASGI Middleware for request deduplication

    Prevents duplicate requests from being processed within a time window.

    Note: Simplified version - caching responses in ASGI is complex due to streaming.
    This version just tracks and logs duplicates without caching responses.
    """

    def __init__(self, app: ASGIApp, window_seconds: int = 5):
        self.app = app
        self.window_seconds = window_seconds
        self._request_timestamps: dict[str, float] = {}

    def _make_request_key(self, scope: Scope) -> str:
        """Generate unique key for request"""
        import hashlib

        request = Request(scope)
        key_parts = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items())),
        ]

        # Include user ID if authenticated
        user_id = scope.get("state", {}).get("user_id")
        if user_id:
            key_parts.append(str(user_id))

        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        # Only track idempotent methods
        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            await self.app(scope, receive, send)
            return

        request_key = self._make_request_key(scope)
        current_time = time.time()

        # Check for recent duplicate
        if request_key in self._request_timestamps:
            last_time = self._request_timestamps[request_key]
            if current_time - last_time < self.window_seconds:
                logger.debug(f"Duplicate request detected: {request.method} {request.url.path}")

        # Update timestamp
        self._request_timestamps[request_key] = current_time

        # Cleanup old entries periodically
        if len(self._request_timestamps) > 1000:
            self._cleanup_cache(current_time)

        await self.app(scope, receive, send)

    def _cleanup_cache(self, current_time: float):
        """Remove expired cache entries"""
        expired_keys = [
            key
            for key, timestamp in self._request_timestamps.items()
            if current_time - timestamp >= self.window_seconds
        ]

        for key in expired_keys:
            del self._request_timestamps[key]


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
