"""
Query Optimizer Utilities
Provides helpers for optimizing database queries, preventing N+1 issues, and improving performance.

This module consolidates query optimization functionality:
- QueryOptimizer: Static methods for eager loading, pagination, and batch operations
- QueryAnalyzer: Query profiling and slow query detection
- N1QueryDetector: Detection of N+1 query patterns
- EagerLoadMixin: Mixin for service classes
- Convenience functions for common relationship loading patterns
"""

import logging
import re
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from sqlalchemy import event, func
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, Session, joinedload, selectinload, subqueryload

logger = logging.getLogger(__name__)

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType")
T = TypeVar("T")


class QueryOptimizer:
    """
    Utility class for optimizing database queries and preventing N+1 issues
    """

    @staticmethod
    def eager_load_relationships(
        query: Query, relationships: List[str], strategy: str = "selectinload"
    ) -> Query:
        """
        Apply eager loading to prevent N+1 queries

        Args:
            query: SQLAlchemy query object
            relationships: List of relationship names to eager load
            strategy: Loading strategy ('selectinload', 'joinedload', 'subqueryload')

        Returns:
            Query with eager loading applied

        Example:
            query = db.query(Courier)
            query = QueryOptimizer.eager_load_relationships(
                query,
                ['current_vehicle', 'vehicle_assignments'],
                strategy='selectinload'
            )
        """
        if not relationships:
            return query

        strategy_map = {
            "selectinload": selectinload,  # Best for one-to-many (default)
            "joinedload": joinedload,  # Best for one-to-one or many-to-one
            "subqueryload": subqueryload,  # Alternative for one-to-many
        }

        load_strategy = strategy_map.get(strategy, selectinload)

        for relationship in relationships:
            query = query.options(load_strategy(relationship))

        return query

    @staticmethod
    def paginate_with_count(
        query: Query, page: int = 1, page_size: int = 50, max_page_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Optimized pagination with total count

        Args:
            query: SQLAlchemy query object
            page: Page number (1-indexed)
            page_size: Items per page
            max_page_size: Maximum allowed page size

        Returns:
            Dictionary with items, total, page, page_size, total_pages
        """
        # Validate inputs
        page = max(1, page)
        page_size = min(max(1, page_size), max_page_size)

        # Get total count (optimized - uses COUNT(*) OVER() if possible)
        total = query.count()

        # Calculate pagination
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size

        # Get items
        items = query.offset(offset).limit(page_size).all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }

    @staticmethod
    def optimize_count_query(query: Query) -> int:
        """
        Optimized count query that avoids loading full objects

        Args:
            query: SQLAlchemy query object

        Returns:
            Count of matching records
        """
        # Use COUNT(*) instead of loading all objects
        count_query = query.statement.with_only_columns(func.count()).order_by(None)
        return query.session.execute(count_query).scalar()

    @staticmethod
    def exists(query: Query) -> bool:
        """
        Optimized existence check (better than count() > 0)

        Args:
            query: SQLAlchemy query object

        Returns:
            Boolean indicating if any records exist
        """
        return query.limit(1).first() is not None

    @staticmethod
    def batch_load_by_ids(
        session: Session,
        model: Type[ModelType],
        ids: List[int],
        batch_size: int = 100,
        relationships: Optional[List[str]] = None,
    ) -> List[ModelType]:
        """
        Batch load records by IDs to avoid N+1 queries

        Args:
            session: Database session
            model: SQLAlchemy model class
            ids: List of IDs to fetch
            batch_size: Batch size for fetching
            relationships: Optional relationships to eager load

        Returns:
            List of model instances
        """
        if not ids:
            return []

        results = []
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]
            query = session.query(model).filter(model.id.in_(batch_ids))

            if relationships:
                query = QueryOptimizer.eager_load_relationships(query, relationships)

            batch_results = query.all()
            results.extend(batch_results)

        return results

    @staticmethod
    def optimize_stats_query(
        session: Session, model: Type[ModelType], filters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Optimized statistics query using database aggregations

        Args:
            session: Database session
            model: SQLAlchemy model class
            filters: Optional filter conditions

        Returns:
            Dictionary with aggregated statistics
        """
        query = session.query(model)

        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == value)

        # Use database-level aggregations instead of Python loops
        total = query.count()

        return {"total": total}


class EagerLoadMixin:
    """
    Mixin for services to easily apply eager loading strategies
    """

    # Override in child classes to specify default relationships to eager load
    default_eager_load: List[str] = []

    def get_with_eager_load(
        self,
        db: Session,
        id: int,
        relationships: Optional[List[str]] = None,
        strategy: str = "selectinload",
    ) -> Optional[Any]:
        """
        Get single record with eager loading

        Args:
            db: Database session
            id: Record ID
            relationships: Relationships to eager load (uses default if None)
            strategy: Loading strategy

        Returns:
            Model instance or None
        """
        relationships = relationships or self.default_eager_load
        query = db.query(self.model).filter(self.model.id == id)

        if relationships:
            query = QueryOptimizer.eager_load_relationships(query, relationships, strategy)

        return query.first()

    def get_multi_with_eager_load(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        relationships: Optional[List[str]] = None,
        strategy: str = "selectinload",
        filters: Optional[Dict] = None,
    ) -> List[Any]:
        """
        Get multiple records with eager loading

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum records to return
            relationships: Relationships to eager load
            strategy: Loading strategy
            filters: Optional filter conditions

        Returns:
            List of model instances
        """
        relationships = relationships or self.default_eager_load
        query = db.query(self.model)

        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)

        # Apply eager loading
        if relationships:
            query = QueryOptimizer.eager_load_relationships(query, relationships, strategy)

        return query.offset(skip).limit(limit).all()


# Convenience functions for common patterns
def with_courier_relationships(query: Query) -> Query:
    """Apply common courier eager loading"""
    return QueryOptimizer.eager_load_relationships(
        query,
        ["current_vehicle", "organization"],
        strategy="joinedload",  # One-to-one relationships
    )


def with_vehicle_relationships(query: Query) -> Query:
    """Apply common vehicle eager loading"""
    return QueryOptimizer.eager_load_relationships(
        query, ["assigned_couriers", "organization"], strategy="selectinload"
    )


def with_delivery_relationships(query: Query) -> Query:
    """Apply common delivery eager loading"""
    return QueryOptimizer.eager_load_relationships(
        query, ["courier", "organization"], strategy="joinedload"
    )


def optimize_statistics_query(session: Session, model: Type, group_by_field: str, filters: Optional[Dict] = None):
    """
    Helper to create optimized statistics queries using SQL aggregations
    instead of Python loops

    Example:
        Instead of:
            deliveries = db.query(Delivery).all()
            pending = sum(1 for d in deliveries if d.status == 'pending')

        Use:
            stats = db.query(
                Delivery.status,
                func.count(Delivery.id)
            ).group_by(Delivery.status).all()
    """
    query = session.query(getattr(model, group_by_field), func.count(model.id))

    if filters:
        for key, value in filters.items():
            if hasattr(model, key):
                query = query.filter(getattr(model, key) == value)

    return query.group_by(getattr(model, group_by_field)).all()


class QueryAnalyzer:
    """
    Analyze database queries for performance issues.

    Features:
    - Slow query logging
    - Query execution statistics
    """

    def __init__(self, slow_threshold: float = 0.1):
        """
        Initialize query analyzer.

        Args:
            slow_threshold: Threshold in seconds for slow query warnings
        """
        self.slow_threshold = slow_threshold
        self._query_count = 0
        self._slow_query_count = 0
        self._total_query_time = 0.0
        self._queries: List[dict] = []

    def reset_stats(self):
        """Reset query statistics."""
        self._query_count = 0
        self._slow_query_count = 0
        self._total_query_time = 0.0
        self._queries.clear()

    def get_stats(self) -> dict:
        """Get query statistics."""
        avg_query_time = self._total_query_time / self._query_count if self._query_count > 0 else 0
        return {
            "total_queries": self._query_count,
            "slow_queries": self._slow_query_count,
            "total_time": self._total_query_time,
            "avg_time": avg_query_time,
            "slow_threshold": self.slow_threshold,
        }

    def record_query(self, statement: str, duration: float, params: Optional[dict] = None):
        """Record query execution."""
        self._query_count += 1
        self._total_query_time += duration

        if duration >= self.slow_threshold:
            self._slow_query_count += 1
            query_info = {
                "statement": statement[:500],
                "duration": duration,
                "params": params,
                "timestamp": time.time(),
            }
            self._queries.append(query_info)
            logger.warning(f"Slow query detected ({duration:.3f}s): {statement[:200]}...")

    def get_slow_queries(self, limit: int = 10) -> List[dict]:
        """Get slowest queries."""
        sorted_queries = sorted(self._queries, key=lambda q: q["duration"], reverse=True)
        return sorted_queries[:limit]


class N1QueryDetector:
    """
    Detect N+1 query problems.

    Features:
    - Track query patterns
    - Detect repeated similar queries
    """

    def __init__(self, threshold: int = 5):
        """
        Initialize N+1 detector.

        Args:
            threshold: Number of similar queries to trigger warning
        """
        self.threshold = threshold
        self._query_patterns: dict[str, int] = {}
        self._active = False

    def start_tracking(self):
        """Start tracking queries."""
        self._active = True
        self._query_patterns.clear()

    def stop_tracking(self):
        """Stop tracking queries."""
        self._active = False

    def record_query(self, statement: str):
        """Record query for N+1 detection."""
        if not self._active:
            return

        pattern = self._extract_pattern(statement)
        if pattern in self._query_patterns:
            self._query_patterns[pattern] += 1
            if self._query_patterns[pattern] == self.threshold:
                logger.warning(
                    f"Potential N+1 query detected: {pattern[:200]}... "
                    f"(executed {self.threshold} times). "
                    "Consider using eager loading (joinedload/selectinload)"
                )
        else:
            self._query_patterns[pattern] = 1

    @staticmethod
    def _extract_pattern(statement: str) -> str:
        """Extract query pattern by removing specific values."""
        pattern = re.sub(r"'[^']*'", "'?'", statement)
        pattern = re.sub(r"\b\d+\b", "?", pattern)
        pattern = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "?",
            pattern,
            flags=re.IGNORECASE,
        )
        return pattern

    def get_patterns(self) -> dict[str, int]:
        """Get detected query patterns."""
        return self._query_patterns.copy()


# Global instances
query_analyzer = QueryAnalyzer()
n1_detector = N1QueryDetector()


@contextmanager
def track_queries(session: Session):
    """
    Context manager to track queries within a block.

    Usage:
        with track_queries(session):
            users = session.query(User).all()
            for user in users:
                user.organization  # This might cause N+1
    """
    n1_detector.start_tracking()
    try:
        yield
    finally:
        n1_detector.stop_tracking()
        patterns = n1_detector.get_patterns()
        if patterns:
            logger.info(f"Query tracking summary: {len(patterns)} unique patterns")


def profile_query(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to profile query performance.

    Usage:
        @profile_query
        def get_users(session):
            return session.query(User).all()
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            query_analyzer.record_query(statement=func.__name__, duration=duration)
            if duration >= query_analyzer.slow_threshold:
                logger.warning(f"Slow function {func.__name__} took {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {e}")
            raise
    return wrapper


def setup_query_monitoring(engine: Engine):
    """
    Setup SQLAlchemy event listeners for query monitoring.

    Args:
        engine: SQLAlchemy engine
    """
    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        if "query_start_time" in conn.info and conn.info["query_start_time"]:
            duration = time.time() - conn.info["query_start_time"].pop()
            query_analyzer.record_query(statement, duration, parameters)
            n1_detector.record_query(statement)

    logger.info("Query monitoring enabled")


__all__ = [
    # Optimizer classes
    "QueryOptimizer",
    "EagerLoadMixin",
    # Monitoring classes
    "QueryAnalyzer",
    "N1QueryDetector",
    # Global instances
    "query_analyzer",
    "n1_detector",
    # Decorators and context managers
    "track_queries",
    "profile_query",
    "setup_query_monitoring",
    # Convenience functions
    "with_courier_relationships",
    "with_vehicle_relationships",
    "with_delivery_relationships",
    "optimize_statistics_query",
]
