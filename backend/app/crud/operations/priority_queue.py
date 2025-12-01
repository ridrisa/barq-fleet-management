from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.crud.base import CRUDBase
from app.models.operations.priority_queue import PriorityQueueEntry, QueuePriority, QueueStatus
from app.schemas.operations.priority_queue import PriorityQueueEntryCreate, PriorityQueueEntryUpdate


class CRUDPriorityQueueEntry(CRUDBase[PriorityQueueEntry, PriorityQueueEntryCreate, PriorityQueueEntryUpdate]):
    def create_with_number(self, db: Session, *, obj_in: PriorityQueueEntryCreate) -> PriorityQueueEntry:
        """Create queue entry with auto-generated number and calculated priority"""
        last_entry = db.query(PriorityQueueEntry).order_by(PriorityQueueEntry.id.desc()).first()
        next_number = 1 if not last_entry else last_entry.id + 1
        queue_number = f"PQ-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        # Calculate total priority score
        obj_in_data = obj_in.model_dump()
        total_score = (
            obj_in_data.get('base_priority_score', 0) +
            obj_in_data.get('time_factor_score', 0) +
            obj_in_data.get('customer_tier_score', 0) +
            obj_in_data.get('sla_factor_score', 0)
        )
        obj_in_data['total_priority_score'] = total_score

        # Calculate warning threshold
        if obj_in_data.get('sla_deadline'):
            from datetime import timedelta
            buffer_minutes = obj_in_data.get('sla_buffer_minutes', 30)
            obj_in_data['warning_threshold'] = (
                obj_in_data['sla_deadline'] - timedelta(minutes=buffer_minutes)
            )

        db_obj = PriorityQueueEntry(
            **obj_in_data,
            queue_number=queue_number,
            queued_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # Update queue positions
        self._recalculate_queue_positions(db)

        return db_obj

    def get_by_number(self, db: Session, *, queue_number: str) -> Optional[PriorityQueueEntry]:
        """Get queue entry by number"""
        return db.query(PriorityQueueEntry).filter(
            PriorityQueueEntry.queue_number == queue_number
        ).first()

    def get_by_delivery(self, db: Session, *, delivery_id: int) -> Optional[PriorityQueueEntry]:
        """Get queue entry for delivery"""
        return db.query(PriorityQueueEntry).filter(
            PriorityQueueEntry.delivery_id == delivery_id
        ).first()

    def get_queued(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[PriorityQueueEntry]:
        """Get all queued entries ordered by priority"""
        return (
            db.query(PriorityQueueEntry)
            .filter(PriorityQueueEntry.status == QueueStatus.QUEUED)
            .order_by(
                PriorityQueueEntry.total_priority_score.desc(),
                PriorityQueueEntry.queued_at.asc()
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_priority(
        self, db: Session, *, priority: QueuePriority, skip: int = 0, limit: int = 100
    ) -> List[PriorityQueueEntry]:
        """Get entries by priority level"""
        return (
            db.query(PriorityQueueEntry)
            .filter(
                PriorityQueueEntry.priority == priority,
                PriorityQueueEntry.status == QueueStatus.QUEUED
            )
            .order_by(PriorityQueueEntry.total_priority_score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_urgent(self, db: Session) -> List[PriorityQueueEntry]:
        """Get urgent and critical entries"""
        return (
            db.query(PriorityQueueEntry)
            .filter(
                PriorityQueueEntry.status == QueueStatus.QUEUED,
                PriorityQueueEntry.priority.in_([QueuePriority.CRITICAL, QueuePriority.URGENT])
            )
            .order_by(PriorityQueueEntry.total_priority_score.desc())
            .all()
        )

    def get_at_risk(self, db: Session) -> List[PriorityQueueEntry]:
        """Get entries at risk of SLA breach"""
        now = datetime.utcnow()
        return (
            db.query(PriorityQueueEntry)
            .filter(
                PriorityQueueEntry.status == QueueStatus.QUEUED,
                PriorityQueueEntry.warning_threshold <= now
            )
            .order_by(PriorityQueueEntry.sla_deadline.asc())
            .all()
        )

    def get_by_zone(
        self, db: Session, *, zone_id: int, skip: int = 0, limit: int = 100
    ) -> List[PriorityQueueEntry]:
        """Get queued entries for a zone"""
        return (
            db.query(PriorityQueueEntry)
            .filter(
                PriorityQueueEntry.required_zone_id == zone_id,
                PriorityQueueEntry.status == QueueStatus.QUEUED
            )
            .order_by(PriorityQueueEntry.total_priority_score.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_escalated(self, db: Session) -> List[PriorityQueueEntry]:
        """Get escalated entries"""
        return (
            db.query(PriorityQueueEntry)
            .filter(PriorityQueueEntry.is_escalated == True)
            .order_by(PriorityQueueEntry.escalated_at.desc())
            .all()
        )

    def mark_as_processing(self, db: Session, *, entry_id: int) -> Optional[PriorityQueueEntry]:
        """Mark entry as being processed"""
        entry = self.get(db, id=entry_id)
        if entry and entry.status == QueueStatus.QUEUED:
            entry.status = QueueStatus.PROCESSING
            entry.processing_started_at = datetime.utcnow()
            db.add(entry)
            db.commit()
            db.refresh(entry)
            self._recalculate_queue_positions(db)
        return entry

    def mark_as_assigned(self, db: Session, *, entry_id: int) -> Optional[PriorityQueueEntry]:
        """Mark entry as assigned to courier"""
        entry = self.get(db, id=entry_id)
        if entry and entry.status in [QueueStatus.QUEUED, QueueStatus.PROCESSING]:
            entry.status = QueueStatus.ASSIGNED
            entry.assigned_at = datetime.utcnow()
            # Calculate time in queue
            if entry.queued_at:
                duration = (entry.assigned_at - entry.queued_at).total_seconds() / 60
                entry.time_in_queue_minutes = int(duration)
            db.add(entry)
            db.commit()
            db.refresh(entry)
            self._recalculate_queue_positions(db)
        return entry

    def mark_as_completed(
        self, db: Session, *, entry_id: int, sla_met: bool
    ) -> Optional[PriorityQueueEntry]:
        """Mark entry as completed"""
        entry = self.get(db, id=entry_id)
        if entry:
            entry.status = QueueStatus.COMPLETED
            entry.completed_at = datetime.utcnow()
            entry.was_sla_met = sla_met
            # Calculate SLA breach if applicable
            if not sla_met and entry.sla_deadline:
                breach_duration = (entry.completed_at - entry.sla_deadline).total_seconds() / 60
                entry.sla_breach_minutes = int(breach_duration)
            db.add(entry)
            db.commit()
            db.refresh(entry)
            self._recalculate_queue_positions(db)
        return entry

    def mark_as_expired(self, db: Session, *, entry_id: int) -> Optional[PriorityQueueEntry]:
        """Mark entry as expired (missed SLA deadline while in queue)"""
        entry = self.get(db, id=entry_id)
        if entry and entry.status == QueueStatus.QUEUED:
            entry.status = QueueStatus.EXPIRED
            entry.expired_at = datetime.utcnow()
            entry.was_sla_met = False
            if entry.sla_deadline:
                breach_duration = (entry.expired_at - entry.sla_deadline).total_seconds() / 60
                entry.sla_breach_minutes = int(breach_duration)
            db.add(entry)
            db.commit()
            db.refresh(entry)
            self._recalculate_queue_positions(db)
        return entry

    def escalate(
        self, db: Session, *, entry_id: int, reason: str, escalated_to_id: int
    ) -> Optional[PriorityQueueEntry]:
        """Escalate queue entry"""
        entry = self.get(db, id=entry_id)
        if entry:
            entry.is_escalated = True
            entry.escalation_reason = reason
            entry.escalated_to_id = escalated_to_id
            entry.escalated_at = datetime.utcnow()
            db.add(entry)
            db.commit()
            db.refresh(entry)
        return entry

    def increment_assignment_attempt(self, db: Session, *, entry_id: int) -> Optional[PriorityQueueEntry]:
        """Increment assignment attempt counter"""
        entry = self.get(db, id=entry_id)
        if entry:
            entry.assignment_attempts += 1
            db.add(entry)
            db.commit()
            db.refresh(entry)
        return entry

    def _recalculate_queue_positions(self, db: Session):
        """Recalculate queue positions for all queued entries"""
        queued_entries = (
            db.query(PriorityQueueEntry)
            .filter(PriorityQueueEntry.status == QueueStatus.QUEUED)
            .order_by(
                PriorityQueueEntry.total_priority_score.desc(),
                PriorityQueueEntry.queued_at.asc()
            )
            .all()
        )

        for position, entry in enumerate(queued_entries, start=1):
            entry.queue_position = position
            # Rough estimate of wait time based on position
            entry.estimated_wait_time_minutes = position * 15  # 15 minutes per position

        db.commit()


priority_queue_entry = CRUDPriorityQueueEntry(PriorityQueueEntry)
