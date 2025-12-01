"""COD Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date
from decimal import Decimal

from app.services.base import CRUDBase
from app.models.operations.cod import COD, CODStatus
from app.schemas.operations.cod import CODCreate, CODUpdate


class CODService(CRUDBase[COD, CODCreate, CODUpdate]):
    """Service for COD (Cash On Delivery) management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[COD]:
        """
        Get COD transactions for a specific courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of COD records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.collection_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: CODStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[COD]:
        """
        Get COD transactions by status

        Args:
            db: Database session
            status: COD status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of COD records
        """
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.collection_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[COD]:
        """
        Get pending COD transactions

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of pending COD records
        """
        query = db.query(self.model).filter(
            self.model.status == CODStatus.PENDING
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return (
            query.order_by(self.model.collection_date.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        db: Session,
        *,
        start_date: date,
        end_date: date,
        courier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[COD]:
        """
        Get COD transactions within a date range

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            courier_id: Optional courier ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of COD records
        """
        query = db.query(self.model).filter(
            and_(
                self.model.collection_date >= start_date,
                self.model.collection_date <= end_date
            )
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)

        return (
            query.order_by(self.model.collection_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def mark_as_collected(
        self,
        db: Session,
        *,
        cod_id: int,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[COD]:
        """
        Mark COD as collected

        Args:
            db: Database session
            cod_id: ID of the COD transaction
            reference_number: Optional reference number
            notes: Optional notes

        Returns:
            Updated COD record or None if not found
        """
        cod = self.get(db, id=cod_id)
        if not cod:
            return None

        update_data = {
            "status": CODStatus.COLLECTED
        }

        if reference_number:
            update_data["reference_number"] = reference_number
        if notes:
            update_data["notes"] = notes

        return self.update(db, db_obj=cod, obj_in=update_data)

    def mark_as_deposited(
        self,
        db: Session,
        *,
        cod_id: int,
        deposit_date: Optional[date] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[COD]:
        """
        Mark COD as deposited

        Args:
            db: Database session
            cod_id: ID of the COD transaction
            deposit_date: Date of deposit (defaults to today)
            reference_number: Optional reference number
            notes: Optional notes

        Returns:
            Updated COD record or None if not found
        """
        cod = self.get(db, id=cod_id)
        if not cod:
            return None

        update_data = {
            "status": CODStatus.DEPOSITED,
            "deposit_date": deposit_date or date.today()
        }

        if reference_number:
            update_data["reference_number"] = reference_number
        if notes:
            update_data["notes"] = notes

        return self.update(db, db_obj=cod, obj_in=update_data)

    def mark_as_reconciled(
        self,
        db: Session,
        *,
        cod_id: int,
        notes: Optional[str] = None
    ) -> Optional[COD]:
        """
        Mark COD as reconciled

        Args:
            db: Database session
            cod_id: ID of the COD transaction
            notes: Optional notes

        Returns:
            Updated COD record or None if not found
        """
        cod = self.get(db, id=cod_id)
        if not cod:
            return None

        update_data = {
            "status": CODStatus.RECONCILED
        }

        if notes:
            update_data["notes"] = notes

        return self.update(db, db_obj=cod, obj_in=update_data)

    def bulk_deposit(
        self,
        db: Session,
        *,
        cod_ids: List[int],
        deposit_date: Optional[date] = None,
        reference_number: Optional[str] = None
    ) -> int:
        """
        Mark multiple COD transactions as deposited

        Args:
            db: Database session
            cod_ids: List of COD IDs
            deposit_date: Date of deposit (defaults to today)
            reference_number: Optional reference number

        Returns:
            Number of records updated
        """
        update_data = {
            "status": CODStatus.DEPOSITED,
            "deposit_date": deposit_date or date.today()
        }

        if reference_number:
            update_data["reference_number"] = reference_number

        return self.bulk_update(db, ids=cod_ids, update_data=update_data)

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get COD statistics

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with COD statistics
        """
        query = db.query(self.model)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if start_date:
            query = query.filter(self.model.collection_date >= start_date)
        if end_date:
            query = query.filter(self.model.collection_date <= end_date)

        cods = query.all()

        total_transactions = len(cods)
        pending = sum(1 for c in cods if c.status == CODStatus.PENDING)
        collected = sum(1 for c in cods if c.status == CODStatus.COLLECTED)
        deposited = sum(1 for c in cods if c.status == CODStatus.DEPOSITED)
        reconciled = sum(1 for c in cods if c.status == CODStatus.RECONCILED)

        total_amount = sum(c.amount for c in cods)
        pending_amount = sum(
            c.amount for c in cods if c.status == CODStatus.PENDING
        )
        collected_amount = sum(
            c.amount for c in cods if c.status == CODStatus.COLLECTED
        )
        deposited_amount = sum(
            c.amount for c in cods if c.status == CODStatus.DEPOSITED
        )
        reconciled_amount = sum(
            c.amount for c in cods if c.status == CODStatus.RECONCILED
        )

        return {
            "total_transactions": total_transactions,
            "pending_count": pending,
            "collected_count": collected,
            "deposited_count": deposited,
            "reconciled_count": reconciled,
            "total_amount": float(total_amount),
            "pending_amount": float(pending_amount),
            "collected_amount": float(collected_amount),
            "deposited_amount": float(deposited_amount),
            "reconciled_amount": float(reconciled_amount),
            "average_transaction_amount": float(total_amount / total_transactions) if total_transactions > 0 else 0
        }

    def get_courier_balance(
        self,
        db: Session,
        *,
        courier_id: int
    ) -> Dict:
        """
        Get courier's COD balance (pending + collected amounts)

        Args:
            db: Database session
            courier_id: ID of the courier

        Returns:
            Dictionary with balance information
        """
        pending_cods = db.query(self.model).filter(
            and_(
                self.model.courier_id == courier_id,
                self.model.status.in_([CODStatus.PENDING, CODStatus.COLLECTED])
            )
        ).all()

        pending_amount = sum(
            cod.amount for cod in pending_cods
            if cod.status == CODStatus.PENDING
        )
        collected_amount = sum(
            cod.amount for cod in pending_cods
            if cod.status == CODStatus.COLLECTED
        )

        total_balance = pending_amount + collected_amount

        return {
            "courier_id": courier_id,
            "pending_amount": float(pending_amount),
            "collected_amount": float(collected_amount),
            "total_balance": float(total_balance),
            "transaction_count": len(pending_cods)
        }

    def settle_courier_cod(
        self,
        db: Session,
        *,
        courier_id: int,
        deposit_date: Optional[date] = None,
        reference_number: Optional[str] = None
    ) -> Dict:
        """
        Settle all pending and collected COD for a courier

        Args:
            db: Database session
            courier_id: ID of the courier
            deposit_date: Date of deposit (defaults to today)
            reference_number: Optional reference number

        Returns:
            Dictionary with settlement information
        """
        # Get all pending and collected COD for courier
        cods = db.query(self.model).filter(
            and_(
                self.model.courier_id == courier_id,
                self.model.status.in_([CODStatus.PENDING, CODStatus.COLLECTED])
            )
        ).all()

        if not cods:
            return {
                "courier_id": courier_id,
                "transactions_settled": 0,
                "total_amount": 0.0,
                "message": "No pending or collected COD transactions found"
            }

        cod_ids = [cod.id for cod in cods]
        total_amount = sum(cod.amount for cod in cods)

        # Mark all as deposited
        updated_count = self.bulk_deposit(
            db,
            cod_ids=cod_ids,
            deposit_date=deposit_date,
            reference_number=reference_number
        )

        return {
            "courier_id": courier_id,
            "transactions_settled": updated_count,
            "total_amount": float(total_amount),
            "deposit_date": (deposit_date or date.today()).isoformat(),
            "reference_number": reference_number
        }


cod_service = CODService(COD)
