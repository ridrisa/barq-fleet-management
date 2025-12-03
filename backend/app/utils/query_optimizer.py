"""
Query Optimization Utilities
Tools for analyzing, profiling, and optimizing database queries
"""

import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, List, Optional, TypeVar

from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, Session

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)

T = TypeVar("T")


class QueryAnalyzer:
    """
    Analyze database queries for performance issues

    Features:
    - N+1 query detection
    - Slow query logging
    - Query execution statistics
    - EXPLAIN query analysis
    """

    def __init__(self, slow_threshold: float = 0.1):
        """
        Initialize query analyzer

        Args:
            slow_threshold: Threshold in seconds for slow query warnings
        """
        self.slow_threshold = slow_threshold
        self._query_count = 0
        self._slow_query_count = 0
        self._total_query_time = 0.0
        self._queries: List[dict] = []

    def reset_stats(self):
        """Reset query statistics"""
        self._query_count = 0
        self._slow_query_count = 0
        self._total_query_time = 0.0
        self._queries.clear()

    def get_stats(self) -> dict:
        """
        Get query statistics

        Returns:
            Dictionary with query stats
        """
        avg_query_time = self._total_query_time / self._query_count if self._query_count > 0 else 0

        return {
            "total_queries": self._query_count,
            "slow_queries": self._slow_query_count,
            "total_time": self._total_query_time,
            "avg_time": avg_query_time,
            "slow_threshold": self.slow_threshold,
        }

    def record_query(self, statement: str, duration: float, params: Optional[dict] = None):
        """
        Record query execution

        Args:
            statement: SQL statement
            duration: Execution duration in seconds
            params: Query parameters
        """
        self._query_count += 1
        self._total_query_time += duration

        if duration >= self.slow_threshold:
            self._slow_query_count += 1

            query_info = {
                "statement": statement[:500],  # Truncate long queries
                "duration": duration,
                "params": params,
                "timestamp": time.time(),
            }

            self._queries.append(query_info)

            logger.warning(f"Slow query detected ({duration:.3f}s): {statement[:200]}...")

    def get_slow_queries(self, limit: int = 10) -> List[dict]:
        """
        Get slowest queries

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of slow queries sorted by duration
        """
        sorted_queries = sorted(self._queries, key=lambda q: q["duration"], reverse=True)
        return sorted_queries[:limit]

    @staticmethod
    def explain_query(session: Session, query: Query) -> dict:
        """
        Get EXPLAIN output for query

        Args:
            session: Database session
            query: SQLAlchemy query

        Returns:
            Dictionary with EXPLAIN results
        """
        try:
            # Get compiled query
            compiled = query.statement.compile(compile_kwargs={"literal_binds": True})

            # Execute EXPLAIN
            explain_query = text(f"EXPLAIN ANALYZE {compiled}")
            result = session.execute(explain_query)

            explain_output = [row[0] for row in result]

            return {
                "query": str(compiled),
                "explain": explain_output,
            }
        except Exception as e:
            logger.error(f"Error analyzing query: {e}")
            return {"error": str(e)}


# Global query analyzer
query_analyzer = QueryAnalyzer(slow_threshold=performance_config.monitoring.slow_query_threshold)


class N1QueryDetector:
    """
    Detect N+1 query problems

    Features:
    - Track query patterns
    - Detect repeated similar queries
    - Suggest eager loading
    """

    def __init__(self, threshold: int = 5):
        """
        Initialize N+1 detector

        Args:
            threshold: Number of similar queries to trigger warning
        """
        self.threshold = threshold
        self._query_patterns: dict[str, int] = {}
        self._active = False

    def start_tracking(self):
        """Start tracking queries"""
        self._active = True
        self._query_patterns.clear()

    def stop_tracking(self):
        """Stop tracking queries"""
        self._active = False

    def record_query(self, statement: str):
        """
        Record query for N+1 detection

        Args:
            statement: SQL statement
        """
        if not self._active:
            return

        # Extract query pattern (remove specific values)
        pattern = self._extract_pattern(statement)

        if pattern in self._query_patterns:
            self._query_patterns[pattern] += 1

            # Check for N+1 pattern
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
        """
        Extract query pattern by removing specific values

        Args:
            statement: SQL statement

        Returns:
            Query pattern
        """
        import re

        # Remove quoted strings
        pattern = re.sub(r"'[^']*'", "'?'", statement)

        # Remove numbers
        pattern = re.sub(r"\b\d+\b", "?", pattern)

        # Remove UUIDs
        pattern = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "?",
            pattern,
            flags=re.IGNORECASE,
        )

        return pattern

    def get_patterns(self) -> dict[str, int]:
        """Get detected query patterns"""
        return self._query_patterns.copy()


# Global N+1 detector
n1_detector = N1QueryDetector()


@contextmanager
def track_queries(session: Session):
    """
    Context manager to track queries within a block

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

        # Log summary
        patterns = n1_detector.get_patterns()
        if patterns:
            logger.info(f"Query tracking summary: {len(patterns)} unique patterns")

            # Find potential N+1 queries
            potential_n1 = {
                pattern: count
                for pattern, count in patterns.items()
                if count >= n1_detector.threshold
            }

            if potential_n1:
                logger.warning(f"Potential N+1 queries detected: {len(potential_n1)} patterns")


def profile_query(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to profile query performance

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

            # Record query performance
            query_analyzer.record_query(statement=func.__name__, duration=duration)

            if duration >= query_analyzer.slow_threshold:
                logger.warning(f"Slow function {func.__name__} took {duration:.3f}s")

            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {e}")
            raise

    return wrapper


class QueryCache:
    """
    Simple query result cache

    Features:
    - In-memory cache for query results
    - TTL support
    - Query key generation
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize query cache

        Args:
            default_ttl: Default TTL in seconds
        """
        self.default_ttl = default_ttl
        self._cache: dict[str, tuple[Any, float]] = {}

    def _make_key(self, query: Query) -> str:
        """
        Generate cache key from query

        Args:
            query: SQLAlchemy query

        Returns:
            Cache key
        """
        import hashlib

        # Compile query to string
        compiled = str(query.statement.compile(compile_kwargs={"literal_binds": True}))

        return hashlib.md5(compiled.encode()).hexdigest()

    def get(self, query: Query) -> Optional[Any]:
        """
        Get cached query result

        Args:
            query: SQLAlchemy query

        Returns:
            Cached result or None
        """
        key = self._make_key(query)

        if key in self._cache:
            result, expires_at = self._cache[key]

            if time.time() < expires_at:
                logger.debug(f"Query cache hit: {key}")
                return result
            else:
                # Expired
                del self._cache[key]

        logger.debug(f"Query cache miss: {key}")
        return None

    def set(self, query: Query, result: Any, ttl: Optional[int] = None):
        """
        Cache query result

        Args:
            query: SQLAlchemy query
            result: Query result
            ttl: Time to live in seconds
        """
        key = self._make_key(query)
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl

        self._cache[key] = (result, expires_at)
        logger.debug(f"Query cached: {key} (ttl={ttl}s)")

    def clear(self):
        """Clear all cached queries"""
        self._cache.clear()
        logger.info("Query cache cleared")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "keys": list(self._cache.keys()),
        }


# Global query cache
query_cache = QueryCache()


def cached_query(ttl: Optional[int] = None):
    """
    Decorator to cache query results

    Usage:
        @cached_query(ttl=300)
        def get_active_users(session):
            return session.query(User).filter(User.is_active == True).all()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Try to extract query from function
            result = func(*args, **kwargs)

            # If result is a Query, cache it
            if isinstance(result, Query):
                cached = query_cache.get(result)
                if cached is not None:
                    return cached

                # Execute query
                executed_result = result.all()
                query_cache.set(result, executed_result, ttl)
                return executed_result

            return result

        return wrapper

    return decorator


def setup_query_monitoring(engine: Engine):
    """
    Setup SQLAlchemy event listeners for query monitoring

    Args:
        engine: SQLAlchemy engine

    Usage:
        from app.core.database import db_manager
        setup_query_monitoring(db_manager.write_engine)
    """

    @event.listens_for(engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Track query start time"""
        conn.info.setdefault("query_start_time", []).append(time.time())

    @event.listens_for(engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Track query execution and analyze"""
        if "query_start_time" in conn.info and conn.info["query_start_time"]:
            duration = time.time() - conn.info["query_start_time"].pop()

            # Record in query analyzer
            query_analyzer.record_query(statement, duration, parameters)

            # Record for N+1 detection
            n1_detector.record_query(statement)

    logger.info("Query monitoring enabled")


class QueryOptimizer:
    """
    Utility class for common query optimizations
    """

    @staticmethod
    def optimize_pagination(
        query: Query, page: int, page_size: int, count_query: Optional[Query] = None
    ) -> tuple[List[Any], int]:
        """
        Optimized pagination with efficient counting

        Args:
            query: Base query
            page: Page number (1-indexed)
            page_size: Items per page
            count_query: Optional separate count query

        Returns:
            Tuple of (items, total_count)
        """
        # Use separate count query if provided (more efficient)
        if count_query:
            total = count_query.count()
        else:
            total = query.count()

        # Get paginated items
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return items, total

    @staticmethod
    def batch_load_relationships(session: Session, instances: List[Any], *relationships: str):
        """
        Batch load relationships to avoid N+1 queries

        Args:
            session: Database session
            instances: List of model instances
            *relationships: Relationship attribute names

        Usage:
            users = session.query(User).all()
            QueryOptimizer.batch_load_relationships(session, users, 'organization', 'role')
        """
        from sqlalchemy.orm import joinedload

        if not instances:
            return

        model = type(instances[0])
        ids = [instance.id for instance in instances]

        # Reload with eager loading
        for relationship in relationships:
            query = session.query(model).filter(model.id.in_(ids))
            query = query.options(joinedload(relationship))
            query.all()

    @staticmethod
    def optimize_exists_check(query: Query) -> bool:
        """
        Optimized exists check (faster than count() > 0)

        Args:
            query: SQLAlchemy query

        Returns:
            True if any results exist
        """
        return query.limit(1).count() > 0


__all__ = [
    "QueryAnalyzer",
    "query_analyzer",
    "N1QueryDetector",
    "n1_detector",
    "track_queries",
    "profile_query",
    "QueryCache",
    "query_cache",
    "cached_query",
    "setup_query_monitoring",
    "QueryOptimizer",
]
