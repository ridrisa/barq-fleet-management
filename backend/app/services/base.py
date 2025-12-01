from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from app.models.base import BaseModel as DBBaseModel


ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD service with common database operations
    """

    def __init__(self, model: Type[ModelType]):
        """
        Initialize CRUD service with model
        Args:
            model: SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a single record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filtering
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Dictionary of field:value filters
            order_by: Field name to order by (prefix with - for descending)
        """
        query = db.query(self.model)

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)

        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                query = query.order_by(getattr(self.model, order_by[1:]).desc())
            else:
                query = query.order_by(getattr(self.model, order_by))
        else:
            # Default order by created_at descending
            if hasattr(self.model, "created_at"):
                query = query.order_by(self.model.created_at.desc())

        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count total records matching filters
        """
        query = db.query(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)

        return query.count()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record
        Args:
            db: Database session
            obj_in: Pydantic schema with creation data
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record
        Args:
            db: Database session
            db_obj: Existing database object
            obj_in: Pydantic schema or dict with update data
        """
        obj_data = db_obj.__dict__
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[ModelType]:
        """
        Delete a record by ID
        """
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def search(
        self,
        db: Session,
        *,
        search_term: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Search records across multiple fields
        Args:
            db: Database session
            search_term: Search string
            search_fields: List of field names to search in
            skip: Number of records to skip
            limit: Maximum number of records to return
        """
        query = db.query(self.model)

        if search_term and search_fields:
            search_filters = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_filters.append(
                        getattr(self.model, field).ilike(f"%{search_term}%")
                    )

            if search_filters:
                query = query.filter(or_(*search_filters))

        return query.offset(skip).limit(limit).all()

    def bulk_create(self, db: Session, *, obj_list: List[CreateSchemaType]) -> List[ModelType]:
        """
        Create multiple records at once
        """
        db_objs = [self.model(**obj.model_dump()) for obj in obj_list]
        db.add_all(db_objs)
        db.commit()
        for obj in db_objs:
            db.refresh(obj)
        return db_objs

    def bulk_update(
        self,
        db: Session,
        *,
        ids: List[int],
        update_data: Dict[str, Any]
    ) -> int:
        """
        Update multiple records at once
        Returns: Number of records updated
        """
        result = db.query(self.model).filter(self.model.id.in_(ids)).update(
            update_data, synchronize_session=False
        )
        db.commit()
        return result

    def bulk_delete(self, db: Session, *, ids: List[int]) -> int:
        """
        Delete multiple records at once
        Returns: Number of records deleted
        """
        result = db.query(self.model).filter(self.model.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.commit()
        return result
