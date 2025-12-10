from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.fleet.document import Document, DocumentEntity, DocumentType
from app.schemas.fleet.document import DocumentCreate, DocumentUpdate
from app.services.base import CRUDBase


class DocumentService(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    """Service for Document operations with business logic"""

    def get_by_entity(
        self,
        db: Session,
        *,
        entity_type: DocumentEntity,
        entity_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Document]:
        """Get all documents for a specific entity (courier or vehicle)"""
        return (
            db.query(Document)
            .filter(
                Document.entity_type == entity_type,
                Document.entity_id == entity_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_entity_type(
        self,
        db: Session,
        *,
        entity_type: DocumentEntity,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Document]:
        """Get all documents for an entity type (all couriers or all vehicles)"""
        query = db.query(Document).filter(Document.entity_type == entity_type)

        if organization_id:
            query = query.filter(Document.organization_id == organization_id)

        return query.offset(skip).limit(limit).all()

    def get_by_document_type(
        self,
        db: Session,
        *,
        document_type: DocumentType,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Document]:
        """Get all documents of a specific type"""
        query = db.query(Document).filter(Document.document_type == document_type)

        if organization_id:
            query = query.filter(Document.organization_id == organization_id)

        return query.offset(skip).limit(limit).all()

    def get_expiring_documents(
        self,
        db: Session,
        *,
        days_threshold: int = 30,
        entity_type: Optional[DocumentEntity] = None,
        organization_id: Optional[int] = None,
    ) -> List[Document]:
        """Get documents expiring within threshold days"""
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        query = db.query(Document).filter(
            and_(
                Document.expiry_date != None,
                Document.expiry_date <= threshold_date,
            )
        )

        if entity_type:
            query = query.filter(Document.entity_type == entity_type)

        if organization_id:
            query = query.filter(Document.organization_id == organization_id)

        return query.order_by(Document.expiry_date.asc()).all()

    def get_expired_documents(
        self,
        db: Session,
        *,
        entity_type: Optional[DocumentEntity] = None,
        organization_id: Optional[int] = None,
    ) -> List[Document]:
        """Get all expired documents"""
        today = date.today()

        query = db.query(Document).filter(
            and_(
                Document.expiry_date != None,
                Document.expiry_date < today,
            )
        )

        if entity_type:
            query = query.filter(Document.entity_type == entity_type)

        if organization_id:
            query = query.filter(Document.organization_id == organization_id)

        return query.order_by(Document.expiry_date.asc()).all()

    def get_courier_documents(
        self,
        db: Session,
        courier_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Document]:
        """Get all documents for a courier"""
        return self.get_by_entity(
            db,
            entity_type=DocumentEntity.COURIER,
            entity_id=courier_id,
            skip=skip,
            limit=limit,
        )

    def get_vehicle_documents(
        self,
        db: Session,
        vehicle_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Document]:
        """Get all documents for a vehicle"""
        return self.get_by_entity(
            db,
            entity_type=DocumentEntity.VEHICLE,
            entity_id=vehicle_id,
            skip=skip,
            limit=limit,
        )

    def search_documents(
        self,
        db: Session,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Document]:
        """Search documents by name, number, or notes"""
        query = db.query(Document)

        if organization_id:
            query = query.filter(Document.organization_id == organization_id)

        if search_term:
            search_filters = [
                Document.document_name.ilike(f"%{search_term}%"),
                Document.document_number.ilike(f"%{search_term}%"),
                Document.notes.ilike(f"%{search_term}%"),
            ]
            query = query.filter(or_(*search_filters))

        return query.offset(skip).limit(limit).all()

    def get_statistics(
        self,
        db: Session,
        *,
        entity_type: Optional[DocumentEntity] = None,
        organization_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get document statistics"""
        from sqlalchemy import func

        today = date.today()
        threshold_30_days = today + timedelta(days=30)

        base_query = db.query(Document)

        if entity_type:
            base_query = base_query.filter(Document.entity_type == entity_type)

        if organization_id:
            base_query = base_query.filter(Document.organization_id == organization_id)

        total = base_query.with_entities(func.count(Document.id)).scalar()

        # Count by document type
        type_counts = (
            base_query.with_entities(Document.document_type, func.count(Document.id))
            .group_by(Document.document_type)
            .all()
        )

        # Count by entity type
        entity_counts = (
            base_query.with_entities(Document.entity_type, func.count(Document.id))
            .group_by(Document.entity_type)
            .all()
        )

        # Count expired
        expired_count = (
            base_query.filter(
                and_(
                    Document.expiry_date != None,
                    Document.expiry_date < today,
                )
            )
            .with_entities(func.count(Document.id))
            .scalar()
        )

        # Count expiring soon (within 30 days)
        expiring_soon_count = (
            base_query.filter(
                and_(
                    Document.expiry_date != None,
                    Document.expiry_date >= today,
                    Document.expiry_date <= threshold_30_days,
                )
            )
            .with_entities(func.count(Document.id))
            .scalar()
        )

        return {
            "total": total,
            "type_breakdown": dict(type_counts),
            "entity_breakdown": dict(entity_counts),
            "expired": expired_count,
            "expiring_soon": expiring_soon_count,
        }


# Create instance
document_service = DocumentService(Document)
