"""
Batch Operations Utilities
Efficient bulk insert, update, and processing operations
"""
import logging
from typing import Any, Callable, List, Optional, Type, TypeVar, Dict
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import update
from contextlib import contextmanager

from app.core.performance_config import performance_config

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BatchInsert:
    """
    Efficient batch insert operations

    Features:
    - Chunked batch inserts
    - Conflict handling (upsert)
    - Progress tracking
    - Transaction management
    """

    def __init__(self, chunk_size: int = 1000):
        """
        Initialize batch insert handler

        Args:
            chunk_size: Number of records per batch
        """
        self.chunk_size = chunk_size

    def insert(
        self,
        session: Session,
        model: Type[T],
        records: List[Dict[str, Any]],
        return_ids: bool = False
    ) -> Optional[List[Any]]:
        """
        Batch insert records

        Args:
            session: Database session
            model: SQLAlchemy model class
            records: List of record dictionaries
            return_ids: Whether to return inserted IDs

        Returns:
            List of inserted IDs if return_ids=True

        Usage:
            batch_insert = BatchInsert()
            records = [
                {"name": "User 1", "email": "user1@example.com"},
                {"name": "User 2", "email": "user2@example.com"},
            ]
            batch_insert.insert(session, User, records)
        """
        if not records:
            logger.warning("No records to insert")
            return []

        total = len(records)
        logger.info(f"Batch inserting {total} {model.__name__} records")

        inserted_ids = []

        # Process in chunks
        for i in range(0, total, self.chunk_size):
            chunk = records[i:i + self.chunk_size]

            try:
                # Bulk insert using SQLAlchemy
                if return_ids:
                    # Need to insert one by one to get IDs
                    for record in chunk:
                        instance = model(**record)
                        session.add(instance)
                        session.flush()
                        inserted_ids.append(instance.id)
                else:
                    # Bulk insert (faster)
                    session.bulk_insert_mappings(model, chunk)

                session.flush()

                logger.debug(
                    f"Inserted chunk {i // self.chunk_size + 1}: "
                    f"{len(chunk)} records ({i + len(chunk)}/{total})"
                )

            except Exception as e:
                logger.error(f"Error inserting chunk at index {i}: {e}")
                raise

        logger.info(f"Successfully inserted {total} {model.__name__} records")

        return inserted_ids if return_ids else None

    def upsert(
        self,
        session: Session,
        model: Type[T],
        records: List[Dict[str, Any]],
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None
    ):
        """
        Batch upsert (insert or update on conflict)

        Args:
            session: Database session
            model: SQLAlchemy model class
            records: List of record dictionaries
            conflict_columns: Columns to check for conflicts
            update_columns: Columns to update on conflict (None = update all)

        Usage:
            batch_insert = BatchInsert()
            records = [
                {"email": "user1@example.com", "name": "User 1"},
                {"email": "user2@example.com", "name": "User 2"},
            ]
            batch_insert.upsert(
                session, User, records,
                conflict_columns=["email"],
                update_columns=["name"]
            )
        """
        if not records:
            logger.warning("No records to upsert")
            return

        total = len(records)
        logger.info(f"Batch upserting {total} {model.__name__} records")

        # Process in chunks
        for i in range(0, total, self.chunk_size):
            chunk = records[i:i + self.chunk_size]

            try:
                # Use PostgreSQL INSERT ... ON CONFLICT
                stmt = insert(model).values(chunk)

                # Determine columns to update
                if update_columns:
                    update_dict = {
                        col: stmt.excluded[col]
                        for col in update_columns
                    }
                else:
                    # Update all columns except conflict columns
                    update_dict = {
                        col.name: stmt.excluded[col.name]
                        for col in model.__table__.columns
                        if col.name not in conflict_columns
                    }

                # Add ON CONFLICT clause
                stmt = stmt.on_conflict_do_update(
                    index_elements=conflict_columns,
                    set_=update_dict
                )

                session.execute(stmt)
                session.flush()

                logger.debug(
                    f"Upserted chunk {i // self.chunk_size + 1}: "
                    f"{len(chunk)} records ({i + len(chunk)}/{total})"
                )

            except Exception as e:
                logger.error(f"Error upserting chunk at index {i}: {e}")
                raise

        logger.info(f"Successfully upserted {total} {model.__name__} records")


class BatchUpdate:
    """
    Efficient batch update operations

    Features:
    - Chunked batch updates
    - Conditional updates
    - Progress tracking
    """

    def __init__(self, chunk_size: int = 1000):
        """
        Initialize batch update handler

        Args:
            chunk_size: Number of records per batch
        """
        self.chunk_size = chunk_size

    def update(
        self,
        session: Session,
        model: Type[T],
        updates: List[Dict[str, Any]],
        id_column: str = "id"
    ):
        """
        Batch update records by ID

        Args:
            session: Database session
            model: SQLAlchemy model class
            updates: List of update dictionaries (must include id_column)
            id_column: Name of ID column

        Usage:
            batch_update = BatchUpdate()
            updates = [
                {"id": 1, "name": "Updated User 1"},
                {"id": 2, "name": "Updated User 2"},
            ]
            batch_update.update(session, User, updates)
        """
        if not updates:
            logger.warning("No records to update")
            return

        total = len(updates)
        logger.info(f"Batch updating {total} {model.__name__} records")

        # Process in chunks
        for i in range(0, total, self.chunk_size):
            chunk = updates[i:i + self.chunk_size]

            try:
                # Bulk update using SQLAlchemy
                session.bulk_update_mappings(model, chunk)
                session.flush()

                logger.debug(
                    f"Updated chunk {i // self.chunk_size + 1}: "
                    f"{len(chunk)} records ({i + len(chunk)}/{total})"
                )

            except Exception as e:
                logger.error(f"Error updating chunk at index {i}: {e}")
                raise

        logger.info(f"Successfully updated {total} {model.__name__} records")

    def update_where(
        self,
        session: Session,
        model: Type[T],
        values: Dict[str, Any],
        filter_func: Callable[[Any], Any]
    ) -> int:
        """
        Batch update with WHERE clause

        Args:
            session: Database session
            model: SQLAlchemy model class
            values: Dictionary of values to update
            filter_func: Filter function for WHERE clause

        Returns:
            Number of updated records

        Usage:
            batch_update = BatchUpdate()
            count = batch_update.update_where(
                session,
                User,
                {"is_active": False},
                lambda q: q.filter(User.last_login < date(2023, 1, 1))
            )
        """
        try:
            # Build update statement
            stmt = update(model).values(**values)

            # Apply filter
            query = session.query(model)
            query = filter_func(query)

            # Execute update
            stmt = stmt.where(model.id.in_([obj.id for obj in query.all()]))
            result = session.execute(stmt)

            count = result.rowcount
            session.flush()

            logger.info(f"Updated {count} {model.__name__} records")
            return count

        except Exception as e:
            logger.error(f"Error in batch update where: {e}")
            raise


class BatchDelete:
    """
    Efficient batch delete operations

    Features:
    - Chunked batch deletes
    - Conditional deletes
    - Progress tracking
    """

    def __init__(self, chunk_size: int = 1000):
        """
        Initialize batch delete handler

        Args:
            chunk_size: Number of records per batch
        """
        self.chunk_size = chunk_size

    def delete_by_ids(
        self,
        session: Session,
        model: Type[T],
        ids: List[Any]
    ) -> int:
        """
        Batch delete records by IDs

        Args:
            session: Database session
            model: SQLAlchemy model class
            ids: List of record IDs to delete

        Returns:
            Number of deleted records

        Usage:
            batch_delete = BatchDelete()
            count = batch_delete.delete_by_ids(session, User, [1, 2, 3])
        """
        if not ids:
            logger.warning("No IDs to delete")
            return 0

        total = len(ids)
        logger.info(f"Batch deleting {total} {model.__name__} records")

        deleted_count = 0

        # Process in chunks
        for i in range(0, total, self.chunk_size):
            chunk = ids[i:i + self.chunk_size]

            try:
                # Delete by IDs
                result = session.query(model).filter(model.id.in_(chunk)).delete(
                    synchronize_session=False
                )

                deleted_count += result
                session.flush()

                logger.debug(
                    f"Deleted chunk {i // self.chunk_size + 1}: "
                    f"{len(chunk)} IDs ({i + len(chunk)}/{total})"
                )

            except Exception as e:
                logger.error(f"Error deleting chunk at index {i}: {e}")
                raise

        logger.info(f"Successfully deleted {deleted_count} {model.__name__} records")
        return deleted_count


class ChunkedProcessor:
    """
    Process large datasets in chunks

    Features:
    - Memory-efficient chunked processing
    - Progress tracking
    - Error handling per chunk
    """

    def __init__(self, chunk_size: int = 1000):
        """
        Initialize chunked processor

        Args:
            chunk_size: Number of items per chunk
        """
        self.chunk_size = chunk_size

    def process_query(
        self,
        session: Session,
        query: Any,
        processor: Callable[[List[Any]], Any],
        on_error: Optional[Callable[[Exception, List[Any]], None]] = None
    ) -> int:
        """
        Process query results in chunks

        Args:
            session: Database session
            query: SQLAlchemy query
            processor: Function to process each chunk
            on_error: Optional error handler

        Returns:
            Number of processed items

        Usage:
            def process_chunk(users):
                for user in users:
                    user.updated_at = datetime.utcnow()

            processor = ChunkedProcessor()
            count = processor.process_query(
                session,
                session.query(User),
                process_chunk
            )
        """
        total = query.count()
        logger.info(f"Processing {total} records in chunks of {self.chunk_size}")

        processed_count = 0

        # Process in chunks
        for i in range(0, total, self.chunk_size):
            chunk = query.offset(i).limit(self.chunk_size).all()

            try:
                processor(chunk)
                session.flush()

                processed_count += len(chunk)

                logger.debug(
                    f"Processed chunk {i // self.chunk_size + 1}: "
                    f"{len(chunk)} records ({processed_count}/{total})"
                )

            except Exception as e:
                logger.error(f"Error processing chunk at offset {i}: {e}")

                if on_error:
                    on_error(e, chunk)
                else:
                    raise

        logger.info(f"Successfully processed {processed_count} records")
        return processed_count

    def process_list(
        self,
        items: List[Any],
        processor: Callable[[List[Any]], Any],
        on_error: Optional[Callable[[Exception, List[Any]], None]] = None
    ) -> int:
        """
        Process list in chunks

        Args:
            items: List of items to process
            processor: Function to process each chunk
            on_error: Optional error handler

        Returns:
            Number of processed items

        Usage:
            def process_chunk(items):
                for item in items:
                    print(item)

            processor = ChunkedProcessor()
            count = processor.process_list(items, process_chunk)
        """
        total = len(items)
        logger.info(f"Processing {total} items in chunks of {self.chunk_size}")

        processed_count = 0

        # Process in chunks
        for i in range(0, total, self.chunk_size):
            chunk = items[i:i + self.chunk_size]

            try:
                processor(chunk)
                processed_count += len(chunk)

                logger.debug(
                    f"Processed chunk {i // self.chunk_size + 1}: "
                    f"{len(chunk)} items ({processed_count}/{total})"
                )

            except Exception as e:
                logger.error(f"Error processing chunk at index {i}: {e}")

                if on_error:
                    on_error(e, chunk)
                else:
                    raise

        logger.info(f"Successfully processed {processed_count} items")
        return processed_count


@contextmanager
def batch_session(session: Session, batch_size: int = 100):
    """
    Context manager for batch operations with auto-commit

    Args:
        session: Database session
        batch_size: Number of operations before commit

    Usage:
        with batch_session(session, batch_size=100) as batch:
            for i in range(1000):
                user = User(name=f"User {i}")
                session.add(user)
                batch.increment()  # Auto-commits every 100 operations
    """
    class BatchCounter:
        def __init__(self, session: Session, batch_size: int):
            self.session = session
            self.batch_size = batch_size
            self.count = 0

        def increment(self):
            self.count += 1
            if self.count % self.batch_size == 0:
                self.session.flush()
                logger.debug(f"Batch committed: {self.count} operations")

    counter = BatchCounter(session, batch_size)

    try:
        yield counter
        session.flush()  # Final flush
    except Exception as e:
        session.rollback()
        logger.error(f"Batch session error: {e}")
        raise


# Convenience functions
def bulk_insert(
    session: Session,
    model: Type[T],
    records: List[Dict[str, Any]],
    chunk_size: int = 1000
):
    """
    Convenience function for bulk insert

    Usage:
        bulk_insert(session, User, records)
    """
    batch_insert = BatchInsert(chunk_size=chunk_size)
    return batch_insert.insert(session, model, records)


def bulk_update(
    session: Session,
    model: Type[T],
    updates: List[Dict[str, Any]],
    chunk_size: int = 1000
):
    """
    Convenience function for bulk update

    Usage:
        bulk_update(session, User, updates)
    """
    batch_update = BatchUpdate(chunk_size=chunk_size)
    return batch_update.update(session, model, updates)


def bulk_delete(
    session: Session,
    model: Type[T],
    ids: List[Any],
    chunk_size: int = 1000
):
    """
    Convenience function for bulk delete

    Usage:
        bulk_delete(session, User, [1, 2, 3])
    """
    batch_delete = BatchDelete(chunk_size=chunk_size)
    return batch_delete.delete_by_ids(session, model, ids)


__all__ = [
    "BatchInsert",
    "BatchUpdate",
    "BatchDelete",
    "ChunkedProcessor",
    "batch_session",
    "bulk_insert",
    "bulk_update",
    "bulk_delete",
]
