"""
Transaction Management Utilities

Provides context managers and decorators for safe database transactions
with automatic rollback on error.

This module implements several patterns for transaction management:

1. transactional() - Context manager for wrapping code blocks in transactions
2. atomic() - Simpler alias for transactional with common defaults
3. @transaction - Decorator for wrapping entire functions in transactions
4. UnitOfWork - Class-based pattern for complex multi-step operations

Usage Examples:

    # Basic usage with context manager
    from app.core.transaction import transactional

    def transfer_vehicle(db: Session, vehicle_id: int, new_courier_id: int):
        with transactional(db) as session:
            old_assignment = end_current_assignment(session, vehicle_id)
            new_assignment = create_assignment(session, vehicle_id, new_courier_id)
            return new_assignment
        # Commits automatically, rolls back on any exception

    # Using the decorator
    from app.core.transaction import transaction

    @transaction
    def bulk_update_status(db: Session, vehicle_ids: list, status: str):
        for vid in vehicle_ids:
            update_vehicle_status(db, vid, status)
        # All updates committed together or none at all

    # Using atomic() for cleaner syntax
    from app.core.transaction import atomic

    with atomic(db) as session:
        create_delivery(session, delivery_data)
        assign_courier(session, delivery_id, courier_id)
"""

import functools
import logging
from contextlib import contextmanager
from typing import Any, Callable, Generator, Optional, TypeVar

from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.service_exceptions import (
    ConcurrencyException,
    DuplicateEntityException,
    ServiceException,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TransactionError(Exception):
    """Raised when a transaction operation fails."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


@contextmanager
def transactional(
    db: Session,
    auto_commit: bool = True,
    raise_on_error: bool = True,
) -> Generator[Session, None, None]:
    """
    Context manager for database transactions with automatic rollback.

    Wraps a block of code in a database transaction. On successful completion,
    the transaction is committed (if auto_commit=True). On any exception,
    the transaction is rolled back.

    Args:
        db: Database session to use for the transaction
        auto_commit: Whether to commit on success (default True).
                     Set to False if you want to manage commit manually.
        raise_on_error: Whether to re-raise exceptions (default True).
                        Set to False to suppress errors after rollback.

    Yields:
        Database session

    Raises:
        SQLAlchemyError: If database operation fails and raise_on_error is True
        ServiceException: Re-raised as-is after rollback

    Example:
        with transactional(db) as session:
            service.create(session, data)
            service.update(session, id, data)
        # Auto-commits if no exception
    """
    try:
        yield db
        if auto_commit:
            db.commit()
            logger.debug("Transaction committed successfully")
    except IntegrityError as e:
        db.rollback()
        logger.warning(f"Transaction rolled back due to integrity error: {str(e)}")
        if raise_on_error:
            # Try to provide a more specific error
            error_str = str(e.orig) if e.orig else str(e)
            if "duplicate" in error_str.lower() or "unique" in error_str.lower():
                raise DuplicateEntityException(
                    entity_type="Entity",
                    field="unknown",
                    value="unknown",
                    message=f"Duplicate entry detected: {error_str}",
                ) from e
            raise
    except OperationalError as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to operational error: {str(e)}")
        if raise_on_error:
            # Check for lock-related errors
            error_str = str(e.orig) if e.orig else str(e)
            if "lock" in error_str.lower() or "deadlock" in error_str.lower():
                raise ConcurrencyException(
                    entity_type="Entity",
                    entity_id="unknown",
                    message=f"Concurrent modification detected: {error_str}",
                ) from e
            raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to database error: {str(e)}")
        if raise_on_error:
            raise
    except ServiceException:
        # Service exceptions should be re-raised as-is
        db.rollback()
        logger.debug("Transaction rolled back due to service exception")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction rolled back due to unexpected error: {str(e)}")
        if raise_on_error:
            raise


@contextmanager
def atomic(db: Session) -> Generator[Session, None, None]:
    """
    Alias for transactional() with default settings for cleaner syntax.

    This is the recommended way to wrap database operations that should
    succeed or fail together.

    Example:
        with atomic(db) as session:
            # Multiple operations that should succeed or fail together
            create_vehicle(session, vehicle_data)
            create_initial_inspection(session, vehicle_id)
    """
    with transactional(db, auto_commit=True, raise_on_error=True) as session:
        yield session


@contextmanager
def read_only(db: Session) -> Generator[Session, None, None]:
    """
    Context manager for read-only database operations.

    Ensures no commits happen and rolls back any accidental modifications.
    Useful for queries that should never modify data.

    Example:
        with read_only(db) as session:
            vehicles = session.query(Vehicle).all()
            # Any accidental modifications will be rolled back
    """
    try:
        yield db
    finally:
        db.rollback()


def transaction(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for wrapping a function in a database transaction.

    The decorated function must have 'db: Session' as its first parameter.
    The transaction is committed on success and rolled back on any exception.

    Args:
        func: Function to wrap. Must accept db: Session as first parameter.

    Returns:
        Wrapped function with transaction handling

    Example:
        @transaction
        def create_user_with_profile(db: Session, user_data: dict):
            user = user_service.create(db, user_data)
            profile_service.create(db, user.id, {})
            return user

        # The transaction commits if both operations succeed,
        # rolls back if either fails
    """
    @functools.wraps(func)
    def wrapper(db: Session, *args: Any, **kwargs: Any) -> T:
        with transactional(db):
            return func(db, *args, **kwargs)
    return wrapper


def transaction_with_options(
    auto_commit: bool = True,
    raise_on_error: bool = True,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator factory for transaction with custom options.

    Args:
        auto_commit: Whether to commit on success
        raise_on_error: Whether to re-raise exceptions

    Returns:
        Decorator function

    Example:
        @transaction_with_options(auto_commit=False)
        def bulk_operation(db: Session, items: list):
            for item in items:
                process(db, item)
            # Manual commit required
            db.commit()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(db: Session, *args: Any, **kwargs: Any) -> T:
            with transactional(db, auto_commit=auto_commit, raise_on_error=raise_on_error):
                return func(db, *args, **kwargs)
        return wrapper
    return decorator


class UnitOfWork:
    """
    Unit of Work pattern implementation for complex transactions.

    Use this when you need explicit control over transaction boundaries
    or when coordinating multiple service operations.

    Attributes:
        db: The database session
        committed: Whether the transaction has been committed

    Example:
        with UnitOfWork(db) as uow:
            vehicle = vehicle_service.create(uow.db, vehicle_data)
            assignment = assignment_service.create(uow.db, {
                "vehicle_id": vehicle.id,
                "courier_id": courier_id,
            })
            uow.commit()  # Explicit commit

        # Or with auto-commit:
        with UnitOfWork(db, auto_commit=True) as uow:
            vehicle = vehicle_service.create(uow.db, vehicle_data)
            # Commits automatically on exit
    """

    def __init__(self, db: Session, auto_commit: bool = False):
        """
        Initialize Unit of Work.

        Args:
            db: Database session to use
            auto_commit: If True, commit automatically on successful exit
        """
        self.db = db
        self.auto_commit = auto_commit
        self._committed = False
        self._rolled_back = False

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> bool:
        if exc_type is not None:
            self.rollback()
            return False  # Re-raise the exception

        if self.auto_commit and not self._committed and not self._rolled_back:
            self.commit()

        return False

    def commit(self) -> None:
        """
        Commit the transaction.

        Raises:
            TransactionError: If commit fails or transaction already finalized
        """
        if self._committed:
            raise TransactionError("Transaction already committed")
        if self._rolled_back:
            raise TransactionError("Cannot commit a rolled-back transaction")

        try:
            self.db.commit()
            self._committed = True
            logger.debug("UnitOfWork committed successfully")
        except SQLAlchemyError as e:
            self.rollback()
            logger.error(f"UnitOfWork commit failed: {str(e)}")
            raise TransactionError(
                f"Failed to commit transaction: {str(e)}",
                original_error=e,
            ) from e

    def rollback(self) -> None:
        """
        Rollback the transaction.

        Safe to call multiple times.
        """
        if not self._committed and not self._rolled_back:
            self.db.rollback()
            self._rolled_back = True
            logger.debug("UnitOfWork rolled back")

    @property
    def is_finalized(self) -> bool:
        """Check if the unit of work has been committed or rolled back."""
        return self._committed or self._rolled_back


class NestedTransaction:
    """
    Support for savepoints (nested transactions).

    Use this when you need to partially rollback a transaction
    while keeping earlier changes.

    Example:
        with transactional(db) as session:
            create_vehicle(session, vehicle_data)  # Will be kept

            with NestedTransaction(session) as nested:
                try:
                    create_assignment(session, assignment_data)
                except SomeError:
                    nested.rollback()  # Only rolls back the assignment
                    # Vehicle creation is preserved
    """

    def __init__(self, db: Session):
        self.db = db
        self._savepoint = None
        self._released = False

    def __enter__(self) -> "NestedTransaction":
        self._savepoint = self.db.begin_nested()
        return self

    def __exit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[Exception],
        exc_tb: Optional[Any],
    ) -> bool:
        if exc_type is not None and not self._released:
            self.rollback()
        elif not self._released:
            self.commit()
        return False

    def commit(self) -> None:
        """Commit the savepoint (release it)."""
        if not self._released and self._savepoint:
            self._savepoint.commit()
            self._released = True

    def rollback(self) -> None:
        """Rollback to the savepoint."""
        if not self._released and self._savepoint:
            self._savepoint.rollback()
            self._released = True


__all__ = [
    # Exceptions
    "TransactionError",
    # Context managers
    "transactional",
    "atomic",
    "read_only",
    # Decorators
    "transaction",
    "transaction_with_options",
    # Classes
    "UnitOfWork",
    "NestedTransaction",
]
