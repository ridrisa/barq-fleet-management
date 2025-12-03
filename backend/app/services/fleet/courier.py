from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.models.fleet import Courier, CourierStatus
from app.schemas.fleet import CourierCreate, CourierDocumentStatus, CourierUpdate
from app.services.base import CRUDBase


class CourierService(CRUDBase[Courier, CourierCreate, CourierUpdate]):
    """Service for Courier operations with business logic"""

    def get_by_barq_id(self, db: Session, barq_id: str) -> Optional[Courier]:
        """Get courier by BARQ ID"""
        return db.query(Courier).filter(Courier.barq_id == barq_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[Courier]:
        """Get courier by email"""
        return db.query(Courier).filter(Courier.email == email).first()

    def get_by_employee_id(self, db: Session, employee_id: str) -> Optional[Courier]:
        """Get courier by employee ID"""
        return db.query(Courier).filter(Courier.employee_id == employee_id).first()

    def get_active_couriers(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        city: Optional[str] = None,
        organization_id: Optional[int] = None,
    ) -> List[Courier]:
        """Get all active couriers, optionally filtered by city"""
        query = db.query(Courier).filter(Courier.status == CourierStatus.ACTIVE)

        if organization_id:
            query = query.filter(Courier.organization_id == organization_id)

        if city:
            query = query.filter(Courier.city == city)

        return query.offset(skip).limit(limit).all()

    def get_by_status(
        self,
        db: Session,
        status: CourierStatus,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Courier]:
        """Get couriers by status"""
        query = db.query(Courier).filter(Courier.status == status)

        if organization_id:
            query = query.filter(Courier.organization_id == organization_id)

        return query.offset(skip).limit(limit).all()

    def get_without_vehicle(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[Courier]:
        """Get couriers without assigned vehicle"""
        query = (
            db.query(Courier)
            .filter(Courier.current_vehicle_id == None)
            .filter(Courier.status == CourierStatus.ACTIVE)
        )

        if organization_id:
            query = query.filter(Courier.organization_id == organization_id)

        return query.offset(skip).limit(limit).all()

    def get_by_city(
        self,
        db: Session,
        city: str,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Courier]:
        """Get couriers by city"""
        query = db.query(Courier).filter(Courier.city == city)

        if organization_id:
            query = query.filter(Courier.organization_id == organization_id)

        return query.offset(skip).limit(limit).all()

    def assign_vehicle(self, db: Session, courier_id: int, vehicle_id: int) -> Courier:
        """Assign a vehicle to courier"""
        courier = self.get(db, courier_id)
        if courier:
            courier.current_vehicle_id = vehicle_id
            db.commit()
            db.refresh(courier)
        return courier

    def unassign_vehicle(self, db: Session, courier_id: int) -> Courier:
        """Unassign vehicle from courier"""
        courier = self.get(db, courier_id)
        if courier:
            courier.current_vehicle_id = None
            db.commit()
            db.refresh(courier)
        return courier

    def update_status(
        self,
        db: Session,
        courier_id: int,
        status: CourierStatus,
        last_working_day: Optional[date] = None,
    ) -> Courier:
        """Update courier status"""
        courier = self.get(db, courier_id)
        if courier:
            courier.status = status
            if status == CourierStatus.TERMINATED and last_working_day:
                courier.last_working_day = last_working_day
            db.commit()
            db.refresh(courier)
        return courier

    def get_expiring_documents(
        self, db: Session, days_threshold: int = 30, organization_id: Optional[int] = None
    ) -> List[CourierDocumentStatus]:
        """
        Get couriers with documents expiring soon
        Args:
            days_threshold: Days until expiry to consider (default 30)
            organization_id: Optional organization ID filter
        """
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)

        query = db.query(Courier).filter(
            and_(
                Courier.status.in_([CourierStatus.ACTIVE, CourierStatus.ON_LEAVE]),
                or_(
                    Courier.iqama_expiry_date <= threshold_date,
                    Courier.passport_expiry_date <= threshold_date,
                    Courier.license_expiry_date <= threshold_date,
                ),
            )
        )

        if organization_id:
            query = query.filter(Courier.organization_id == organization_id)

        couriers = query.all()

        result = []
        for courier in couriers:
            doc_status = CourierDocumentStatus(
                courier_id=courier.id,
                barq_id=courier.barq_id,
                full_name=courier.full_name,
                iqama_expiry_date=courier.iqama_expiry_date,
                iqama_expired=(
                    courier.iqama_expiry_date < today if courier.iqama_expiry_date else False
                ),
                iqama_expires_soon=(
                    courier.iqama_expiry_date <= threshold_date
                    if courier.iqama_expiry_date
                    else False
                ),
                passport_expiry_date=courier.passport_expiry_date,
                passport_expired=(
                    courier.passport_expiry_date < today if courier.passport_expiry_date else False
                ),
                passport_expires_soon=(
                    courier.passport_expiry_date <= threshold_date
                    if courier.passport_expiry_date
                    else False
                ),
                license_expiry_date=courier.license_expiry_date,
                license_expired=(
                    courier.license_expiry_date < today if courier.license_expiry_date else False
                ),
                license_expires_soon=(
                    courier.license_expiry_date <= threshold_date
                    if courier.license_expiry_date
                    else False
                ),
            )

            doc_status.any_expired = (
                doc_status.iqama_expired
                or doc_status.passport_expired
                or doc_status.license_expired
            )
            doc_status.any_expires_soon = (
                doc_status.iqama_expires_soon
                or doc_status.passport_expires_soon
                or doc_status.license_expires_soon
            )

            result.append(doc_status)

        return result

    def get_statistics(self, db: Session, organization_id: Optional[int] = None) -> Dict[str, Any]:
        """Get overall courier statistics"""
        base_query = db.query(Courier)

        if organization_id:
            base_query = base_query.filter(Courier.organization_id == organization_id)

        total = base_query.with_entities(func.count(Courier.id)).scalar()

        status_counts = (
            base_query.with_entities(Courier.status, func.count(Courier.id))
            .group_by(Courier.status)
            .all()
        )

        with_vehicle = (
            base_query.filter(Courier.current_vehicle_id != None)
            .with_entities(func.count(Courier.id))
            .scalar()
        )

        without_vehicle = (
            base_query.filter(Courier.current_vehicle_id == None)
            .filter(Courier.status == CourierStatus.ACTIVE)
            .with_entities(func.count(Courier.id))
            .scalar()
        )

        return {
            "total": total,
            "status_breakdown": dict(status_counts),
            "with_vehicle": with_vehicle,
            "without_vehicle": without_vehicle,
        }

    def search_couriers(
        self,
        db: Session,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[Courier]:
        """Search couriers by name, BARQ ID, email, or phone"""
        query = db.query(Courier)

        if organization_id:
            query = query.filter(Courier.organization_id == organization_id)

        if search_term:
            search_filters = []
            search_fields = ["full_name", "barq_id", "email", "mobile_number", "employee_id"]
            for field in search_fields:
                if hasattr(Courier, field):
                    search_filters.append(getattr(Courier, field).ilike(f"%{search_term}%"))

            if search_filters:
                query = query.filter(or_(*search_filters))

        return query.offset(skip).limit(limit).all()


# Create instance
courier_service = CourierService(Courier)
