"""Custom exceptions for the application"""


class AppException(Exception):
    """Base exception for application errors"""

    def __init__(self, status_code: int, detail: str, code: str = "error"):
        self.status_code = status_code
        self.detail = detail
        self.code = code
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Exception raised when a resource is not found"""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, code="not_found")


class UnauthorizedException(AppException):
    """Exception raised when user is not authenticated"""

    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail, code="unauthorized")


class ForbiddenException(AppException):
    """Exception raised when user does not have permission"""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=403, detail=detail, code="forbidden")


class BadRequestException(AppException):
    """Exception raised for bad requests"""

    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail, code="bad_request")


class ConflictException(AppException):
    """Exception raised when there's a conflict (e.g., duplicate resource)"""

    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail, code="conflict")
