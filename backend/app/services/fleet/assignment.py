from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.fleet import CourierVehicleAssignment, AssignmentStatus
from app.schemas.fleet import AssignmentCreate, AssignmentUpdate
from app.services.base import CRUDBase


class AssignmentService(CRUDBase[CourierVehicleAssignment, AssignmentCreate, AssignmentUpdate]):
    """Service for CourierVehicleAssignment operations"""

    def get_active_for_courier(self, db: Session, courier_id: int) -> Optional[CourierVehicleAssignment]:
        """Get active assignment for a courier"""
        return (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.courier_id == courier_id)
            .filter(CourierVehicleAssignment.status == AssignmentStatus.ACTIVE)
            .first()
        )

    def get_active_for_vehicle(self, db: Session, vehicle_id: int) -> Optional[CourierVehicleAssignment]:
        """Get active assignment for a vehicle"""
        return (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.vehicle_id == vehicle_id)
            .filter(CourierVehicleAssignment.status == AssignmentStatus.ACTIVE)
            .first()
        )

    def get_history_for_courier(self, db: Session, courier_id: int, *, skip: int = 0, limit: int = 100) -> List[CourierVehicleAssignment]:
        """Get assignment history for a courier"""
        return (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.courier_id == courier_id)
            .order_by(CourierVehicleAssignment.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_history_for_vehicle(self, db: Session, vehicle_id: int, *, skip: int = 0, limit: int = 100) -> List[CourierVehicleAssignment]:
        """Get assignment history for a vehicle"""
        return (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.vehicle_id == vehicle_id)
            .order_by(CourierVehicleAssignment.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


assignment_service = AssignmentService(CourierVehicleAssignment)
