from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.operations.zone import Zone, ZoneStatus
from app.schemas.operations.zone import ZoneCreate, ZoneUpdate


class CRUDZone(CRUDBase[Zone, ZoneCreate, ZoneUpdate]):
    def get_by_code(self, db: Session, *, zone_code: str) -> Optional[Zone]:
        """Get zone by unique code"""
        return db.query(Zone).filter(Zone.zone_code == zone_code).first()

    def get_active_zones(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Zone]:
        """Get all active zones"""
        return (
            db.query(Zone)
            .filter(Zone.status == ZoneStatus.ACTIVE)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_city(self, db: Session, *, city: str, skip: int = 0, limit: int = 100) -> List[Zone]:
        """Get zones by city"""
        return (
            db.query(Zone)
            .filter(Zone.city == city)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_at_capacity(self, db: Session) -> List[Zone]:
        """Get zones at or near capacity"""
        return (
            db.query(Zone)
            .filter(
                Zone.status == ZoneStatus.ACTIVE,
                Zone.current_couriers >= Zone.max_couriers
            )
            .all()
        )

    def increment_courier_count(self, db: Session, *, zone_id: int) -> Optional[Zone]:
        """Increment current courier count"""
        zone = self.get(db, id=zone_id)
        if zone:
            zone.current_couriers += 1
            db.add(zone)
            db.commit()
            db.refresh(zone)
        return zone

    def decrement_courier_count(self, db: Session, *, zone_id: int) -> Optional[Zone]:
        """Decrement current courier count"""
        zone = self.get(db, id=zone_id)
        if zone and zone.current_couriers > 0:
            zone.current_couriers -= 1
            db.add(zone)
            db.commit()
            db.refresh(zone)
        return zone

    def update_performance_metrics(
        self, db: Session, *, zone_id: int,
        avg_delivery_time: float,
        total_deliveries: int,
        success_rate: float
    ) -> Optional[Zone]:
        """Update zone performance metrics"""
        zone = self.get(db, id=zone_id)
        if zone:
            zone.avg_delivery_time_minutes = avg_delivery_time
            zone.total_deliveries_completed = total_deliveries
            zone.success_rate = success_rate
            db.add(zone)
            db.commit()
            db.refresh(zone)
        return zone


zone = CRUDZone(Zone)
