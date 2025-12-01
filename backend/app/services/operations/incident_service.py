"""Incident Service"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date

from app.services.base import CRUDBase
from app.models.operations.incident import Incident, IncidentType, IncidentStatus
from app.schemas.operations.incident import IncidentCreate, IncidentUpdate


class IncidentService(CRUDBase[Incident, IncidentCreate, IncidentUpdate]):
    """Service for incident management operations"""

    def get_by_courier(
        self,
        db: Session,
        *,
        courier_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get incidents for a specific courier

        Args:
            db: Database session
            courier_id: ID of the courier
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of incident records
        """
        return (
            db.query(self.model)
            .filter(self.model.courier_id == courier_id)
            .order_by(self.model.incident_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_vehicle(
        self,
        db: Session,
        *,
        vehicle_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get incidents for a specific vehicle

        Args:
            db: Database session
            vehicle_id: ID of the vehicle
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of incident records
        """
        return (
            db.query(self.model)
            .filter(self.model.vehicle_id == vehicle_id)
            .order_by(self.model.incident_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self,
        db: Session,
        *,
        incident_type: IncidentType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get incidents by type

        Args:
            db: Database session
            incident_type: Type of incident
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of incident records
        """
        return (
            db.query(self.model)
            .filter(self.model.incident_type == incident_type)
            .order_by(self.model.incident_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: IncidentStatus,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get incidents by status

        Args:
            db: Database session
            status: Incident status
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of incident records
        """
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .order_by(self.model.incident_date.desc())
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
        vehicle_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get incidents within a date range

        Args:
            db: Database session
            start_date: Start date
            end_date: End date
            courier_id: Optional courier ID to filter by
            vehicle_id: Optional vehicle ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of incident records
        """
        query = db.query(self.model).filter(
            and_(
                self.model.incident_date >= start_date,
                self.model.incident_date <= end_date
            )
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if vehicle_id:
            query = query.filter(self.model.vehicle_id == vehicle_id)

        return (
            query.order_by(self.model.incident_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_open_incidents(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get open incidents (reported or investigating)

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            vehicle_id: Optional vehicle ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of open incident records
        """
        query = db.query(self.model).filter(
            self.model.status.in_([
                IncidentStatus.REPORTED,
                IncidentStatus.INVESTIGATING
            ])
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if vehicle_id:
            query = query.filter(self.model.vehicle_id == vehicle_id)

        return (
            query.order_by(self.model.incident_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        db: Session,
        *,
        incident_id: int,
        status: IncidentStatus,
        resolution: Optional[str] = None
    ) -> Optional[Incident]:
        """
        Update incident status

        Args:
            db: Database session
            incident_id: ID of the incident
            status: New status
            resolution: Optional resolution notes (required for RESOLVED/CLOSED)

        Returns:
            Updated incident or None if not found
        """
        incident = self.get(db, id=incident_id)
        if not incident:
            return None

        update_data = {"status": status}

        if resolution:
            update_data["resolution"] = resolution

        return self.update(db, db_obj=incident, obj_in=update_data)

    def resolve_incident(
        self,
        db: Session,
        *,
        incident_id: int,
        resolution: str,
        cost: Optional[int] = None
    ) -> Optional[Incident]:
        """
        Mark incident as resolved

        Args:
            db: Database session
            incident_id: ID of the incident
            resolution: Resolution description
            cost: Optional cost of resolution

        Returns:
            Updated incident or None if not found
        """
        incident = self.get(db, id=incident_id)
        if not incident:
            return None

        update_data = {
            "status": IncidentStatus.RESOLVED,
            "resolution": resolution
        }

        if cost is not None:
            update_data["cost"] = cost

        return self.update(db, db_obj=incident, obj_in=update_data)

    def close_incident(
        self,
        db: Session,
        *,
        incident_id: int,
        resolution: Optional[str] = None
    ) -> Optional[Incident]:
        """
        Close an incident

        Args:
            db: Database session
            incident_id: ID of the incident
            resolution: Optional final resolution notes

        Returns:
            Updated incident or None if not found
        """
        incident = self.get(db, id=incident_id)
        if not incident:
            return None

        update_data = {"status": IncidentStatus.CLOSED}

        if resolution:
            update_data["resolution"] = resolution

        return self.update(db, db_obj=incident, obj_in=update_data)

    def get_statistics(
        self,
        db: Session,
        *,
        courier_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get incident statistics

        Args:
            db: Database session
            courier_id: Optional courier ID to filter by
            vehicle_id: Optional vehicle ID to filter by
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            Dictionary with incident statistics
        """
        query = db.query(self.model)

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if vehicle_id:
            query = query.filter(self.model.vehicle_id == vehicle_id)
        if start_date:
            query = query.filter(self.model.incident_date >= start_date)
        if end_date:
            query = query.filter(self.model.incident_date <= end_date)

        incidents = query.all()

        total_incidents = len(incidents)

        # Count by status
        reported = sum(1 for i in incidents if i.status == IncidentStatus.REPORTED)
        investigating = sum(1 for i in incidents if i.status == IncidentStatus.INVESTIGATING)
        resolved = sum(1 for i in incidents if i.status == IncidentStatus.RESOLVED)
        closed = sum(1 for i in incidents if i.status == IncidentStatus.CLOSED)

        # Count by type
        accidents = sum(1 for i in incidents if i.incident_type == IncidentType.ACCIDENT)
        thefts = sum(1 for i in incidents if i.incident_type == IncidentType.THEFT)
        damages = sum(1 for i in incidents if i.incident_type == IncidentType.DAMAGE)
        violations = sum(1 for i in incidents if i.incident_type == IncidentType.VIOLATION)
        other = sum(1 for i in incidents if i.incident_type == IncidentType.OTHER)

        # Calculate costs
        total_cost = sum(i.cost or 0 for i in incidents)
        resolved_cost = sum(
            i.cost or 0
            for i in incidents
            if i.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
        )

        return {
            "total_incidents": total_incidents,
            "by_status": {
                "reported": reported,
                "investigating": investigating,
                "resolved": resolved,
                "closed": closed,
                "open": reported + investigating
            },
            "by_type": {
                "accident": accidents,
                "theft": thefts,
                "damage": damages,
                "violation": violations,
                "other": other
            },
            "costs": {
                "total_cost": total_cost,
                "resolved_cost": resolved_cost,
                "average_cost": total_cost / total_incidents if total_incidents > 0 else 0
            },
            "resolution_rate": (resolved + closed) / total_incidents * 100 if total_incidents > 0 else 0
        }

    def get_high_cost_incidents(
        self,
        db: Session,
        *,
        min_cost: int = 1000,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get incidents with high costs

        Args:
            db: Database session
            min_cost: Minimum cost threshold
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of high-cost incident records
        """
        return (
            db.query(self.model)
            .filter(self.model.cost >= min_cost)
            .order_by(self.model.cost.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent_incidents(
        self,
        db: Session,
        *,
        days: int = 30,
        courier_id: Optional[int] = None,
        vehicle_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        """
        Get recent incidents within specified days

        Args:
            db: Database session
            days: Number of days to look back
            courier_id: Optional courier ID to filter by
            vehicle_id: Optional vehicle ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of recent incident records
        """
        from datetime import timedelta
        cutoff_date = date.today() - timedelta(days=days)

        query = db.query(self.model).filter(
            self.model.incident_date >= cutoff_date
        )

        if courier_id:
            query = query.filter(self.model.courier_id == courier_id)
        if vehicle_id:
            query = query.filter(self.model.vehicle_id == vehicle_id)

        return (
            query.order_by(self.model.incident_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )


incident_service = IncidentService(Incident)
