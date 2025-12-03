"""Building Service"""

from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.accommodation.building import Building
from app.schemas.accommodation.building import BuildingCreate, BuildingUpdate
from app.services.base import CRUDBase


class BuildingService(CRUDBase[Building, BuildingCreate, BuildingUpdate]):
    """Service for building management operations"""

    def get_by_location(
        self, db: Session, *, location_search: str, skip: int = 0, limit: int = 100
    ) -> List[Building]:
        """
        Search buildings by address/location

        Args:
            db: Database session
            location_search: Search term for address
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of building records matching the search
        """
        return (
            db.query(self.model)
            .filter(self.model.address.ilike(f"%{location_search}%"))
            .order_by(self.model.name)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_name(self, db: Session, *, name: str) -> Optional[Building]:
        """
        Get building by exact name

        Args:
            db: Database session
            name: Building name

        Returns:
            Building record or None
        """
        return db.query(self.model).filter(self.model.name == name).first()

    def search_buildings(
        self, db: Session, *, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Building]:
        """
        Search buildings by name or address

        Args:
            db: Database session
            search_term: Search term
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of building records
        """
        return self.search(
            db, search_term=search_term, search_fields=["name", "address"], skip=skip, limit=limit
        )

    def get_statistics(self, db: Session, *, building_id: Optional[int] = None) -> Dict:
        """
        Get building statistics

        Args:
            db: Database session
            building_id: Optional building ID to filter by

        Returns:
            Dictionary with building statistics
        """
        query = db.query(self.model)

        if building_id:
            query = query.filter(self.model.id == building_id)

        buildings = query.all()

        if building_id and buildings:
            # Single building statistics
            building = buildings[0]
            return {
                "building_id": building.id,
                "building_name": building.name,
                "total_rooms": building.total_rooms,
                "total_capacity": building.total_capacity,
                "address": building.address,
            }

        # All buildings statistics
        total_buildings = len(buildings)
        total_rooms = sum(b.total_rooms for b in buildings)
        total_capacity = sum(b.total_capacity for b in buildings)

        return {
            "total_buildings": total_buildings,
            "total_rooms": total_rooms,
            "total_capacity": total_capacity,
            "average_capacity_per_building": (
                total_capacity / total_buildings if total_buildings > 0 else 0
            ),
        }

    def update_building_stats(self, db: Session, *, building_id: int) -> Optional[Building]:
        """
        Recalculate and update building statistics (total_rooms, total_capacity)

        Args:
            db: Database session
            building_id: Building ID

        Returns:
            Updated building record or None
        """
        from app.models.accommodation.room import Room

        building = self.get(db, id=building_id)
        if not building:
            return None

        # Count total rooms
        total_rooms = db.query(func.count(Room.id)).filter(Room.building_id == building_id).scalar()

        # Sum total capacity
        total_capacity = (
            db.query(func.sum(Room.capacity)).filter(Room.building_id == building_id).scalar() or 0
        )

        building.total_rooms = total_rooms
        building.total_capacity = total_capacity

        db.commit()
        db.refresh(building)
        return building


building_service = BuildingService(Building)
