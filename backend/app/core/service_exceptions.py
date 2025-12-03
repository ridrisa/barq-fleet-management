"""
Service Layer Exceptions

Custom exceptions for the service layer providing clear error types
for different business rule violations and entity operations.

These exceptions allow the API layer to handle different error types
appropriately and return correct HTTP status codes.

This module is separate from app.core.exceptions which contains HTTP-specific
exceptions. Service exceptions represent business logic errors that can be
translated to HTTP responses by the API layer.

Usage:
    from app.core.service_exceptions import (
        EntityNotFoundException,
        DuplicateEntityException,
        BusinessRuleViolationException,
    )

    # In a service method
    def get_vehicle(self, db: Session, vehicle_id: int) -> Vehicle:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise EntityNotFoundException("Vehicle", vehicle_id)
        return vehicle

    # In an API endpoint, catch and convert to HTTP exception
    try:
        vehicle = vehicle_service.get_vehicle(db, vehicle_id)
    except EntityNotFoundException as e:
        raise HTTPException(status_code=404, detail=e.message)
"""

from typing import Any, Dict, Optional


class ServiceException(Exception):
    """
    Base exception for all service layer errors.

    All service-layer exceptions should inherit from this class to allow
    consistent handling in the API layer.

    Attributes:
        message: Human-readable error description
        details: Additional context as key-value pairs
        original_error: The underlying exception if wrapping another error
    """

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.original_error = original_error

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


class EntityNotFoundException(ServiceException):
    """
    Raised when a requested entity is not found.

    HTTP Status: 404 Not Found

    Example:
        raise EntityNotFoundException("Vehicle", vehicle_id)
        raise EntityNotFoundException("Courier", courier_id, "Courier is not active")
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        message: Optional[str] = None,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(
            message=message or f"{entity_type} with id {entity_id} not found",
            details={"entity_type": entity_type, "entity_id": str(entity_id)},
        )


class DuplicateEntityException(ServiceException):
    """
    Raised when attempting to create an entity that already exists.

    HTTP Status: 409 Conflict

    Example:
        raise DuplicateEntityException("Vehicle", "plate_number", "ABC-1234")
        raise DuplicateEntityException("User", "email", email, "Email already registered")
    """

    def __init__(
        self,
        entity_type: str,
        field: str,
        value: Any,
        message: Optional[str] = None,
    ):
        self.entity_type = entity_type
        self.field = field
        self.value = value
        super().__init__(
            message=message or f"{entity_type} with {field}='{value}' already exists",
            details={"entity_type": entity_type, "field": field, "value": str(value)},
        )


class BusinessRuleViolationException(ServiceException):
    """
    Raised when a business rule is violated.

    HTTP Status: 422 Unprocessable Entity

    Example:
        raise BusinessRuleViolationException(
            rule="vehicle_assignment",
            message="Vehicle is already assigned to another courier",
            details={"vehicle_id": 123, "current_courier_id": 456}
        )
    """

    def __init__(
        self,
        rule: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.rule = rule
        super().__init__(
            message=message,
            details={"rule": rule, **(details or {})},
        )


class UnauthorizedOperationException(ServiceException):
    """
    Raised when user is not authorized for an operation.

    HTTP Status: 403 Forbidden

    Example:
        raise UnauthorizedOperationException("delete", "Vehicle")
        raise UnauthorizedOperationException(
            "approve",
            "LeaveRequest",
            "Only managers can approve leave requests"
        )
    """

    def __init__(
        self,
        operation: str,
        resource: str,
        message: Optional[str] = None,
    ):
        self.operation = operation
        self.resource = resource
        super().__init__(
            message=message or f"Not authorized to {operation} on {resource}",
            details={"operation": operation, "resource": resource},
        )


class ValidationException(ServiceException):
    """
    Raised when input validation fails at the service layer.

    HTTP Status: 400 Bad Request

    Note: This is different from Pydantic validation which happens at the API layer.
    Use this for business-level validation (e.g., checking foreign key existence,
    validating business constraints).

    Example:
        raise ValidationException("courier_id", "Courier does not exist", courier_id)
        raise ValidationException("date_range", "End date must be after start date")
    """

    def __init__(
        self,
        field: str,
        message: str,
        value: Any = None,
    ):
        self.field = field
        self.value = value
        details = {"field": field}
        if value is not None:
            details["value"] = str(value)
        super().__init__(
            message=message,
            details=details,
        )


class ExternalServiceException(ServiceException):
    """
    Raised when an external service call fails.

    HTTP Status: 502 Bad Gateway or 503 Service Unavailable

    Example:
        raise ExternalServiceException("FMS API", "Connection timeout")
        raise ExternalServiceException(
            "SMS Gateway",
            "Failed to send verification code",
            original_error=e
        )
    """

    def __init__(
        self,
        service_name: str,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        self.service_name = service_name
        super().__init__(
            message=message,
            details={"service": service_name},
            original_error=original_error,
        )


class StateTransitionException(ServiceException):
    """
    Raised when an invalid state transition is attempted.

    HTTP Status: 409 Conflict or 422 Unprocessable Entity

    Example:
        raise StateTransitionException(
            "Delivery",
            current_state="delivered",
            target_state="pending",
            message="Cannot revert a delivered order to pending"
        )
    """

    def __init__(
        self,
        entity_type: str,
        current_state: str,
        target_state: str,
        message: Optional[str] = None,
    ):
        self.entity_type = entity_type
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(
            message=message or f"Cannot transition {entity_type} from '{current_state}' to '{target_state}'",
            details={
                "entity_type": entity_type,
                "current_state": current_state,
                "target_state": target_state,
            },
        )


class ConcurrencyException(ServiceException):
    """
    Raised when a concurrent modification conflict is detected.

    HTTP Status: 409 Conflict

    Example:
        raise ConcurrencyException(
            "Vehicle",
            vehicle_id,
            "Vehicle was modified by another user"
        )
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        message: Optional[str] = None,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(
            message=message or f"{entity_type} with id {entity_id} was modified by another operation",
            details={"entity_type": entity_type, "entity_id": str(entity_id)},
        )


class QuotaExceededException(ServiceException):
    """
    Raised when a resource quota or limit is exceeded.

    HTTP Status: 429 Too Many Requests or 422 Unprocessable Entity

    Example:
        raise QuotaExceededException(
            "vehicles",
            limit=50,
            current=50,
            message="Maximum vehicle limit reached for your organization"
        )
    """

    def __init__(
        self,
        resource: str,
        limit: int,
        current: int,
        message: Optional[str] = None,
    ):
        self.resource = resource
        self.limit = limit
        self.current = current
        super().__init__(
            message=message or f"{resource.capitalize()} quota exceeded (limit: {limit}, current: {current})",
            details={"resource": resource, "limit": limit, "current": current},
        )


class DependencyException(ServiceException):
    """
    Raised when an operation fails due to dependent resources.

    HTTP Status: 409 Conflict or 422 Unprocessable Entity

    Example:
        raise DependencyException(
            "Vehicle",
            vehicle_id,
            dependencies=["active_assignments", "pending_maintenance"],
            message="Cannot delete vehicle with active dependencies"
        )
    """

    def __init__(
        self,
        entity_type: str,
        entity_id: Any,
        dependencies: list,
        message: Optional[str] = None,
    ):
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.dependencies = dependencies
        super().__init__(
            message=message or f"Cannot modify {entity_type} with id {entity_id} due to existing dependencies",
            details={
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "dependencies": dependencies,
            },
        )


__all__ = [
    # Base exception
    "ServiceException",
    # Entity exceptions
    "EntityNotFoundException",
    "DuplicateEntityException",
    # Business rule exceptions
    "BusinessRuleViolationException",
    "UnauthorizedOperationException",
    "ValidationException",
    "StateTransitionException",
    # Resource exceptions
    "QuotaExceededException",
    "DependencyException",
    "ConcurrencyException",
    # External service exceptions
    "ExternalServiceException",
]
