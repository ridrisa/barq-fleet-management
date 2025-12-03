"""
BARQ Fleet Management - Exception Hierarchy

Comprehensive exception handling with:
- Consistent error response format
- Error codes for client handling
- User-friendly error messages
- Detailed logging information

Usage:
    from app.core.exceptions import NotFoundException, ValidationException

    # Raise with default message
    raise NotFoundException()

    # Raise with custom message
    raise NotFoundException(detail="Courier not found", resource="courier")

    # Raise with error code for specific handling
    raise ValidationException(
        detail="Invalid phone number format",
        code="INVALID_PHONE_FORMAT"
    )
"""

from typing import Any, Dict, List, Optional


class ErrorCode:
    """
    Centralized error codes for consistent API responses.

    Clients can use these codes for:
    - Localization
    - Specific error handling
    - Analytics
    """

    # General errors (1000-1999)
    INTERNAL_ERROR = "ERR_1000"
    VALIDATION_ERROR = "ERR_1001"
    BAD_REQUEST = "ERR_1002"
    NOT_FOUND = "ERR_1003"
    CONFLICT = "ERR_1004"
    RATE_LIMITED = "ERR_1005"
    SERVICE_UNAVAILABLE = "ERR_1006"

    # Authentication errors (2000-2999)
    UNAUTHORIZED = "ERR_2000"
    INVALID_CREDENTIALS = "ERR_2001"
    TOKEN_EXPIRED = "ERR_2002"
    TOKEN_INVALID = "ERR_2003"
    TOKEN_REVOKED = "ERR_2004"
    ACCOUNT_LOCKED = "ERR_2005"
    ACCOUNT_DISABLED = "ERR_2006"
    REFRESH_TOKEN_EXPIRED = "ERR_2007"
    OAUTH_ERROR = "ERR_2008"

    # Authorization errors (3000-3999)
    FORBIDDEN = "ERR_3000"
    INSUFFICIENT_PERMISSIONS = "ERR_3001"
    ROLE_REQUIRED = "ERR_3002"
    RESOURCE_ACCESS_DENIED = "ERR_3003"

    # Resource errors (4000-4999)
    RESOURCE_NOT_FOUND = "ERR_4000"
    RESOURCE_ALREADY_EXISTS = "ERR_4001"
    RESOURCE_DELETED = "ERR_4002"
    RESOURCE_LOCKED = "ERR_4003"
    RESOURCE_ARCHIVED = "ERR_4004"

    # Validation errors (5000-5999)
    FIELD_REQUIRED = "ERR_5000"
    FIELD_INVALID = "ERR_5001"
    FIELD_TOO_SHORT = "ERR_5002"
    FIELD_TOO_LONG = "ERR_5003"
    FIELD_OUT_OF_RANGE = "ERR_5004"
    INVALID_FORMAT = "ERR_5005"
    INVALID_EMAIL = "ERR_5006"
    INVALID_PHONE = "ERR_5007"
    INVALID_DATE = "ERR_5008"
    INVALID_FILE_TYPE = "ERR_5009"
    FILE_TOO_LARGE = "ERR_5010"

    # Business logic errors (6000-6999)
    OPERATION_NOT_ALLOWED = "ERR_6000"
    STATE_TRANSITION_INVALID = "ERR_6001"
    DEPENDENCY_ERROR = "ERR_6002"
    QUOTA_EXCEEDED = "ERR_6003"
    DUPLICATE_ENTRY = "ERR_6004"
    WORKFLOW_ERROR = "ERR_6005"
    ASSIGNMENT_CONFLICT = "ERR_6006"

    # External service errors (7000-7999)
    EXTERNAL_SERVICE_ERROR = "ERR_7000"
    DATABASE_ERROR = "ERR_7001"
    CACHE_ERROR = "ERR_7002"
    EMAIL_SERVICE_ERROR = "ERR_7003"
    SMS_SERVICE_ERROR = "ERR_7004"
    STORAGE_ERROR = "ERR_7005"
    OAUTH_PROVIDER_ERROR = "ERR_7006"


class AppException(Exception):
    """
    Base exception for all application errors.

    Provides consistent error response format across the API.

    Attributes:
        status_code: HTTP status code
        detail: Human-readable error message
        code: Machine-readable error code
        errors: List of detailed error information
        headers: Optional response headers
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.code = code
        self.errors = errors or []
        self.headers = headers
        super().__init__(self.detail)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for JSON response."""
        response = {
            "error": {
                "code": self.code,
                "message": self.detail,
                "status": self.status_code,
            }
        }
        if self.errors:
            response["error"]["details"] = self.errors
        return response


# =============================================================================
# HTTP 400 - Bad Request Exceptions
# =============================================================================


class BadRequestException(AppException):
    """Exception raised for bad requests (400)."""

    def __init__(
        self,
        detail: str = "The request could not be processed",
        code: str = ErrorCode.BAD_REQUEST,
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(status_code=400, detail=detail, code=code, errors=errors)


class ValidationException(BadRequestException):
    """Exception raised for validation errors (400)."""

    def __init__(
        self,
        detail: str = "Validation failed",
        code: str = ErrorCode.VALIDATION_ERROR,
        errors: Optional[List[Dict[str, Any]]] = None,
        field: Optional[str] = None,
    ) -> None:
        if field and not errors:
            errors = [{"field": field, "message": detail}]
        super().__init__(detail=detail, code=code, errors=errors)


# =============================================================================
# HTTP 401 - Unauthorized Exceptions
# =============================================================================


class UnauthorizedException(AppException):
    """Exception raised when user is not authenticated (401)."""

    def __init__(
        self,
        detail: str = "Authentication required",
        code: str = ErrorCode.UNAUTHORIZED,
    ) -> None:
        super().__init__(
            status_code=401,
            detail=detail,
            code=code,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(UnauthorizedException):
    """Exception raised for invalid login credentials."""

    def __init__(
        self,
        detail: str = "Invalid email or password",
    ) -> None:
        super().__init__(detail=detail, code=ErrorCode.INVALID_CREDENTIALS)


class TokenExpiredException(UnauthorizedException):
    """Exception raised when authentication token has expired."""

    def __init__(
        self,
        detail: str = "Your session has expired, please login again",
    ) -> None:
        super().__init__(detail=detail, code=ErrorCode.TOKEN_EXPIRED)


class TokenInvalidException(UnauthorizedException):
    """Exception raised when authentication token is invalid."""

    def __init__(
        self,
        detail: str = "Invalid authentication token",
    ) -> None:
        super().__init__(detail=detail, code=ErrorCode.TOKEN_INVALID)


class AccountLockedException(UnauthorizedException):
    """Exception raised when account is locked due to too many failed attempts."""

    def __init__(
        self,
        detail: str = "Account temporarily locked due to too many failed login attempts",
        lockout_minutes: int = 15,
    ) -> None:
        super().__init__(
            detail=f"{detail}. Please try again in {lockout_minutes} minutes.",
            code=ErrorCode.ACCOUNT_LOCKED,
        )


class AccountDisabledException(UnauthorizedException):
    """Exception raised when account is disabled."""

    def __init__(
        self,
        detail: str = "Your account has been disabled. Please contact support.",
    ) -> None:
        super().__init__(detail=detail, code=ErrorCode.ACCOUNT_DISABLED)


# =============================================================================
# HTTP 403 - Forbidden Exceptions
# =============================================================================


class ForbiddenException(AppException):
    """Exception raised when user does not have permission (403)."""

    def __init__(
        self,
        detail: str = "You do not have permission to perform this action",
        code: str = ErrorCode.FORBIDDEN,
    ) -> None:
        super().__init__(status_code=403, detail=detail, code=code)


class InsufficientPermissionsException(ForbiddenException):
    """Exception raised when user lacks specific permissions."""

    def __init__(
        self,
        detail: str = "Insufficient permissions",
        required_permission: Optional[str] = None,
    ) -> None:
        if required_permission:
            detail = f"{detail}. Required permission: {required_permission}"
        super().__init__(detail=detail, code=ErrorCode.INSUFFICIENT_PERMISSIONS)


class RoleRequiredException(ForbiddenException):
    """Exception raised when user lacks required role."""

    def __init__(
        self,
        detail: str = "This action requires elevated privileges",
        required_role: Optional[str] = None,
    ) -> None:
        if required_role:
            detail = f"{detail}. Required role: {required_role}"
        super().__init__(detail=detail, code=ErrorCode.ROLE_REQUIRED)


# =============================================================================
# HTTP 404 - Not Found Exceptions
# =============================================================================


class NotFoundException(AppException):
    """Exception raised when a resource is not found (404)."""

    def __init__(
        self,
        detail: str = "Resource not found",
        code: str = ErrorCode.RESOURCE_NOT_FOUND,
        resource: Optional[str] = None,
        resource_id: Optional[Any] = None,
    ) -> None:
        if resource:
            detail = f"{resource.capitalize()} not found"
            if resource_id:
                detail = f"{resource.capitalize()} with ID '{resource_id}' not found"
        super().__init__(status_code=404, detail=detail, code=code)


# =============================================================================
# HTTP 409 - Conflict Exceptions
# =============================================================================


class ConflictException(AppException):
    """Exception raised when there's a conflict (409)."""

    def __init__(
        self,
        detail: str = "Resource already exists",
        code: str = ErrorCode.CONFLICT,
    ) -> None:
        super().__init__(status_code=409, detail=detail, code=code)


class DuplicateEntryException(ConflictException):
    """Exception raised when trying to create a duplicate resource."""

    def __init__(
        self,
        detail: str = "A resource with this identifier already exists",
        field: Optional[str] = None,
    ) -> None:
        if field:
            detail = f"A resource with this {field} already exists"
        super().__init__(detail=detail, code=ErrorCode.DUPLICATE_ENTRY)


class StateTransitionException(ConflictException):
    """Exception raised when a state transition is not allowed."""

    def __init__(
        self,
        detail: str = "This state transition is not allowed",
        current_state: Optional[str] = None,
        target_state: Optional[str] = None,
    ) -> None:
        if current_state and target_state:
            detail = f"Cannot transition from '{current_state}' to '{target_state}'"
        super().__init__(detail=detail, code=ErrorCode.STATE_TRANSITION_INVALID)


# =============================================================================
# HTTP 422 - Unprocessable Entity Exceptions
# =============================================================================


class UnprocessableEntityException(AppException):
    """Exception raised when request is valid but cannot be processed (422)."""

    def __init__(
        self,
        detail: str = "Request cannot be processed",
        code: str = ErrorCode.OPERATION_NOT_ALLOWED,
        errors: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        super().__init__(status_code=422, detail=detail, code=code, errors=errors)


# =============================================================================
# HTTP 429 - Rate Limited Exceptions
# =============================================================================


class RateLimitExceededException(AppException):
    """Exception raised when rate limit is exceeded (429)."""

    def __init__(
        self,
        detail: str = "Too many requests, please try again later",
        retry_after: int = 60,
    ) -> None:
        super().__init__(
            status_code=429,
            detail=detail,
            code=ErrorCode.RATE_LIMITED,
            headers={"Retry-After": str(retry_after)},
        )


# =============================================================================
# HTTP 500 - Internal Server Exceptions
# =============================================================================


class InternalServerException(AppException):
    """Exception raised for internal server errors (500)."""

    def __init__(
        self,
        detail: str = "An internal error occurred. Please try again later.",
        code: str = ErrorCode.INTERNAL_ERROR,
    ) -> None:
        super().__init__(status_code=500, detail=detail, code=code)


class DatabaseException(InternalServerException):
    """Exception raised for database errors."""

    def __init__(
        self,
        detail: str = "A database error occurred. Please try again.",
    ) -> None:
        super().__init__(detail=detail, code=ErrorCode.DATABASE_ERROR)


class ExternalServiceException(InternalServerException):
    """Exception raised for external service errors."""

    def __init__(
        self,
        detail: str = "An external service is currently unavailable",
        service: Optional[str] = None,
    ) -> None:
        if service:
            detail = f"{service} service is currently unavailable"
        super().__init__(detail=detail, code=ErrorCode.EXTERNAL_SERVICE_ERROR)


# =============================================================================
# HTTP 503 - Service Unavailable Exceptions
# =============================================================================


class ServiceUnavailableException(AppException):
    """Exception raised when service is unavailable (503)."""

    def __init__(
        self,
        detail: str = "Service temporarily unavailable. Please try again later.",
        retry_after: int = 30,
    ) -> None:
        super().__init__(
            status_code=503,
            detail=detail,
            code=ErrorCode.SERVICE_UNAVAILABLE,
            headers={"Retry-After": str(retry_after)},
        )


# =============================================================================
# Exception Mapping for FastAPI
# =============================================================================


def get_exception_handlers() -> Dict[type, Any]:
    """
    Get exception handlers for FastAPI application.

    Usage:
        from app.core.exceptions import get_exception_handlers

        app = FastAPI()
        for exc_class, handler in get_exception_handlers().items():
            app.add_exception_handler(exc_class, handler)
    """
    from fastapi import Request
    from fastapi.responses import JSONResponse

    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
            headers=exc.headers,
        )

    return {AppException: app_exception_handler}


__all__ = [
    # Error codes
    "ErrorCode",
    # Base exception
    "AppException",
    # 400 exceptions
    "BadRequestException",
    "ValidationException",
    # 401 exceptions
    "UnauthorizedException",
    "InvalidCredentialsException",
    "TokenExpiredException",
    "TokenInvalidException",
    "AccountLockedException",
    "AccountDisabledException",
    # 403 exceptions
    "ForbiddenException",
    "InsufficientPermissionsException",
    "RoleRequiredException",
    # 404 exceptions
    "NotFoundException",
    # 409 exceptions
    "ConflictException",
    "DuplicateEntryException",
    "StateTransitionException",
    # 422 exceptions
    "UnprocessableEntityException",
    # 429 exceptions
    "RateLimitExceededException",
    # 500 exceptions
    "InternalServerException",
    "DatabaseException",
    "ExternalServiceException",
    # 503 exceptions
    "ServiceUnavailableException",
    # Utilities
    "get_exception_handlers",
]
