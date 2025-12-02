"""Canned Response Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.base import CRUDBase
from app.models.support import CannedResponse
from app.schemas.support import CannedResponseCreate, CannedResponseUpdate


class CannedResponseService(CRUDBase[CannedResponse, CannedResponseCreate, CannedResponseUpdate]):
    """Service for canned response management"""

    def create_response(
        self, db: Session, *, obj_in: CannedResponseCreate, created_by: int
    ) -> CannedResponse:
        """Create a new canned response"""
        obj_in_data = obj_in.model_dump()
        obj_in_data['created_by'] = created_by

        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_shortcut(self, db: Session, *, shortcut: str) -> Optional[CannedResponse]:
        """Get canned response by shortcut"""
        return db.query(self.model).filter(self.model.shortcut == shortcut).first()

    def get_by_title(self, db: Session, *, title: str) -> Optional[CannedResponse]:
        """Get canned response by title"""
        return db.query(self.model).filter(self.model.title == title).first()

    def get_active_responses(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CannedResponse]:
        """Get all active canned responses"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.category, self.model.title)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_public_responses(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[CannedResponse]:
        """Get all public and active canned responses"""
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                self.model.is_public == True
            )
            .order_by(self.model.category, self.model.title)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category(
        self, db: Session, *, category: str, skip: int = 0, limit: int = 100
    ) -> List[CannedResponse]:
        """Get canned responses by category"""
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                self.model.category == category
            )
            .order_by(self.model.title)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_categories(self, db: Session) -> Dict[str, int]:
        """Get list of categories with counts"""
        result = (
            db.query(
                self.model.category,
                func.count(self.model.id).label('count')
            )
            .filter(self.model.is_active == True)
            .group_by(self.model.category)
            .all()
        )
        return {category: count for category, count in result}

    def search_responses(
        self, db: Session, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[CannedResponse]:
        """Search canned responses by title or content"""
        return (
            db.query(self.model)
            .filter(
                self.model.is_active == True,
                (
                    self.model.title.ilike(f"%{query}%") |
                    self.model.content.ilike(f"%{query}%") |
                    self.model.shortcut.ilike(f"%{query}%")
                )
            )
            .order_by(self.model.usage_count.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def increment_usage(self, db: Session, *, response_id: int) -> Optional[CannedResponse]:
        """Increment usage count for a canned response"""
        response = self.get(db, id=response_id)
        if not response:
            return None

        response.usage_count += 1
        db.commit()
        db.refresh(response)
        return response

    def get_rendered_content(
        self, db: Session, *, response_id: int, variables: Dict[str, str]
    ) -> Optional[str]:
        """Get canned response content with variables replaced"""
        response = self.get(db, id=response_id)
        if not response:
            return None

        content = response.content
        for key, value in variables.items():
            content = content.replace(f"{{{key}}}", value)

        # Increment usage
        response.usage_count += 1
        db.commit()

        return content

    def get_top_used(
        self, db: Session, *, limit: int = 10
    ) -> List[CannedResponse]:
        """Get most used canned responses"""
        return (
            db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.usage_count.desc())
            .limit(limit)
            .all()
        )

    def activate_response(self, db: Session, *, response_id: int) -> Optional[CannedResponse]:
        """Activate a canned response"""
        response = self.get(db, id=response_id)
        if not response:
            return None

        response.is_active = True
        db.commit()
        db.refresh(response)
        return response

    def deactivate_response(self, db: Session, *, response_id: int) -> Optional[CannedResponse]:
        """Deactivate a canned response"""
        response = self.get(db, id=response_id)
        if not response:
            return None

        response.is_active = False
        db.commit()
        db.refresh(response)
        return response


canned_response_service = CannedResponseService(CannedResponse)
