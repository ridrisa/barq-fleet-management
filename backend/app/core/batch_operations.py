"""
Batch Operations Helper Module
Provides optimized batch operations for database updates, inserts, and deletes
"""

from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BatchOperations:
    """
    Helper class for efficient batch database operations
    """

    @staticmethod
    def batch_insert(
        db: Session,
        model_class: Type[T],
        objects: List[Dict[str, Any]],
        commit: bool = True
    ) -> int:
        """
        Batch insert multiple records efficiently

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            objects: List of dictionaries with object data
            commit: Whether to commit after insert

        Returns:
            Number of records inserted

        Example:
            couriers_data = [
                {"barq_id": "BRQ001", "full_name": "John Doe", ...},
                {"barq_id": "BRQ002", "full_name": "Jane Smith", ...},
            ]
            count = BatchOperations.batch_insert(db, Courier, couriers_data)
        """
        if not objects:
            return 0

        # Use bulk_insert_mappings for better performance
        db.bulk_insert_mappings(model_class, objects)

        if commit:
            db.commit()

        return len(objects)

    @staticmethod
    def batch_update(
        db: Session,
        model_class: Type[T],
        updates: List[Dict[str, Any]],
        id_field: str = "id",
        commit: bool = True
    ) -> int:
        """
        Batch update multiple records efficiently

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            updates: List of dictionaries with id and fields to update
            id_field: Name of the ID field (default: "id")
            commit: Whether to commit after update

        Returns:
            Number of records updated

        Example:
            updates = [
                {"id": 1, "status": "ACTIVE", "performance_score": 95.5},
                {"id": 2, "status": "INACTIVE", "performance_score": 70.0},
            ]
            count = BatchOperations.batch_update(db, Courier, updates)
        """
        if not updates:
            return 0

        # Use bulk_update_mappings for better performance
        db.bulk_update_mappings(model_class, updates)

        if commit:
            db.commit()

        return len(updates)

    @staticmethod
    def batch_update_field(
        db: Session,
        model_class: Type[T],
        ids: List[Any],
        field_updates: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
        commit: bool = True
    ) -> int:
        """
        Update a single field for multiple records

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            ids: List of record IDs to update
            field_updates: Dictionary of field names and values to update
            filters: Additional filters (e.g., {"organization_id": 1})
            commit: Whether to commit after update

        Returns:
            Number of records updated

        Example:
            # Set all specified couriers to ACTIVE status
            count = BatchOperations.batch_update_field(
                db, Courier,
                ids=[1, 2, 3],
                field_updates={"status": "ACTIVE"},
                filters={"organization_id": 1}
            )
        """
        if not ids or not field_updates:
            return 0

        query = db.query(model_class).filter(model_class.id.in_(ids))

        # Apply additional filters
        if filters:
            for field, value in filters.items():
                query = query.filter(getattr(model_class, field) == value)

        count = query.update(field_updates, synchronize_session=False)

        if commit:
            db.commit()

        return count

    @staticmethod
    def batch_delete(
        db: Session,
        model_class: Type[T],
        ids: List[Any],
        filters: Optional[Dict[str, Any]] = None,
        commit: bool = True
    ) -> int:
        """
        Delete multiple records efficiently

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            ids: List of record IDs to delete
            filters: Additional filters for safety (e.g., {"organization_id": 1})
            commit: Whether to commit after delete

        Returns:
            Number of records deleted

        Example:
            count = BatchOperations.batch_delete(
                db, Courier,
                ids=[1, 2, 3],
                filters={"organization_id": 1}
            )
        """
        if not ids:
            return 0

        query = db.query(model_class).filter(model_class.id.in_(ids))

        # Apply additional filters
        if filters:
            for field, value in filters.items():
                query = query.filter(getattr(model_class, field) == value)

        count = query.delete(synchronize_session=False)

        if commit:
            db.commit()

        return count

    @staticmethod
    def batch_soft_delete(
        db: Session,
        model_class: Type[T],
        ids: List[Any],
        deleted_at_field: str = "deleted_at",
        filters: Optional[Dict[str, Any]] = None,
        commit: bool = True
    ) -> int:
        """
        Soft delete multiple records (sets deleted_at timestamp)

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            ids: List of record IDs to soft delete
            deleted_at_field: Name of the deleted_at field
            filters: Additional filters
            commit: Whether to commit after update

        Returns:
            Number of records soft deleted
        """
        from datetime import datetime

        return BatchOperations.batch_update_field(
            db, model_class,
            ids=ids,
            field_updates={deleted_at_field: datetime.utcnow()},
            filters=filters,
            commit=commit
        )

    @staticmethod
    def batch_upsert(
        db: Session,
        model_class: Type[T],
        objects: List[Dict[str, Any]],
        unique_fields: List[str],
        update_fields: Optional[List[str]] = None,
        commit: bool = True
    ) -> Dict[str, int]:
        """
        Batch upsert (insert or update) records

        Args:
            db: Database session
            model_class: SQLAlchemy model class
            objects: List of dictionaries with object data
            unique_fields: List of field names that uniquely identify records
            update_fields: List of fields to update if record exists (None = all fields)
            commit: Whether to commit after operation

        Returns:
            Dictionary with counts: {"inserted": X, "updated": Y}

        Example:
            objects = [
                {"barq_id": "BRQ001", "full_name": "John Doe", "status": "ACTIVE"},
                {"barq_id": "BRQ002", "full_name": "Jane Smith", "status": "INACTIVE"},
            ]
            result = BatchOperations.batch_upsert(
                db, Courier, objects,
                unique_fields=["barq_id"],
                update_fields=["full_name", "status"]
            )
        """
        if not objects:
            return {"inserted": 0, "updated": 0}

        inserted = 0
        updated = 0

        for obj_data in objects:
            # Build filter for unique fields
            filters = {field: obj_data[field] for field in unique_fields if field in obj_data}

            # Check if record exists
            query = db.query(model_class)
            for field, value in filters.items():
                query = query.filter(getattr(model_class, field) == value)

            existing = query.first()

            if existing:
                # Update existing record
                if update_fields is None:
                    update_fields = [k for k in obj_data.keys() if k not in unique_fields]

                for field in update_fields:
                    if field in obj_data:
                        setattr(existing, field, obj_data[field])

                updated += 1
            else:
                # Insert new record
                new_obj = model_class(**obj_data)
                db.add(new_obj)
                inserted += 1

        if commit:
            db.commit()

        return {"inserted": inserted, "updated": updated}

    @staticmethod
    def chunked_operation(
        items: List[Any],
        chunk_size: int,
        operation_func: callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """
        Execute an operation on items in chunks

        Args:
            items: List of items to process
            chunk_size: Size of each chunk
            operation_func: Function to call for each chunk
            *args, **kwargs: Additional arguments to pass to operation_func

        Returns:
            List of results from each chunk operation

        Example:
            def update_chunk(db, ids):
                return BatchOperations.batch_update_field(
                    db, Courier, ids, {"status": "ACTIVE"}
                )

            results = BatchOperations.chunked_operation(
                items=courier_ids,
                chunk_size=100,
                operation_func=update_chunk,
                db=db
            )
        """
        results = []

        for i in range(0, len(items), chunk_size):
            chunk = items[i:i + chunk_size]
            result = operation_func(chunk, *args, **kwargs)
            results.append(result)

        return results


# Convenience functions for common operations

def bulk_update_courier_status(
    db: Session,
    courier_ids: List[int],
    status: str,
    organization_id: Optional[int] = None,
) -> int:
    """
    Bulk update courier status

    Example:
        count = bulk_update_courier_status(
            db, [1, 2, 3], "ACTIVE", organization_id=1
        )
    """
    from app.models.fleet.courier import Courier

    filters = {}
    if organization_id:
        filters["organization_id"] = organization_id

    return BatchOperations.batch_update_field(
        db, Courier,
        ids=courier_ids,
        field_updates={"status": status},
        filters=filters
    )


def bulk_assign_vehicles(
    db: Session,
    assignments: List[Dict[str, Any]],
    organization_id: Optional[int] = None,
) -> int:
    """
    Bulk create courier-vehicle assignments

    Args:
        assignments: List of dicts with courier_id, vehicle_id, start_date, etc.

    Example:
        assignments = [
            {"courier_id": 1, "vehicle_id": 10, "start_date": date.today()},
            {"courier_id": 2, "vehicle_id": 11, "start_date": date.today()},
        ]
        count = bulk_assign_vehicles(db, assignments, organization_id=1)
    """
    from app.models.fleet.assignment import CourierVehicleAssignment

    # Add organization_id to all assignments if provided
    if organization_id:
        for assignment in assignments:
            assignment["organization_id"] = organization_id

    return BatchOperations.batch_insert(db, CourierVehicleAssignment, assignments)


def bulk_update_performance_scores(
    db: Session,
    scores: List[Dict[str, Any]],
    organization_id: Optional[int] = None,
) -> int:
    """
    Bulk update courier performance scores

    Args:
        scores: List of dicts with id and performance_score

    Example:
        scores = [
            {"id": 1, "performance_score": 95.5, "total_deliveries": 150},
            {"id": 2, "performance_score": 88.0, "total_deliveries": 120},
        ]
        count = bulk_update_performance_scores(db, scores, organization_id=1)
    """
    from app.models.fleet.courier import Courier

    return BatchOperations.batch_update(db, Courier, scores)


# Export all
__all__ = [
    "BatchOperations",
    "bulk_update_courier_status",
    "bulk_assign_vehicles",
    "bulk_update_performance_scores",
]
