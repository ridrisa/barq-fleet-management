"""
BigQuery Sync Service - Migrates courier data from SANED BigQuery to local database

Maps fields from BigQuery `ultimate` table to local Courier model.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models.fleet.courier import (
    Courier,
    CourierStatus,
    ProjectType,
    SponsorshipStatus,
)
from app.services.integrations.bigquery_client import bigquery_client

logger = logging.getLogger(__name__)


class BigQuerySyncService:
    """Service to sync courier data from BigQuery to local database"""

    # Status mapping: BigQuery value -> CourierStatus enum
    STATUS_MAP = {
        "Active": CourierStatus.ACTIVE,
        "active": CourierStatus.ACTIVE,
        "ACTIVE": CourierStatus.ACTIVE,
        "Inactive": CourierStatus.INACTIVE,
        "inactive": CourierStatus.INACTIVE,
        "INACTIVE": CourierStatus.INACTIVE,
        "On Leave": CourierStatus.ON_LEAVE,
        "on leave": CourierStatus.ON_LEAVE,
        "ON_LEAVE": CourierStatus.ON_LEAVE,
        "Terminated": CourierStatus.TERMINATED,
        "terminated": CourierStatus.TERMINATED,
        "TERMINATED": CourierStatus.TERMINATED,
        "Onboarding": CourierStatus.ONBOARDING,
        "onboarding": CourierStatus.ONBOARDING,
        "ONBOARDING": CourierStatus.ONBOARDING,
        "Suspended": CourierStatus.SUSPENDED,
        "suspended": CourierStatus.SUSPENDED,
        "SUSPENDED": CourierStatus.SUSPENDED,
    }

    # Sponsorship mapping: BigQuery value -> SponsorshipStatus enum
    SPONSORSHIP_MAP = {
        "Ajeer": SponsorshipStatus.AJEER,
        "ajeer": SponsorshipStatus.AJEER,
        "AJEER": SponsorshipStatus.AJEER,
        "Inhouse": SponsorshipStatus.INHOUSE,
        "inhouse": SponsorshipStatus.INHOUSE,
        "INHOUSE": SponsorshipStatus.INHOUSE,
        "In-House": SponsorshipStatus.INHOUSE,
        "In House": SponsorshipStatus.INHOUSE,
        "Trial": SponsorshipStatus.TRIAL,
        "trial": SponsorshipStatus.TRIAL,
        "TRIAL": SponsorshipStatus.TRIAL,
        "Freelancer": SponsorshipStatus.FREELANCER,
        "freelancer": SponsorshipStatus.FREELANCER,
        "FREELANCER": SponsorshipStatus.FREELANCER,
    }

    # Project mapping: BigQuery value -> ProjectType enum
    PROJECT_MAP = {
        "Ecommerce": ProjectType.ECOMMERCE,
        "ecommerce": ProjectType.ECOMMERCE,
        "ECOMMERCE": ProjectType.ECOMMERCE,
        "E-commerce": ProjectType.ECOMMERCE,
        "Food": ProjectType.FOOD,
        "food": ProjectType.FOOD,
        "FOOD": ProjectType.FOOD,
        "Warehouse": ProjectType.WAREHOUSE,
        "warehouse": ProjectType.WAREHOUSE,
        "WAREHOUSE": ProjectType.WAREHOUSE,
        "Barq": ProjectType.BARQ,
        "barq": ProjectType.BARQ,
        "BARQ": ProjectType.BARQ,
        "Mixed": ProjectType.MIXED,
        "mixed": ProjectType.MIXED,
        "MIXED": ProjectType.MIXED,
    }

    def _parse_date(self, value: Any) -> Optional[datetime]:
        """Parse date from various formats"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.date() if hasattr(value, "date") else value
        if hasattr(value, "date"):  # datetime-like object
            return value.date()
        if isinstance(value, str):
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        return None

    def _map_status(self, bq_status: Optional[str]) -> CourierStatus:
        """Map BigQuery status to CourierStatus enum"""
        if bq_status is None:
            return CourierStatus.ONBOARDING
        return self.STATUS_MAP.get(bq_status, CourierStatus.ONBOARDING)

    def _map_sponsorship(
        self, bq_sponsorship: Optional[str]
    ) -> Optional[SponsorshipStatus]:
        """Map BigQuery sponsorship to SponsorshipStatus enum"""
        if bq_sponsorship is None:
            return None
        return self.SPONSORSHIP_MAP.get(bq_sponsorship)

    def _map_project(self, bq_project: Optional[str]) -> Optional[ProjectType]:
        """Map BigQuery project to ProjectType enum"""
        if bq_project is None:
            return None
        return self.PROJECT_MAP.get(bq_project)

    def _bq_row_to_courier_data(
        self, bq_row: Dict[str, Any], organization_id: int
    ) -> Dict[str, Any]:
        """Convert BigQuery row to Courier model data dict"""
        return {
            "organization_id": organization_id,
            "barq_id": str(bq_row.get("BARQ_ID", "")) if bq_row.get("BARQ_ID") else None,
            "full_name": bq_row.get("Name"),
            "mobile_number": bq_row.get("mobile_number") or "",
            "national_id": (
                str(bq_row.get("id_number")) if bq_row.get("id_number") else None
            ),
            "status": self._map_status(bq_row.get("Status")),
            "sponsorship_status": self._map_sponsorship(
                bq_row.get("SponsorshipStatus")
            ),
            "project_type": self._map_project(bq_row.get("PROJECT")),
            "supervisor_name": bq_row.get("Supervisor"),
            "city": bq_row.get("city"),
            "joining_date": self._parse_date(bq_row.get("joining_Date")),
            "last_working_day": self._parse_date(bq_row.get("last_working_day")),
            "iban": bq_row.get("IBAN"),
            "total_deliveries": int(bq_row.get("Total_Orders") or 0),
        }

    def sync_courier(
        self,
        db: Session,
        bq_row: Dict[str, Any],
        organization_id: int,
        update_existing: bool = True,
    ) -> Tuple[Courier, str]:
        """
        Sync a single courier from BigQuery data.

        Returns tuple of (courier, action) where action is 'created', 'updated', or 'skipped'
        """
        barq_id = str(bq_row.get("BARQ_ID", ""))
        if not barq_id:
            logger.warning("Skipping row without BARQ_ID")
            return None, "skipped"

        # Check if courier exists
        existing = db.query(Courier).filter(Courier.barq_id == barq_id).first()

        courier_data = self._bq_row_to_courier_data(bq_row, organization_id)

        if existing:
            if not update_existing:
                return existing, "skipped"

            # Update existing courier
            for key, value in courier_data.items():
                if key != "organization_id" and value is not None:
                    setattr(existing, key, value)

            db.flush()
            logger.info(f"Updated courier: {barq_id}")
            return existing, "updated"
        else:
            # Create new courier
            # Ensure required fields
            if not courier_data.get("full_name"):
                courier_data["full_name"] = f"Courier {barq_id}"
            if not courier_data.get("mobile_number"):
                courier_data["mobile_number"] = ""

            new_courier = Courier(**courier_data)
            db.add(new_courier)
            db.flush()
            logger.info(f"Created courier: {barq_id}")
            return new_courier, "created"

    def sync_all_couriers(
        self,
        db: Session,
        organization_id: int,
        update_existing: bool = True,
        batch_size: int = 100,
        status_filter: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Sync all couriers from BigQuery to local database.

        Returns stats dict with counts of created, updated, skipped, and errors.
        """
        stats = {"created": 0, "updated": 0, "skipped": 0, "errors": 0, "total": 0}

        offset = 0
        while True:
            # Fetch batch from BigQuery
            try:
                if status_filter:
                    bq_couriers = bigquery_client.get_all_couriers(
                        skip=offset, limit=batch_size, status=status_filter
                    )
                else:
                    bq_couriers = bigquery_client.get_all_couriers(
                        skip=offset, limit=batch_size
                    )
            except Exception as e:
                logger.error(f"Error fetching from BigQuery at offset {offset}: {e}")
                stats["errors"] += 1
                break

            if not bq_couriers:
                break

            # Process batch
            for bq_row in bq_couriers:
                stats["total"] += 1
                try:
                    courier, action = self.sync_courier(
                        db, bq_row, organization_id, update_existing
                    )
                    if action == "created":
                        stats["created"] += 1
                    elif action == "updated":
                        stats["updated"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    logger.error(
                        f"Error syncing courier {bq_row.get('BARQ_ID')}: {e}"
                    )
                    stats["errors"] += 1

            # Commit batch
            try:
                db.commit()
                logger.info(
                    f"Committed batch: offset={offset}, batch_size={len(bq_couriers)}"
                )
            except Exception as e:
                logger.error(f"Error committing batch at offset {offset}: {e}")
                db.rollback()
                stats["errors"] += len(bq_couriers)

            offset += batch_size

            # Safety break for testing (remove in production)
            if offset > 300000:  # Max ~297k rows in ultimate table
                break

        logger.info(f"Sync completed: {stats}")
        return stats

    def sync_single_by_barq_id(
        self, db: Session, barq_id: int, organization_id: int
    ) -> Tuple[Optional[Courier], str]:
        """
        Sync a single courier by BARQ_ID from BigQuery.

        Returns tuple of (courier, action) or (None, 'not_found')
        """
        bq_row = bigquery_client.get_courier_by_barq_id(barq_id)

        if not bq_row:
            return None, "not_found"

        courier, action = self.sync_courier(
            db, bq_row, organization_id, update_existing=True
        )
        db.commit()

        return courier, action


# Singleton instance
bigquery_sync_service = BigQuerySyncService()
