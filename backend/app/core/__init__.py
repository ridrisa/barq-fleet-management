"""
BARQ Fleet Management - Core Module

This module provides core functionality including:
- Exception handling (HTTP and Service layer)
- Logging
- Security
- Dependencies
- Validators
- Transaction management
"""

from app.core.exceptions import (
    AppException,
    BadRequestException,
    ConflictException,
    ErrorCode,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.core.logging import get_logger, setup_logging
from app.core.service_exceptions import (
    BusinessRuleViolationException,
    ConcurrencyException,
    DependencyException,
    DuplicateEntityException,
    EntityNotFoundException,
    ExternalServiceException,
    QuotaExceededException,
    ServiceException,
    StateTransitionException,
    UnauthorizedOperationException,
    ValidationException as ServiceValidationException,
)
from app.core.transaction import (
    NestedTransaction,
    TransactionError,
    UnitOfWork,
    atomic,
    read_only,
    transaction,
    transaction_with_options,
    transactional,
)

__all__ = [
    # HTTP Exceptions (for API layer)
    "AppException",
    "BadRequestException",
    "ConflictException",
    "ErrorCode",
    "ForbiddenException",
    "NotFoundException",
    "UnauthorizedException",
    "ValidationException",
    # Service Layer Exceptions
    "ServiceException",
    "EntityNotFoundException",
    "DuplicateEntityException",
    "BusinessRuleViolationException",
    "UnauthorizedOperationException",
    "ServiceValidationException",
    "ExternalServiceException",
    "StateTransitionException",
    "ConcurrencyException",
    "QuotaExceededException",
    "DependencyException",
    # Transaction Management
    "TransactionError",
    "transactional",
    "atomic",
    "read_only",
    "transaction",
    "transaction_with_options",
    "UnitOfWork",
    "NestedTransaction",
    # Logging
    "get_logger",
    "setup_logging",
]
