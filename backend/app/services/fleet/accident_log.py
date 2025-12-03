from datetime import date
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.fleet import AccidentLog, AccidentSeverity, AccidentStatus
from app.schemas.fleet import AccidentLogCreate, AccidentLogUpdate
from app.services.base import CRUDBase


class AccidentLogService(CRUDBase[AccidentLog, AccidentLogCreate, AccidentLogUpdate]):
    """Service for AccidentLog operations"""

    def get_for_vehicle(
        self,
        db: Session,
        vehicle_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[AccidentLog]:
        """Get accident logs for a vehicle"""
        query = db.query(AccidentLog).filter(AccidentLog.vehicle_id == vehicle_id)

        if organization_id:
            query = query.filter(AccidentLog.organization_id == organization_id)

        return query.order_by(AccidentLog.accident_date.desc()).offset(skip).limit(limit).all()

    def get_for_courier(
        self,
        db: Session,
        courier_id: int,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[AccidentLog]:
        """Get accident logs for a courier"""
        query = db.query(AccidentLog).filter(AccidentLog.courier_id == courier_id)

        if organization_id:
            query = query.filter(AccidentLog.organization_id == organization_id)

        return query.order_by(AccidentLog.accident_date.desc()).offset(skip).limit(limit).all()

    def get_by_severity(
        self,
        db: Session,
        severity: AccidentSeverity,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[AccidentLog]:
        """Get accidents by severity"""
        query = db.query(AccidentLog).filter(AccidentLog.severity == severity)

        if organization_id:
            query = query.filter(AccidentLog.organization_id == organization_id)

        return query.order_by(AccidentLog.accident_date.desc()).offset(skip).limit(limit).all()

    def get_open_cases(
        self, db: Session, *, skip: int = 0, limit: int = 100, organization_id: Optional[int] = None
    ) -> List[AccidentLog]:
        """Get open accident cases"""
        query = db.query(AccidentLog).filter(
            AccidentLog.status.notin_([AccidentStatus.RESOLVED, AccidentStatus.CLOSED])
        )

        if organization_id:
            query = query.filter(AccidentLog.organization_id == organization_id)

        return query.order_by(AccidentLog.accident_date.desc()).offset(skip).limit(limit).all()

    def get_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        *,
        skip: int = 0,
        limit: int = 100,
        organization_id: Optional[int] = None,
    ) -> List[AccidentLog]:
        """Get accidents within a date range"""
        query = db.query(AccidentLog).filter(
            and_(AccidentLog.accident_date >= start_date, AccidentLog.accident_date <= end_date)
        )

        if organization_id:
            query = query.filter(AccidentLog.organization_id == organization_id)

        return query.order_by(AccidentLog.accident_date.desc()).offset(skip).limit(limit).all()


accident_log_service = AccidentLogService(AccidentLog)
