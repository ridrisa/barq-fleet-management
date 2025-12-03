"""
Optimized Database Configuration
Production-ready database setup with connection pooling, query optimization, and read replicas
"""

import logging
import time
from contextlib import contextmanager
from typing import Any, Generator, Optional

from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, Session, declarative_base, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.config.settings import settings
from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)

# Base class for declarative models
Base = declarative_base()


class DatabaseManager:
    """
    Database manager with optimized connection pooling and query helpers
    """

    def __init__(self):
        self._write_engine: Optional[Engine] = None
        self._read_engines: list[Engine] = []
        self._session_factory: Optional[sessionmaker] = None
        self._current_read_replica = 0

    @property
    def write_engine(self) -> Engine:
        """Get or create the write engine (primary database)"""
        if self._write_engine is None:
            self._write_engine = self._create_engine(
                settings.SQLALCHEMY_DATABASE_URI, is_read_replica=False
            )
        return self._write_engine

    @property
    def read_engine(self) -> Engine:
        """
        Get read engine with round-robin load balancing
        Falls back to write engine if no read replicas configured
        """
        if not performance_config.database.enable_read_replicas or not self._read_engines:
            return self.write_engine

        # Round-robin selection
        engine = self._read_engines[self._current_read_replica]
        self._current_read_replica = (self._current_read_replica + 1) % len(self._read_engines)
        return engine

    @property
    def SessionLocal(self) -> sessionmaker:
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.write_engine,
                autoflush=False,
                autocommit=False,
                expire_on_commit=performance_config.database.expire_on_commit,
            )
        return self._session_factory

    def _create_engine(self, database_url: str, is_read_replica: bool = False) -> Engine:
        """
        Create database engine with optimized connection pooling

        Args:
            database_url: Database connection URL
            is_read_replica: Whether this is a read replica

        Returns:
            Configured SQLAlchemy Engine
        """
        config = performance_config.database

        # Pool configuration
        if config.pool_size > 0:
            poolclass = QueuePool
            pool_kwargs = {
                "pool_size": config.pool_size,
                "max_overflow": config.max_overflow,
                "pool_timeout": config.pool_timeout,
                "pool_recycle": config.pool_recycle,
                "pool_pre_ping": config.pool_pre_ping,
            }
        else:
            # Disable pooling (useful for serverless)
            poolclass = NullPool
            pool_kwargs = {}

        engine = create_engine(
            database_url, poolclass=poolclass, echo=config.echo_queries, future=True, **pool_kwargs
        )

        # Event listeners for performance monitoring
        self._setup_engine_events(engine, is_read_replica)

        logger.info(
            f"Created {'read replica' if is_read_replica else 'write'} engine: "
            f"pool_size={config.pool_size}, max_overflow={config.max_overflow}"
        )

        return engine

    def _setup_engine_events(self, engine: Engine, is_read_replica: bool):
        """Setup SQLAlchemy event listeners for monitoring"""

        if performance_config.monitoring.log_queries:

            @event.listens_for(engine, "before_cursor_execute")
            def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                conn.info.setdefault("query_start_time", []).append(time.time())
                if performance_config.monitoring.enable_profiling:
                    logger.debug(f"Query start: {statement[:100]}...")

            @event.listens_for(engine, "after_cursor_execute")
            def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                total = time.time() - conn.info["query_start_time"].pop()

                # Log slow queries
                if performance_config.monitoring.log_slow_queries_only:
                    if total >= performance_config.monitoring.slow_query_threshold:
                        logger.warning(
                            f"Slow query ({total:.3f}s) on {'replica' if is_read_replica else 'primary'}: "
                            f"{statement[:200]}..."
                        )
                else:
                    logger.debug(f"Query executed in {total:.3f}s: {statement[:100]}...")

    def initialize_read_replicas(self):
        """Initialize read replica connections"""
        if not performance_config.database.enable_read_replicas:
            logger.info("Read replicas disabled")
            return

        replica_urls = performance_config.database.read_replica_urls
        if not replica_urls:
            logger.warning("Read replicas enabled but no URLs configured")
            return

        for url in replica_urls:
            if url:  # Skip empty strings
                try:
                    engine = self._create_engine(url, is_read_replica=True)
                    self._read_engines.append(engine)
                    logger.info(f"Initialized read replica: {url}")
                except Exception as e:
                    logger.error(f"Failed to initialize read replica {url}: {e}")

        logger.info(f"Initialized {len(self._read_engines)} read replicas")

    def create_session(self, use_read_replica: bool = False) -> Session:
        """
        Create a new database session

        Args:
            use_read_replica: Use read replica for this session

        Returns:
            SQLAlchemy Session
        """
        if use_read_replica:
            return Session(bind=self.read_engine)
        return self.SessionLocal()

    @contextmanager
    def session_scope(self, use_read_replica: bool = False) -> Generator[Session, None, None]:
        """
        Context manager for database sessions with automatic rollback on error

        Usage:
            with db_manager.session_scope() as session:
                session.query(User).all()
        """
        session = self.create_session(use_read_replica=use_read_replica)
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def close_all_connections(self):
        """Close all database connections (useful for cleanup)"""
        if self._write_engine:
            self._write_engine.dispose()
            logger.info("Disposed write engine")

        for engine in self._read_engines:
            engine.dispose()

        if self._read_engines:
            logger.info(f"Disposed {len(self._read_engines)} read replica engines")

        self._read_engines.clear()
        self._write_engine = None
        self._session_factory = None


# Global database manager instance
db_manager = DatabaseManager()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for database session with rollback safety

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = db_manager.create_session()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_read_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency for read-only database session (uses read replica if available)

    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_read_db)):
            return db.query(User).all()
    """
    db = db_manager.create_session(use_read_replica=True)
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Query optimization helpers
class OptimizedQuery:
    """Helper class for optimized database queries"""

    @staticmethod
    def paginate(query: Query, page: int = 1, page_size: int = 50) -> tuple[list[Any], int]:
        """
        Optimized pagination with total count

        Args:
            query: SQLAlchemy query
            page: Page number (1-indexed)
            page_size: Items per page

        Returns:
            Tuple of (items, total_count)
        """
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 50
        if page_size > 1000:  # Prevent excessive page sizes
            page_size = 1000

        # Get total count (optimized)
        total = query.count()

        # Get paginated items
        items = query.offset((page - 1) * page_size).limit(page_size).all()

        return items, total

    @staticmethod
    def batch_fetch(
        session: Session, model_class: type, ids: list[Any], batch_size: int = 100
    ) -> list[Any]:
        """
        Batch fetch records by IDs to avoid N+1 queries

        Args:
            session: Database session
            model_class: SQLAlchemy model class
            ids: List of IDs to fetch
            batch_size: Batch size for fetching

        Returns:
            List of model instances
        """
        if not ids:
            return []

        results = []
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_results = session.query(model_class).filter(model_class.id.in_(batch_ids)).all()
            results.extend(batch_results)

        return results

    @staticmethod
    def exists(query: Query) -> bool:
        """
        Optimized exists check (better than count() > 0)

        Args:
            query: SQLAlchemy query

        Returns:
            Boolean indicating if any records exist
        """
        return query.limit(1).count() > 0


# Database initialization
def initialize_database():
    """Initialize database with read replicas"""
    logger.info("Initializing database connections...")

    # Test write connection
    try:
        with db_manager.session_scope() as session:
            session.execute("SELECT 1")
        logger.info("Write database connection successful")
    except Exception as e:
        logger.error(f"Failed to connect to write database: {e}")
        raise

    # Initialize read replicas
    db_manager.initialize_read_replicas()

    logger.info("Database initialization complete")


def close_database():
    """Close all database connections"""
    logger.info("Closing database connections...")
    db_manager.close_all_connections()
    logger.info("Database connections closed")


# ============================================================================
# Multi-Tenancy Support
# ============================================================================


def get_tenant_db(
    organization_id: int, is_superuser: bool = False
) -> Generator[Session, None, None]:
    """
    Get database session with tenant context for Row-Level Security (RLS).

    This function sets PostgreSQL session variables that are used by RLS policies
    to enforce tenant isolation at the database level.

    Args:
        organization_id: The organization ID to scope queries to
        is_superuser: If True, bypasses RLS policies for admin access

    Yields:
        Database session with RLS context configured

    Usage:
        async def get_couriers(
            db: Session = Depends(get_tenant_db_dependency)
        ):
            # Automatically filtered by organization_id via RLS
            return db.query(Courier).all()
    """
    db = db_manager.create_session()
    try:
        # Set RLS context variables for tenant isolation
        db.execute(text("SET app.current_org_id = :org_id"), {"org_id": str(int(organization_id))})
        db.execute(text("SET app.is_superuser = :is_super"), {"is_super": str(is_superuser).lower()})
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        # Reset context variables to prevent leaking to connection pool
        try:
            db.execute(text("RESET app.current_org_id"))
            db.execute(text("RESET app.is_superuser"))
        except Exception:
            pass
        db.close()


class TenantContext:
    """
    Context manager for tenant-scoped database operations.

    Usage:
        with TenantContext(organization_id=1) as db:
            couriers = db.query(Courier).all()
    """

    def __init__(self, organization_id: int, is_superuser: bool = False):
        self.organization_id = organization_id
        self.is_superuser = is_superuser
        self.session: Optional[Session] = None

    def __enter__(self) -> Session:
        self.session = db_manager.create_session()
        self.session.execute(text("SET app.current_org_id = :org_id"), {"org_id": str(int(self.organization_id))})
        self.session.execute(text("SET app.is_superuser = :is_super"), {"is_super": str(self.is_superuser).lower()})
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is not None:
                self.session.rollback()
            else:
                self.session.commit()

            # Reset context
            try:
                self.session.execute(text("RESET app.current_org_id"))
                self.session.execute(text("RESET app.is_superuser"))
            except Exception:
                pass

            self.session.close()


# Import text for SQL execution
from sqlalchemy import text

# Export commonly used items
__all__ = [
    "Base",
    "db_manager",
    "get_db",
    "get_read_db",
    "get_tenant_db",
    "TenantContext",
    "OptimizedQuery",
    "initialize_database",
    "close_database",
]
