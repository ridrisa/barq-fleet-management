"""Room Service"""

from typing import Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.accommodation.room import Room, RoomStatus
from app.schemas.accommodation.room import RoomCreate, RoomUpdate
from app.services.base import CRUDBase


class RoomService(CRUDBase[Room, RoomCreate, RoomUpdate]):
    """Service for room management operations"""

    def get_by_building(
        self, db: Session, *, building_id: int, skip: int = 0, limit: int = 100
    ) -> List[Room]:
        """
        Get all rooms in a building

        Args:
            db: Database session
            building_id: ID of the building
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of room records
        """
        return (
            db.query(self.model)
            .filter(self.model.building_id == building_id)
            .order_by(self.model.room_number)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: RoomStatus,
        building_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Room]:
        """
        Get rooms by status

        Args:
            db: Database session
            status: Room status to filter by
            building_id: Optional building ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of room records
        """
        query = db.query(self.model).filter(self.model.status == status)

        if building_id:
            query = query.filter(self.model.building_id == building_id)

        return query.order_by(self.model.room_number).offset(skip).limit(limit).all()

    def get_available(
        self, db: Session, *, building_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Room]:
        """
        Get available rooms (status = available and has free beds)

        Args:
            db: Database session
            building_id: Optional building ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of available room records
        """
        query = db.query(self.model).filter(
            and_(
                self.model.status == RoomStatus.AVAILABLE, self.model.occupied < self.model.capacity
            )
        )

        if building_id:
            query = query.filter(self.model.building_id == building_id)

        return query.order_by(self.model.room_number).offset(skip).limit(limit).all()

    def get_by_room_number(
        self, db: Session, *, building_id: int, room_number: str
    ) -> Optional[Room]:
        """
        Get room by building and room number

        Args:
            db: Database session
            building_id: Building ID
            room_number: Room number

        Returns:
            Room record or None
        """
        return (
            db.query(self.model)
            .filter(
                and_(self.model.building_id == building_id, self.model.room_number == room_number)
            )
            .first()
        )

    def update_occupancy(self, db: Session, *, room_id: int) -> Optional[Room]:
        """
        Recalculate and update room occupancy based on bed allocations

        Args:
            db: Database session
            room_id: Room ID

        Returns:
            Updated room record or None
        """
        from app.models.accommodation.bed import Bed, BedStatus

        room = self.get(db, id=room_id)
        if not room:
            return None

        # Count occupied beds
        occupied_count = (
            db.query(func.count(Bed.id))
            .filter(and_(Bed.room_id == room_id, Bed.status == BedStatus.OCCUPIED))
            .scalar()
        )

        room.occupied = occupied_count

        # Update room status based on occupancy
        if occupied_count == 0:
            room.status = RoomStatus.AVAILABLE
        elif occupied_count >= room.capacity:
            room.status = RoomStatus.OCCUPIED
        else:
            room.status = RoomStatus.AVAILABLE

        db.commit()
        db.refresh(room)
        return room

    def get_statistics(self, db: Session, *, building_id: Optional[int] = None) -> Dict:
        """
        Get room statistics

        Args:
            db: Database session
            building_id: Optional building ID to filter by

        Returns:
            Dictionary with room statistics
        """
        query = db.query(self.model)

        if building_id:
            query = query.filter(self.model.building_id == building_id)

        rooms = query.all()

        available_rooms = sum(
            1 for r in rooms if r.status == RoomStatus.AVAILABLE and r.occupied < r.capacity
        )
        occupied_rooms = sum(
            1 for r in rooms if r.status == RoomStatus.OCCUPIED or r.occupied >= r.capacity
        )
        maintenance_rooms = sum(1 for r in rooms if r.status == RoomStatus.MAINTENANCE)

        total_capacity = sum(r.capacity for r in rooms)
        total_occupied = sum(r.occupied for r in rooms)

        return {
            "total_rooms": len(rooms),
            "available_rooms": available_rooms,
            "occupied_rooms": occupied_rooms,
            "maintenance_rooms": maintenance_rooms,
            "total_capacity": total_capacity,
            "total_occupied": total_occupied,
            "occupancy_rate": (total_occupied / total_capacity * 100) if total_capacity > 0 else 0,
        }


room_service = RoomService(Room)
