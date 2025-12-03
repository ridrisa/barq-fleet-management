"""
Tenant-Aware CRUD Base Class

This module provides a tenant-aware CRUD base class that automatically handles
multi-tenancy by filtering all operations by organization_id.

The TenantAwareCRUD class extends CRUDBase with:
- Automatic organization filtering on all read operations
- Automatic organization_id injection on create operations
- Organization validation on update/delete operations
- Support for both RLS and application-level filtering

Usage:
    class CRUDCourier(TenantAwareCRUD[Courier, CourierCreate, CourierUpdate]):
        pass

    crud_courier = CRUDCourier(Courier)

    # All operations automatically filtered by organization_id
    couriers = crud_courier.get_multi(db, organization_id=1)
    courier = crud_courier.create(db, obj_in=data, organization_id=1)
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.database import Base
from app.crud.base import CRUDBase

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class TenantAwareCRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Tenant-aware CRUD base class with automatic organization filtering.

    This class provides all standard CRUD operations with built-in multi-tenancy
    support. All operations are scoped to a specific organization_id.

    Attributes:
        model: The SQLAlchemy model class

    Note:
        If using PostgreSQL RLS (Row-Level Security), the database will also
        enforce tenant isolation. This class provides application-level
        filtering as an additional layer of security.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD object with model class.

        Args:
            model: SQLAlchemy model class with organization_id column
        """
        self.model = model

    def get(self, db: Session, id: Any, organization_id: int) -> Optional[ModelType]:
        """
        Get a single record by ID within organization scope.

        Args:
            db: Database session
            id: Primary key of the record
            organization_id: Organization ID to filter by

        Returns:
            Model instance or None if not found
        """
        return (
            db.query(self.model)
            .filter(and_(self.model.id == id, self.model.organization_id == organization_id))
            .first()
        )

    def get_by_id_any_org(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID without organization filtering.

        WARNING: Only use this for admin/superuser operations.

        Args:
            db: Database session
            id: Primary key of the record

        Returns:
            Model instance or None if not found
        """
        return db.get(self.model, id)

    def get_multi(
        self, db: Session, organization_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records within organization scope.

        Args:
            db: Database session
            organization_id: Organization ID to filter by
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return (
            db.query(self.model)
            .filter(self.model.organization_id == organization_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_count(self, db: Session, organization_id: int) -> int:
        """
        Get count of records within organization scope.

        Args:
            db: Database session
            organization_id: Organization ID to filter by

        Returns:
            Count of records
        """
        return db.query(self.model).filter(self.model.organization_id == organization_id).count()

    def create(self, db: Session, *, obj_in: CreateSchemaType, organization_id: int) -> ModelType:
        """
        Create a new record with organization scope.

        Args:
            db: Database session
            obj_in: Pydantic schema with data to create
            organization_id: Organization ID to assign to the record

        Returns:
            Created model instance
        """
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["organization_id"] = organization_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_with_dict(
        self, db: Session, *, obj_in: Dict[str, Any], organization_id: int
    ) -> ModelType:
        """
        Create a new record from dictionary with organization scope.

        Args:
            db: Database session
            obj_in: Dictionary with data to create
            organization_id: Organization ID to assign to the record

        Returns:
            Created model instance
        """
        obj_in["organization_id"] = organization_id
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        organization_id: int,
    ) -> ModelType:
        """
        Update an existing record within organization scope.

        Args:
            db: Database session
            db_obj: Existing model instance to update
            obj_in: Pydantic schema or dict with update data
            organization_id: Organization ID to validate against

        Returns:
            Updated model instance

        Raises:
            ValueError: If record doesn't belong to organization
        """
        # Validate organization ownership
        if db_obj.organization_id != organization_id:
            raise ValueError("Record does not belong to this organization")

        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        # Prevent changing organization_id
        update_data.pop("organization_id", None)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int, organization_id: int) -> Optional[ModelType]:
        """
        Remove a record within organization scope.

        Args:
            db: Database session
            id: Primary key of record to delete
            organization_id: Organization ID to validate against

        Returns:
            Deleted model instance or None if not found
        """
        obj = self.get(db, id=id, organization_id=organization_id)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, id: int, organization_id: int) -> bool:
        """
        Check if a record exists within organization scope.

        Args:
            db: Database session
            id: Primary key to check
            organization_id: Organization ID to filter by

        Returns:
            True if record exists, False otherwise
        """
        return (
            db.query(self.model)
            .filter(and_(self.model.id == id, self.model.organization_id == organization_id))
            .first()
            is not None
        )

    def get_by_field(
        self, db: Session, organization_id: int, field_name: str, field_value: Any
    ) -> Optional[ModelType]:
        """
        Get a record by a specific field within organization scope.

        Args:
            db: Database session
            organization_id: Organization ID to filter by
            field_name: Name of the field to filter by
            field_value: Value to match

        Returns:
            Model instance or None if not found
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    getattr(self.model, field_name) == field_value,
                    self.model.organization_id == organization_id,
                )
            )
            .first()
        )

    def get_multi_by_field(
        self,
        db: Session,
        organization_id: int,
        field_name: str,
        field_value: Any,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Get multiple records by a specific field within organization scope.

        Args:
            db: Database session
            organization_id: Organization ID to filter by
            field_name: Name of the field to filter by
            field_value: Value to match
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    getattr(self.model, field_name) == field_value,
                    self.model.organization_id == organization_id,
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def bulk_create(
        self, db: Session, *, objs_in: List[CreateSchemaType], organization_id: int
    ) -> List[ModelType]:
        """
        Bulk create records within organization scope.

        Args:
            db: Database session
            objs_in: List of Pydantic schemas with data
            organization_id: Organization ID to assign to all records

        Returns:
            List of created model instances
        """
        db_objs = []
        for obj_in in objs_in:
            obj_in_data = jsonable_encoder(obj_in)
            obj_in_data["organization_id"] = organization_id
            db_obj = self.model(**obj_in_data)
            db_objs.append(db_obj)

        db.add_all(db_objs)
        db.commit()

        for db_obj in db_objs:
            db.refresh(db_obj)

        return db_objs

    def search(
        self,
        db: Session,
        organization_id: int,
        *,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """
        Search records with multiple filters within organization scope.

        Args:
            db: Database session
            organization_id: Organization ID to filter by
            filters: Dictionary of field_name: value pairs
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching model instances
        """
        query = db.query(self.model).filter(self.model.organization_id == organization_id)

        for field_name, field_value in filters.items():
            if hasattr(self.model, field_name) and field_value is not None:
                query = query.filter(getattr(self.model, field_name) == field_value)

        return query.offset(skip).limit(limit).all()


# Type alias for backward compatibility
TenantCRUD = TenantAwareCRUD


__all__ = [
    "TenantAwareCRUD",
    "TenantCRUD",
]
