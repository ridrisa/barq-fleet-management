"""Delivery Service"""

from datetime import date, datetime
from typing import Dict, List, Optional

from sqlalchemy import and_, extract, func
from sqlalchemy.orm import Session

from app.models.operations.delivery import Delivery, DeliveryStatus
from app.schemas.operations.delivery import DeliveryCreate, DeliveryUpdate
from app.services.base import CRUDBase


class DeliveryService(CRUDBase[Delivery, DeliveryCreate, DeliveryUpdate]):
    """Service for delivery management operations"""

    def get_by_courier(
        self, db: Session, *, courier_id: int, skip: int = 0, limit: int = 100
    ) -> List[Delivery]:
        """
        Get deliveries for a specific courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of delivery records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, db: Session, *, status: DeliveryStatus, skip: int = 0, limit: int = 100
    ) -> List[Delivery]:
        """
        Get deliveries by status

        Args:
            db: Database session
            status: Delivery status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of delivery records
        """
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_tracking_number(self, db: Session, *, tracking_number: str) -> Optional[Delivery]:
        """
        Get delivery by tracking number

        Args:
            db: Database session
            tracking_number: Unique tracking number

        Returns:
            Delivery record or None
        """
        return db.query(self.model).filter(self.model.tracking_number == tracking_number).first()

    def update_status(
        self, db: Session, *, delivery_id: int, status: DeliveryStatus, notes: Optional[str] = None
    ) -> Optional[Delivery]:
        """
        Update delivery status

        Args:
            db: Database session
            delivery_id: ID of the delivery
            status: New status
            notes: Optional notes about the status change

        Returns:
            Updated delivery or None if not found
        """
        delivery = self.get(db, id=delivery_id)
        if not delivery:
            return None

        update_data = {"status": status}

        # Set delivery_time when status is DELIVERED
        if status == DeliveryStatus.DELIVERED:
            update_data["delivery_time"] = datetime.now()

        if notes:
            update_data["notes"] = notes

        return self.update(db, db_obj=delivery, obj_in=update_data)

    def get_pending_deliveries(
        self, db: Session, *, courier_id: Optional[int] = None, skip: int = 0, limit: int = 100
    ) -> List[Delivery]:
        """
        Get pending deliveries, optionally filtered by courier

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of pending delivery records
        """
        query = db.query(self.model).filter(self.model.status == DeliveryStatus.PENDING)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def get_deliveries_by_date_range(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Delivery]:
        """
        Get deliveries within a date range

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of delivery records
        """
        query = db.query(self.model).filter(
            and_(self.model.created_at >= start_date, self.model.created_at <= end_date)
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict:
        """
        Get delivery statistics

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with delivery statistics
        """
        query = db.query(self.model)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if start_date:
            query = query.filter(self.model.created_at >= start_date)
        if end_date:
            query = query.filter(self.model.created_at <= end_date)

        deliveries = query.all()

        total_deliveries = len(deliveries)
        pending = sum(1 for d in deliveries if d.status == DeliveryStatus.PENDING)
        in_transit = sum(1 for d in deliveries if d.status == DeliveryStatus.IN_TRANSIT)
        delivered = sum(1 for d in deliveries if d.status == DeliveryStatus.DELIVERED)
        failed = sum(1 for d in deliveries if d.status == DeliveryStatus.FAILED)
        returned = sum(1 for d in deliveries if d.status == DeliveryStatus.RETURNED)

        total_cod = sum(d.cod_amount or 0 for d in deliveries)
        collected_cod = sum(
            d.cod_amount or 0 for d in deliveries if d.status == DeliveryStatus.DELIVERED
        )

        return {
            "total_deliveries": total_deliveries,
            "pending": pending,
            "in_transit": in_transit,
            "delivered": delivered,
            "failed": failed,
            "returned": returned,
            "success_rate": (delivered / total_deliveries * 100) if total_deliveries > 0 else 0,
            "total_cod_amount": total_cod,
            "collected_cod_amount": collected_cod,
            "pending_cod_amount": total_cod - collected_cod,
        }

    def assign_to_courier(
        self, db: Session, *, delivery_id: int, courier_id: int
    ) -> Optional[Delivery]:
        """
        Assign delivery to a courier

        Args:
            db: Database session
            delivery_id: ID of the delivery
            courier_id: ID of the courier

        Returns:
            Updated delivery or None if not found
        """
        delivery = self.get(db, id=delivery_id)
        if not delivery:
            return None

        update_data = {
            "courier_id": courier_id,
            "status": DeliveryStatus.IN_TRANSIT,
            "pickup_time": datetime.now(),
        }

        return self.update(db, db_obj=delivery, obj_in=update_data)

    def get_cod_deliveries(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        status: Optional[DeliveryStatus] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Delivery]:
        """
        Get deliveries with COD amount

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            status: Optional status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of delivery records with COD
        """
        query = db.query(self.model).filter(self.model.cod_amount > 0)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if status:
            query = query.filter(self.model.status == status)

        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()


delivery_service = DeliveryService(Delivery)
