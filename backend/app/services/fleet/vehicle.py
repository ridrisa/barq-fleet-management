from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import date, timedelta

from app.models.fleet import Vehicle, VehicleStatus, VehicleType
from app.schemas.fleet import VehicleCreate, VehicleUpdate, VehicleDocumentStatus
from app.services.base import CRUDBase


class VehicleService(CRUDBase[Vehicle, VehicleCreate, VehicleUpdate]):
    """Service for Vehicle operations with business logic"""

    def get_by_plate_number(self, db: Session, plate_number: str) -> Optional[Vehicle]:
        """Get vehicle by plate number"""
        return db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()

    def get_by_vin(self, db: Session, vin_number: str) -> Optional[Vehicle]:
        """Get vehicle by VIN number"""
        return db.query(Vehicle).filter(Vehicle.vin_number == vin_number).first()

    def get_active_vehicles(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        vehicle_type: Optional[VehicleType] = None
    ) -> List[Vehicle]:
        """Get all active vehicles, optionally filtered by type"""
        query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE)

        if vehicle_type:
            query = query.filter(Vehicle.vehicle_type == vehicle_type)

        return query.offset(skip).limit(limit).all()

    def get_by_status(
        self,
        db: Session,
        status: VehicleStatus,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vehicle]:
        """Get vehicles by status"""
        return (
            db.query(Vehicle)
            .filter(Vehicle.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_available_vehicles(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        vehicle_type: Optional[VehicleType] = None
    ) -> List[Vehicle]:
        """Get available vehicles (active and not assigned)"""
        query = db.query(Vehicle).filter(
            Vehicle.status == VehicleStatus.ACTIVE
        ).filter(
            ~Vehicle.assigned_couriers.any()
        )

        if vehicle_type:
            query = query.filter(Vehicle.vehicle_type == vehicle_type)

        return query.offset(skip).limit(limit).all()

    def get_by_city(
        self,
        db: Session,
        city: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vehicle]:
        """Get vehicles assigned to a city"""
        return (
            db.query(Vehicle)
            .filter(Vehicle.assigned_to_city == city)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_due_for_service(
        self,
        db: Session,
        *,
        days_threshold: int = 7,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vehicle]:
        """Get vehicles due for service within threshold days"""
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        return (
            db.query(Vehicle)
            .filter(
                and_(
                    Vehicle.status == VehicleStatus.ACTIVE,
                    Vehicle.next_service_due_date <= threshold_date
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_mileage(
        self,
        db: Session,
        vehicle_id: int,
        new_mileage: float
    ) -> Vehicle:
        """Update vehicle mileage"""
        vehicle = self.get(db, vehicle_id)
        if vehicle and new_mileage > vehicle.current_mileage:
            vehicle.current_mileage = new_mileage
            db.commit()
            db.refresh(vehicle)
        return vehicle

    def update_status(
        self,
        db: Session,
        vehicle_id: int,
        status: VehicleStatus
    ) -> Vehicle:
        """Update vehicle status"""
        vehicle = self.get(db, vehicle_id)
        if vehicle:
            vehicle.status = status
            db.commit()
            db.refresh(vehicle)
        return vehicle

    def record_service(
        self,
        db: Session,
        vehicle_id: int,
        service_date: date,
        service_mileage: float,
        next_service_date: Optional[date] = None,
        next_service_mileage: Optional[float] = None
    ) -> Vehicle:
        """Record service completion and schedule next service"""
        vehicle = self.get(db, vehicle_id)
        if vehicle:
            vehicle.last_service_date = service_date
            vehicle.last_service_mileage = service_mileage

            if next_service_date:
                vehicle.next_service_due_date = next_service_date
            if next_service_mileage:
                vehicle.next_service_due_mileage = next_service_mileage

            db.commit()
            db.refresh(vehicle)
        return vehicle

    def get_expiring_documents(
        self,
        db: Session,
        days_threshold: int = 30
    ) -> List[VehicleDocumentStatus]:
        """
        Get vehicles with documents expiring soon
        Args:
            days_threshold: Days until expiry to consider (default 30)
        """
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        vehicles = db.query(Vehicle).filter(
            and_(
                Vehicle.status.in_([VehicleStatus.ACTIVE, VehicleStatus.MAINTENANCE]),
                or_(
                    Vehicle.registration_expiry_date <= threshold_date,
                    Vehicle.insurance_expiry_date <= threshold_date,
                )
            )
        ).all()

        result = []
        for vehicle in vehicles:
            doc_status = VehicleDocumentStatus(
                vehicle_id=vehicle.id,
                plate_number=vehicle.plate_number,
                registration_expiry_date=vehicle.registration_expiry_date,
                registration_expired=vehicle.registration_expiry_date < today if vehicle.registration_expiry_date else False,
                registration_expires_soon=vehicle.registration_expiry_date <= threshold_date if vehicle.registration_expiry_date else False,
                insurance_expiry_date=vehicle.insurance_expiry_date,
                insurance_expired=vehicle.insurance_expiry_date < today if vehicle.insurance_expiry_date else False,
                insurance_expires_soon=vehicle.insurance_expiry_date <= threshold_date if vehicle.insurance_expiry_date else False,
            )

            doc_status.any_expired = (
                doc_status.registration_expired or
                doc_status.insurance_expired
            )
            doc_status.any_expires_soon = (
                doc_status.registration_expires_soon or
                doc_status.insurance_expires_soon
            )

            result.append(doc_status)

        return result

    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Get overall vehicle statistics"""
        total = db.query(func.count(Vehicle.id)).scalar()

        status_counts = (
            db.query(Vehicle.status, func.count(Vehicle.id))
            .group_by(Vehicle.status)
            .all()
        )

        type_counts = (
            db.query(Vehicle.vehicle_type, func.count(Vehicle.id))
            .group_by(Vehicle.vehicle_type)
            .all()
        )

        assigned = (
            db.query(func.count(Vehicle.id))
            .filter(Vehicle.assigned_couriers.any())
            .scalar()
        )

        available = (
            db.query(func.count(Vehicle.id))
            .filter(Vehicle.status == VehicleStatus.ACTIVE)
            .filter(~Vehicle.assigned_couriers.any())
            .scalar()
        )

        return {
            "total": total,
            "status_breakdown": dict(status_counts),
            "type_breakdown": dict(type_counts),
            "assigned": assigned,
            "available": available,
        }

    def search_vehicles(
        self,
        db: Session,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Vehicle]:
        """Search vehicles by plate, make, model, or VIN"""
        return self.search(
            db,
            search_term=search_term,
            search_fields=["plate_number", "make", "model", "vin_number", "registration_number"],
            skip=skip,
            limit=limit
        )


# Create instance
vehicle_service = VehicleService(Vehicle)
