from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.fleet import AssignmentStatus, CourierVehicleAssignment
from app.schemas.fleet import AssignmentCreate, AssignmentUpdate
from app.services.base import CRUDBase


class AssignmentService(CRUDBase[CourierVehicleAssignment, AssignmentCreate, AssignmentUpdate]):
    """Service for CourierVehicleAssignment operations"""

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[CourierVehicleAssignment]:
        """
        Get multiple assignments with eager loading of courier and vehicle relationships
        """
        query = db.query(self.model).options(
            joinedload(CourierVehicleAssignment.courier),
            joinedload(CourierVehicleAssignment.vehicle)
        )

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.filter(getattr(self.model, field) == value)

        # Apply ordering
        if order_by:
            if order_by.startswith("-"):
                query = query.order_by(getattr(self.model, order_by[1:]).desc())
            else:
                query = query.order_by(getattr(self.model, order_by))
        else:
            # Default order by created_at descending
            if hasattr(self.model, "created_at"):
                query = query.order_by(self.model.created_at.desc())

        return query.offset(skip).limit(limit).all()

    def get_active_for_courier(
        self, db: Session, courier_id: int
    ) -> Optional[CourierVehicleAssignment]:
        """Get active assignment for a courier"""
        return (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.courier_id == courier_id)
            .filter(CourierVehicleAssignment.status == AssignmentStatus.ACTIVE)
            .first()
        )

    def get_active_for_vehicle(
        self, db: Session, vehicle_id: int
    ) -> Optional[CourierVehicleAssignment]:
        """Get active assignment for a vehicle"""
        return (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.vehicle_id == vehicle_id)
            .filter(CourierVehicleAssignment.status == AssignmentStatus.ACTIVE)
            .first()
        )

    def get_history_for_courier(
        self, db: Session, courier_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[CourierVehicleAssignment]:
        """Get assignment history for a courier"""
        return (
            db.query(CourierVehicleAssignment)
            .filter(CourierVehicleAssignment.courier_id == courier_id)
            .order_by(CourierVehicleAssignment.start_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_history_for_vehicle(
        self, db: Session, vehicle_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[CourierVehicleAssignment]:
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
