"""Workflow Instance Service"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.services.base import CRUDBase
from app.models.workflow.instance import WorkflowInstance, WorkflowStatus
from app.schemas.workflow import WorkflowInstanceCreate, WorkflowInstanceUpdate


class InstanceService(CRUDBase[WorkflowInstance, WorkflowInstanceCreate, WorkflowInstanceUpdate]):
    """Service for workflow instance management operations"""

    def get_by_template(
        self, db: Session, *, template_id: int, skip: int = 0, limit: int = 100
    ) -> List[WorkflowInstance]:
        """Get all workflow instances for a template"""
        return (
            db.query(self.model)
            .filter(self.model.template_id == template_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, db: Session, *, status: WorkflowStatus, skip: int = 0, limit: int = 100
    ) -> List[WorkflowInstance]:
        """Get workflow instances by status"""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_initiator(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[WorkflowInstance]:
        """Get workflow instances initiated by a user"""
        return (
            db.query(self.model)
            .filter(self.model.initiated_by == user_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def start_workflow(
        self, db: Session, *, instance_id: int
    ) -> Optional[WorkflowInstance]:
        """Start a workflow instance"""
        instance = db.query(self.model).filter(self.model.id == instance_id).first()
        if not instance:
            return None

        instance.status = WorkflowStatus.IN_PROGRESS
        instance.started_at = date.today()
        instance.current_step = 1

        db.commit()
        db.refresh(instance)
        return instance

    def complete_step(
        self,
        db: Session,
        *,
        instance_id: int,
        step_data: Optional[Dict[str, Any]] = None
    ) -> Optional[WorkflowInstance]:
        """Complete current step and move to next"""
        instance = db.query(self.model).filter(self.model.id == instance_id).first()
        if not instance:
            return None

        # Update instance data with step data if provided
        if step_data:
            current_data = instance.data or {}
            current_data[f"step_{instance.current_step}"] = step_data
            instance.data = current_data

        # Move to next step
        instance.current_step += 1

        db.commit()
        db.refresh(instance)
        return instance

    def complete_workflow(
        self, db: Session, *, instance_id: int, notes: Optional[str] = None
    ) -> Optional[WorkflowInstance]:
        """Complete a workflow instance"""
        instance = db.query(self.model).filter(self.model.id == instance_id).first()
        if not instance:
            return None

        instance.status = WorkflowStatus.COMPLETED
        instance.completed_at = date.today()
        if notes:
            instance.notes = notes

        db.commit()
        db.refresh(instance)
        return instance

    def cancel_workflow(
        self, db: Session, *, instance_id: int, reason: Optional[str] = None
    ) -> Optional[WorkflowInstance]:
        """Cancel a workflow instance"""
        instance = db.query(self.model).filter(self.model.id == instance_id).first()
        if not instance:
            return None

        instance.status = WorkflowStatus.CANCELLED
        if reason:
            instance.notes = reason

        db.commit()
        db.refresh(instance)
        return instance

    def approve_workflow(
        self, db: Session, *, instance_id: int, notes: Optional[str] = None
    ) -> Optional[WorkflowInstance]:
        """Approve a workflow instance"""
        instance = db.query(self.model).filter(self.model.id == instance_id).first()
        if not instance:
            return None

        instance.status = WorkflowStatus.APPROVED
        if notes:
            instance.notes = notes

        db.commit()
        db.refresh(instance)
        return instance

    def reject_workflow(
        self, db: Session, *, instance_id: int, reason: Optional[str] = None
    ) -> Optional[WorkflowInstance]:
        """Reject a workflow instance"""
        instance = db.query(self.model).filter(self.model.id == instance_id).first()
        if not instance:
            return None

        instance.status = WorkflowStatus.REJECTED
        if reason:
            instance.notes = reason

        db.commit()
        db.refresh(instance)
        return instance

    def submit_for_approval(
        self, db: Session, *, instance_id: int
    ) -> Optional[WorkflowInstance]:
        """Submit workflow instance for approval"""
        instance = db.query(self.model).filter(self.model.id == instance_id).first()
        if not instance:
            return None

        instance.status = WorkflowStatus.PENDING_APPROVAL

        db.commit()
        db.refresh(instance)
        return instance

    def get_statistics(self, db: Session) -> Dict:
        """Get workflow instance statistics"""
        total = db.query(func.count(self.model.id)).scalar()

        draft = db.query(func.count(self.model.id)).filter(
            self.model.status == WorkflowStatus.DRAFT
        ).scalar()

        in_progress = db.query(func.count(self.model.id)).filter(
            self.model.status == WorkflowStatus.IN_PROGRESS
        ).scalar()

        pending_approval = db.query(func.count(self.model.id)).filter(
            self.model.status == WorkflowStatus.PENDING_APPROVAL
        ).scalar()

        approved = db.query(func.count(self.model.id)).filter(
            self.model.status == WorkflowStatus.APPROVED
        ).scalar()

        completed = db.query(func.count(self.model.id)).filter(
            self.model.status == WorkflowStatus.COMPLETED
        ).scalar()

        rejected = db.query(func.count(self.model.id)).filter(
            self.model.status == WorkflowStatus.REJECTED
        ).scalar()

        cancelled = db.query(func.count(self.model.id)).filter(
            self.model.status == WorkflowStatus.CANCELLED
        ).scalar()

        return {
            "total": total or 0,
            "draft": draft or 0,
            "in_progress": in_progress or 0,
            "pending_approval": pending_approval or 0,
            "approved": approved or 0,
            "completed": completed or 0,
            "rejected": rejected or 0,
            "cancelled": cancelled or 0
        }


instance_service = InstanceService(WorkflowInstance)
