"""
BARQ Fleet Management - Structured Logging Configuration

Provides production-grade logging with:
- JSON structured logging for log aggregation (ELK, CloudWatch, etc.)
- Human-readable text format for development
- Request/response logging
- Performance logging
- Error tracking
- Correlation IDs for request tracing

Usage:
    from app.core.logging import setup_logging, get_logger

    # Setup at application startup
    setup_logging()

    # Get logger in modules
    logger = get_logger(__name__)
    logger.info("Processing request", extra={"user_id": 123, "action": "login"})
"""

import json
import logging
import os
import sys
import time
import traceback
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

# Context variable for request correlation
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")
request_start_time_var: ContextVar[float] = ContextVar("request_start_time", default=0.0)


class LogLevel:
    """Log level constants."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs log records as JSON for easy parsing by log aggregation tools.
    """

    def __init__(
        self,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_logger: bool = True,
        include_correlation_id: bool = True,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__()
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_logger = include_logger
        self.include_correlation_id = include_correlation_id
        self.extra_fields = extra_fields or {}

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {}

        # Timestamp
        if self.include_timestamp:
            log_data["timestamp"] = datetime.now(timezone.utc).isoformat()

        # Log level
        if self.include_level:
            log_data["level"] = record.levelname

        # Logger name
        if self.include_logger:
            log_data["logger"] = record.name

        # Correlation ID
        if self.include_correlation_id:
            correlation_id = correlation_id_var.get()
            if correlation_id:
                log_data["correlation_id"] = correlation_id

        # Message
        log_data["message"] = record.getMessage()

        # Location info
        log_data["location"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Extra fields from log call
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "taskName",
                "message",
            ):
                log_data[key] = value

        # Global extra fields
        log_data.update(self.extra_fields)

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development.

    Outputs colored, formatted logs for terminal viewing.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def __init__(self, use_colors: bool = True) -> None:
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as human-readable text."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        level = record.levelname

        # Color the level
        if self.use_colors and level in self.COLORS:
            level = f"{self.COLORS[level]}{level:8}{self.RESET}"
        else:
            level = f"{level:8}"

        # Build message
        message = record.getMessage()

        # Add correlation ID if present
        correlation_id = correlation_id_var.get()
        if correlation_id:
            correlation_display = f"[{correlation_id[:8]}] "
        else:
            correlation_display = ""

        # Format the base message
        formatted = f"{timestamp} | {level} | {record.name:30} | {correlation_display}{message}"

        # Add extra fields
        extras = []
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "exc_info",
                "exc_text",
                "thread",
                "threadName",
                "taskName",
                "message",
            ):
                extras.append(f"{key}={value}")

        if extras:
            formatted += f" | {', '.join(extras)}"

        # Add exception info
        if record.exc_info:
            formatted += f"\n{''.join(traceback.format_exception(*record.exc_info))}"

        return formatted


def setup_logging(
    level: str = "INFO",
    format_type: str = "json",
    extra_fields: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Setup logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Output format ('json' or 'text')
        extra_fields: Additional fields to include in all log messages
    """
    # Get settings from environment
    level = os.getenv("LOG_LEVEL", level).upper()
    format_type = os.getenv("LOG_FORMAT", format_type).lower()

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Remove existing handlers
    root_logger.handlers = []

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level))

    # Set formatter
    if format_type == "json":
        handler.setFormatter(
            JSONFormatter(
                extra_fields={
                    "service": "barq-fleet-api",
                    "environment": os.getenv("ENVIRONMENT", "development"),
                    **(extra_fields or {}),
                }
            )
        )
    else:
        handler.setFormatter(TextFormatter())

    root_logger.addHandler(handler)

    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if os.getenv("DB_ECHO", "false").lower() == "true" else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """
    Set correlation ID for request tracing.

    Args:
        correlation_id: Correlation ID (generated if not provided)

    Returns:
        The correlation ID being used
    """
    if not correlation_id:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return correlation_id_var.get()


def log_request_start() -> None:
    """Log request start time for performance tracking."""
    request_start_time_var.set(time.time())


def get_request_duration() -> float:
    """Get request duration in seconds."""
    start_time = request_start_time_var.get()
    if start_time:
        return time.time() - start_time
    return 0.0


def log_performance(
    operation: str,
    duration_seconds: float,
    success: bool = True,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log performance metrics.

    Args:
        operation: Name of the operation
        duration_seconds: Duration in seconds
        success: Whether the operation succeeded
        extra: Additional context
    """
    logger = get_logger("performance")
    log_data = {
        "operation": operation,
        "duration_ms": round(duration_seconds * 1000, 2),
        "success": success,
        **(extra or {}),
    }

    if duration_seconds > 1.0:  # Slow operation threshold
        logger.warning(f"Slow operation: {operation}", extra=log_data)
    else:
        logger.info(f"Operation completed: {operation}", extra=log_data)


def log_external_call(
    service: str,
    endpoint: str,
    method: str,
    duration_seconds: float,
    status_code: Optional[int] = None,
    success: bool = True,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log external service calls.

    Args:
        service: Name of the external service
        endpoint: API endpoint called
        method: HTTP method
        duration_seconds: Duration in seconds
        status_code: HTTP status code
        success: Whether the call succeeded
        extra: Additional context
    """
    logger = get_logger("external_calls")
    log_data = {
        "service": service,
        "endpoint": endpoint,
        "method": method,
        "duration_ms": round(duration_seconds * 1000, 2),
        "status_code": status_code,
        "success": success,
        **(extra or {}),
    }

    if not success:
        logger.error(f"External call failed: {service} {method} {endpoint}", extra=log_data)
    elif duration_seconds > 2.0:  # Slow external call threshold
        logger.warning(f"Slow external call: {service} {method} {endpoint}", extra=log_data)
    else:
        logger.info(f"External call: {service} {method} {endpoint}", extra=log_data)


def log_database_query(
    query: str,
    duration_seconds: float,
    rows_affected: Optional[int] = None,
    success: bool = True,
) -> None:
    """
    Log database queries.

    Args:
        query: SQL query (truncated)
        duration_seconds: Duration in seconds
        rows_affected: Number of rows affected
        success: Whether the query succeeded
    """
    logger = get_logger("database")
    log_data = {
        "query": query[:200] + "..." if len(query) > 200 else query,
        "duration_ms": round(duration_seconds * 1000, 2),
        "rows_affected": rows_affected,
        "success": success,
    }

    threshold = float(os.getenv("SLOW_QUERY_THRESHOLD", "0.1"))
    if not success:
        logger.error("Database query failed", extra=log_data)
    elif duration_seconds > threshold:
        logger.warning("Slow database query", extra=log_data)
    elif os.getenv("LOG_QUERIES", "false").lower() == "true":
        logger.debug("Database query", extra=log_data)


def with_logging(
    operation_name: Optional[str] = None,
    log_args: bool = False,
    log_result: bool = False,
) -> Callable:
    """
    Decorator to add logging to functions.

    Args:
        operation_name: Name of the operation (defaults to function name)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            name = operation_name or func.__name__
            logger = get_logger(func.__module__)
            start_time = time.time()

            extra: Dict[str, Any] = {"operation": name}
            if log_args:
                extra["args"] = str(args)[:100]
                extra["kwargs"] = str(kwargs)[:100]

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                if log_result:
                    extra["result"] = str(result)[:100]
                extra["duration_ms"] = round(duration * 1000, 2)

                logger.info(f"Completed: {name}", extra=extra)
                return result

            except Exception as e:
                duration = time.time() - start_time
                extra["duration_ms"] = round(duration * 1000, 2)
                extra["error"] = str(e)

                logger.error(f"Failed: {name}", extra=extra, exc_info=True)
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            name = operation_name or func.__name__
            logger = get_logger(func.__module__)
            start_time = time.time()

            extra: Dict[str, Any] = {"operation": name}
            if log_args:
                extra["args"] = str(args)[:100]
                extra["kwargs"] = str(kwargs)[:100]

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                if log_result:
                    extra["result"] = str(result)[:100]
                extra["duration_ms"] = round(duration * 1000, 2)

                logger.info(f"Completed: {name}", extra=extra)
                return result

            except Exception as e:
                duration = time.time() - start_time
                extra["duration_ms"] = round(duration * 1000, 2)
                extra["error"] = str(e)

                logger.error(f"Failed: {name}", extra=extra, exc_info=True)
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class RequestLogger:
    """
    Middleware-compatible request logger.

    Usage with FastAPI:
        from app.core.logging import RequestLogger

        @app.middleware("http")
        async def log_requests(request: Request, call_next):
            return await RequestLogger.log_request(request, call_next)
    """

    @staticmethod
    async def log_request(request: Any, call_next: Callable) -> Any:
        """Log request/response details."""
        from starlette.requests import Request

        logger = get_logger("http")

        # Set correlation ID from header or generate new one
        correlation_id = request.headers.get("X-Correlation-ID")
        set_correlation_id(correlation_id)
        log_request_start()

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("User-Agent"),
            },
        )

        try:
            response = await call_next(request)
            duration = get_request_duration()

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                },
            )

            # Add correlation ID to response
            response.headers["X-Correlation-ID"] = get_correlation_id()
            return response

        except Exception as e:
            duration = get_request_duration()
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(e),
                },
                exc_info=True,
            )
            raise


__all__ = [
    "LogLevel",
    "JSONFormatter",
    "TextFormatter",
    "setup_logging",
    "get_logger",
    "set_correlation_id",
    "get_correlation_id",
    "log_request_start",
    "get_request_duration",
    "log_performance",
    "log_external_call",
    "log_database_query",
    "with_logging",
    "RequestLogger",
]
