"""Allocation Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import date

from app.services.base import CRUDBase
from app.models.accommodation.allocation import Allocation
from app.schemas.accommodation.allocation import AllocationCreate, AllocationUpdate


class AllocationService(CRUDBase[Allocation, AllocationCreate, AllocationUpdate]):
    """Service for bed allocation management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Allocation]:
        """
        Get all allocations for a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of allocation records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.allocation_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_bed(
        self,
        db: Session,
        *,
        bed_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Allocation]:
        """
        Get all allocations for a bed

        Args:
            db: Database session
            bed_id: ID of the bed
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of allocation records
        """
        return (
            db.query(self.model)
            .filter(self.model.bed_id == bed_id)
            .order_by(self.model.allocation_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        bed_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Allocation]:
        """
        Get active allocations (not yet released)

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            bed_id: Optional bed ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active allocation records
        """
        query = db.query(self.model).filter(self.model.release_date.is_(None))

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        if bed_id:
            query = query.filter(self.model.bed_id == bed_id)

        return (
            query.order_by(self.model.allocation_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_by_courier(
        self,
        db: Session,
        *,
        courier_id: int
    ) -> Optional[Allocation]:
        """
        Get current active allocation for a courier

        Args:
            db: Database session
            courier_id: ID of the courier

        Returns:
            Active allocation record or None
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.courier_id == courier_id,
                    self.model.release_date.is_(None)
                )
            )
            .order_by(self.model.allocation_date.desc())
            .first()
        )

    def get_active_by_bed(
        self,
        db: Session,
        *,
        bed_id: int
    ) -> Optional[Allocation]:
        """
        Get current active allocation for a bed

        Args:
            db: Database session
            bed_id: ID of the bed

        Returns:
            Active allocation record or None
        """
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.bed_id == bed_id,
                    self.model.release_date.is_(None)
                )
            )
            .order_by(self.model.allocation_date.desc())
            .first()
        )

    def allocate_bed(
        self,
        db: Session,
        *,
        allocation_data: AllocationCreate
    ) -> Optional[Allocation]:
        """
        Create a new bed allocation

        Args:
            db: Database session
            allocation_data: Allocation creation data

        Returns:
            Created allocation record or None if bed is not available
        """
        from app.services.accommodation import bed_service

        # Check if bed is available
        bed = bed_service.get(db, id=allocation_data.bed_id)
        if not bed or bed.status != "available":
            return None

        # Check if courier already has an active allocation
        existing = self.get_active_by_courier(db, courier_id=allocation_data.courier_id)
        if existing:
            return None  # Courier already has an active allocation

        # Create allocation
        allocation = self.create(db, obj_in=allocation_data)

        # Update bed status to occupied
        bed_service.allocate_bed(db, bed_id=allocation_data.bed_id)

        return allocation

    def release_allocation(
        self,
        db: Session,
        *,
        allocation_id: int,
        release_date: Optional[date] = None
    ) -> Optional[Allocation]:
        """
        Release a bed allocation

        Args:
            db: Database session
            allocation_id: Allocation ID
            release_date: Date of release (defaults to today)

        Returns:
            Updated allocation record or None
        """
        from app.services.accommodation import bed_service

        allocation = self.get(db, id=allocation_id)
        if not allocation:
            return None

        # Set release date
        allocation.release_date = release_date or date.today()
        db.commit()
        db.refresh(allocation)

        # Update bed status to available
        bed_service.release_bed(db, bed_id=allocation.bed_id)

        return allocation

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None
    ) -> Dict:
        """
        Get allocation statistics

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by

        Returns:
            Dictionary with allocation statistics
        """
        query = db.query(self.model)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        allocations = query.all()

        active_count = sum(1 for a in allocations if a.release_date is None)
        completed_count = sum(1 for a in allocations if a.release_date is not None)

        # Calculate average stay duration for completed allocations
        completed_allocations = [a for a in allocations if a.release_date]
        if completed_allocations:
            total_days = sum(
                (a.release_date - a.allocation_date).days
                for a in completed_allocations
            )
            avg_stay_duration = total_days / len(completed_allocations)
        else:
            avg_stay_duration = 0

        return {
            "total_allocations": len(allocations),
            "active_allocations": active_count,
            "completed_allocations": completed_count,
            "average_stay_duration_days": round(avg_stay_duration, 2)
        }


allocation_service = AllocationService(Allocation)
