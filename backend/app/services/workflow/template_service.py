"""Workflow Template Service"""

from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.workflow.template import WorkflowTemplate
from app.schemas.workflow import WorkflowTemplateCreate, WorkflowTemplateUpdate
from app.services.base import CRUDBase


class TemplateService(CRUDBase[WorkflowTemplate, WorkflowTemplateCreate, WorkflowTemplateUpdate]):
    """Service for workflow template management operations"""

    def get_active(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[WorkflowTemplate]:
        """Get all active workflow templates"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[WorkflowTemplate]:
        """Get workflow templates by category"""
        query = db.query(self.model).filter(self.model.category == category)

        return query.order_by(self.model.name).offset(skip).limit(limit).all()

    def get_by_type(
        self, db: Session, *, template_type: str, skip: int = 0, limit: int = 100
    ) -> List[WorkflowTemplate]:
        """Get workflow templates by type (category)"""
        return self.get_by_category(db, category=template_type, skip=skip, limit=limit)

    def activate_template(self, db: Session, *, template_id: int) -> Optional[WorkflowTemplate]:
        """Activate a workflow template"""
        template = db.query(self.model).filter(self.model.id == template_id).first()
        if not template:
            return None

        template.is_active = True
        db.commit()
        db.refresh(template)
        return template

    def deactivate_template(self, db: Session, *, template_id: int) -> Optional[WorkflowTemplate]:
        """Deactivate a workflow template"""
        template = db.query(self.model).filter(self.model.id == template_id).first()
        if not template:
            return None

        template.is_active = False
        db.commit()
        db.refresh(template)
        return template

    def get_categories(self, db: Session) -> List[str]:
        """Get all unique template categories"""
        categories = (
            db.query(self.model.category).distinct().filter(self.model.category.isnot(None)).all()
        )
        return [cat[0] for cat in categories if cat[0]]

    def get_statistics(self, db: Session) -> Dict:
        """Get workflow template statistics"""
        total = db.query(func.count(self.model.id)).scalar()

        active = db.query(func.count(self.model.id)).filter(self.model.is_active == True).scalar()

        inactive = (
            db.query(func.count(self.model.id)).filter(self.model.is_active == False).scalar()
        )

        categories = len(self.get_categories(db))

        return {
            "total": total or 0,
            "active": active or 0,
            "inactive": inactive or 0,
            "categories": categories,
        }


template_service = TemplateService(WorkflowTemplate)
