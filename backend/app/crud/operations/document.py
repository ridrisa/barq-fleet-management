"""
Operations Document CRUD
"""

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.operations.document import DocumentCategory, OperationsDocument
from app.schemas.operations.document import OperationsDocumentCreate, OperationsDocumentUpdate


class CRUDOperationsDocument(
    CRUDBase[OperationsDocument, OperationsDocumentCreate, OperationsDocumentUpdate]
):
    """CRUD operations for operations documents"""

    def create(
        self, db: Session, *, obj_in: OperationsDocumentCreate, organization_id: int = None
    ) -> OperationsDocument:
        """Create with auto-generated doc_number"""
        # Generate doc_number
        max_id = db.query(func.coalesce(func.max(self.model.id), 0)).scalar() or 0
        doc_number = f"DOC-{(max_id + 1):05d}"

        obj_data = obj_in.model_dump()
        if organization_id:
            obj_data["organization_id"] = organization_id
        db_obj = self.model(**obj_data, doc_number=doc_number)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_category(
        self,
        db: Session,
        *,
        category: DocumentCategory,
        skip: int = 0,
        limit: int = 100,
        organization_id: int = None,
    ) -> List[OperationsDocument]:
        """Get documents by category"""
        query = db.query(self.model).filter(self.model.category == category)
        if organization_id:
            query = query.filter(self.model.organization_id == organization_id)
        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def increment_view_count(self, db: Session, *, doc_id: int) -> Optional[OperationsDocument]:
        """Increment document view count"""
        doc = self.get(db, id=doc_id)
        if doc:
            doc.view_count = (doc.view_count or 0) + 1
            db.commit()
            db.refresh(doc)
        return doc

    def increment_download_count(self, db: Session, *, doc_id: int) -> Optional[OperationsDocument]:
        """Increment document download count"""
        doc = self.get(db, id=doc_id)
        if doc:
            doc.download_count = (doc.download_count or 0) + 1
            db.commit()
            db.refresh(doc)
        return doc

    def search(
        self,
        db: Session,
        *,
        query: str,
        category: Optional[DocumentCategory] = None,
        skip: int = 0,
        limit: int = 100,
        organization_id: int = None,
    ) -> List[OperationsDocument]:
        """Search documents by name, description, or tags"""
        search_filter = (
            self.model.doc_name.ilike(f"%{query}%")
            | self.model.description.ilike(f"%{query}%")
            | self.model.tags.ilike(f"%{query}%")
        )

        q = db.query(self.model).filter(search_filter)

        if organization_id:
            q = q.filter(self.model.organization_id == organization_id)

        if category:
            q = q.filter(self.model.category == category)

        return q.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()


operations_document = CRUDOperationsDocument(OperationsDocument)
