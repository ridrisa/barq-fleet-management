"""Bed Service"""

from typing import Dict, List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.accommodation.bed import Bed, BedStatus
from app.schemas.accommodation.bed import BedCreate, BedUpdate
from app.services.base import CRUDBase


class BedService(CRUDBase[Bed, BedCreate, BedUpdate]):
    """Service for bed management operations"""

    def get_by_room(
        self, db: Session, *, room_id: int, skip: int = 0, limit: int = 100
    ) -> List[Bed]:
        """
        Get all beds in a room

        Args:
            db: Database session
            room_id: ID of the room
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bed records
        """
        return (
            db.query(self.model)
            .filter(self.model.room_id == room_id)
            .order_by(self.model.bed_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: BedStatus,
        room_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Bed]:
        """
        Get beds by status

        Args:
            db: Database session
            status: Bed status to filter by
            room_id: Optional room ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of bed records
        """
        query = db.query(self.model).filter(self.model.status == status)

        if room_id:
            query = query.filter(self.model.room_id == room_id)

        return query.order_by(self.model.bed_number).offset(skip).limit(limit).all()

    def get_available(
        self, db: Session, *, room_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Bed]:
        """
        Get available beds

        Args:
            db: Database session
            room_id: Optional room ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of available bed records
        """
        query = db.query(self.model).filter(self.model.status == BedStatus.AVAILABLE)

        if room_id:
            query = query.filter(self.model.room_id == room_id)

        return query.order_by(self.model.bed_number).offset(skip).limit(limit).all()

    def get_by_bed_number(self, db: Session, *, room_id: int, bed_number: int) -> Optional[Bed]:
        """
        Get bed by room and bed number

        Args:
            db: Database session
            room_id: Room ID
            bed_number: Bed number

        Returns:
            Bed record or None
        """
        return (
            db.query(self.model)
            .filter(and_(self.model.room_id == room_id, self.model.bed_number == bed_number))
            .first()
        )

    def allocate_bed(self, db: Session, *, bed_id: int) -> Optional[Bed]:
        """
        Mark a bed as occupied

        Args:
            db: Database session
            bed_id: Bed ID

        Returns:
            Updated bed record or None
        """
        bed = self.get(db, id=bed_id)
        if not bed:
            return None

        if bed.status != BedStatus.AVAILABLE:
            return None  # Bed not available

        bed.status = BedStatus.OCCUPIED
        db.commit()
        db.refresh(bed)
        return bed

    def release_bed(self, db: Session, *, bed_id: int) -> Optional[Bed]:
        """
        Mark a bed as available (release)

        Args:
            db: Database session
            bed_id: Bed ID

        Returns:
            Updated bed record or None
        """
        bed = self.get(db, id=bed_id)
        if not bed:
            return None

        bed.status = BedStatus.AVAILABLE
        db.commit()
        db.refresh(bed)
        return bed

    def reserve_bed(self, db: Session, *, bed_id: int) -> Optional[Bed]:
        """
        Mark a bed as reserved

        Args:
            db: Database session
            bed_id: Bed ID

        Returns:
            Updated bed record or None
        """
        bed = self.get(db, id=bed_id)
        if not bed:
            return None

        if bed.status != BedStatus.AVAILABLE:
            return None  # Can only reserve available beds

        bed.status = BedStatus.RESERVED
        db.commit()
        db.refresh(bed)
        return bed

    def get_statistics(self, db: Session, *, room_id: Optional[int] = None) -> Dict:
        """
        Get bed statistics

        Args:
            db: Database session
            room_id: Optional room ID to filter by

        Returns:
            Dictionary with bed statistics
        """
        query = db.query(self.model)

        if room_id:
            query = query.filter(self.model.room_id == room_id)

        beds = query.all()

        available_count = sum(1 for b in beds if b.status == BedStatus.AVAILABLE)
        occupied_count = sum(1 for b in beds if b.status == BedStatus.OCCUPIED)
        reserved_count = sum(1 for b in beds if b.status == BedStatus.RESERVED)

        return {
            "total_beds": len(beds),
            "available": available_count,
            "occupied": occupied_count,
            "reserved": reserved_count,
            "availability_rate": (available_count / len(beds) * 100) if len(beds) > 0 else 0,
        }


bed_service = BedService(Bed)
