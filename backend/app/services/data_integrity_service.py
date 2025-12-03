"""Data Integrity Service

Provides data integrity checks and validation:
- Orphaned record detection
- Constraint violation checks
- Data consistency validation
- Duplicate detection
- Reference integrity verification
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, func, or_, text
from sqlalchemy.orm import Session

from app.models.fleet.assignment import Assignment
from app.models.fleet.courier import Courier
from app.models.fleet.vehicle import Vehicle
from app.models.hr.leave import Leave
from app.models.hr.loan import Loan
from app.models.hr.salary import Salary
from app.models.operations.delivery import Delivery


class DataIntegrityService:
    """
    Service for data integrity checks and validation

    Provides:
    - Orphaned record detection
    - Reference integrity checks
    - Duplicate detection
    - Data consistency validation
    """

    def run_full_integrity_check(self, db: Session) -> Dict[str, Any]:
        """
        Run comprehensive data integrity check

        Returns:
            Dictionary with integrity check results
        """
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "orphaned_records": self.check_orphaned_records(db),
                "duplicates": self.check_duplicates(db),
                "consistency": self.check_data_consistency(db),
                "reference_integrity": self.check_reference_integrity(db),
            },
            "summary": {},
        }

        # Calculate summary
        total_issues = 0
        for check_name, check_result in results["checks"].items():
            total_issues += check_result.get("issues_found", 0)

        results["summary"] = {
            "total_issues": total_issues,
            "status": "healthy" if total_issues == 0 else "issues_found",
        }

        return results

    def check_orphaned_records(self, db: Session) -> Dict[str, Any]:
        """Check for orphaned records (records with invalid foreign keys)"""
        issues = []

        # Check for salaries without couriers
        orphaned_salaries = (
            db.query(Salary)
            .outerjoin(Courier, Salary.courier_id == Courier.id)
            .filter(Courier.id.is_(None))
            .count()
        )

        if orphaned_salaries > 0:
            issues.append(
                {
                    "table": "salaries",
                    "issue": "orphaned_records",
                    "count": orphaned_salaries,
                    "description": "Salary records exist without corresponding courier",
                }
            )

        # Check for assignments without courier or vehicle
        orphaned_assignments_courier = (
            db.query(Assignment)
            .outerjoin(Courier, Assignment.courier_id == Courier.id)
            .filter(Courier.id.is_(None))
            .count()
        )

        if orphaned_assignments_courier > 0:
            issues.append(
                {
                    "table": "assignments",
                    "issue": "orphaned_courier",
                    "count": orphaned_assignments_courier,
                    "description": "Assignments exist without corresponding courier",
                }
            )

        orphaned_assignments_vehicle = (
            db.query(Assignment)
            .outerjoin(Vehicle, Assignment.vehicle_id == Vehicle.id)
            .filter(Vehicle.id.is_(None))
            .count()
        )

        if orphaned_assignments_vehicle > 0:
            issues.append(
                {
                    "table": "assignments",
                    "issue": "orphaned_vehicle",
                    "count": orphaned_assignments_vehicle,
                    "description": "Assignments exist without corresponding vehicle",
                }
            )

        return {
            "check": "orphaned_records",
            "status": "pass" if len(issues) == 0 else "fail",
            "issues_found": len(issues),
            "details": issues,
        }

    def check_duplicates(self, db: Session) -> Dict[str, Any]:
        """Check for duplicate records"""
        issues = []

        # Check for duplicate courier employee IDs
        duplicate_employee_ids = (
            db.query(Courier.employee_id, func.count(Courier.id).label("count"))
            .group_by(Courier.employee_id)
            .having(func.count(Courier.id) > 1)
            .all()
        )

        if duplicate_employee_ids:
            issues.append(
                {
                    "table": "couriers",
                    "issue": "duplicate_employee_ids",
                    "count": len(duplicate_employee_ids),
                    "description": "Multiple couriers with same employee ID",
                    "examples": [
                        {"employee_id": eid, "count": count}
                        for eid, count in duplicate_employee_ids[:5]
                    ],
                }
            )

        # Check for duplicate vehicle license plates
        duplicate_plates = (
            db.query(Vehicle.license_plate, func.count(Vehicle.id).label("count"))
            .group_by(Vehicle.license_plate)
            .having(func.count(Vehicle.id) > 1)
            .all()
        )

        if duplicate_plates:
            issues.append(
                {
                    "table": "vehicles",
                    "issue": "duplicate_license_plates",
                    "count": len(duplicate_plates),
                    "description": "Multiple vehicles with same license plate",
                    "examples": [
                        {"license_plate": plate, "count": count}
                        for plate, count in duplicate_plates[:5]
                    ],
                }
            )

        return {
            "check": "duplicates",
            "status": "pass" if len(issues) == 0 else "fail",
            "issues_found": len(issues),
            "details": issues,
        }

    def check_data_consistency(self, db: Session) -> Dict[str, Any]:
        """Check for data consistency issues"""
        issues = []

        # Check for salaries where net > gross
        invalid_salaries = db.query(Salary).filter(Salary.net_salary > Salary.gross_salary).count()

        if invalid_salaries > 0:
            issues.append(
                {
                    "table": "salaries",
                    "issue": "net_greater_than_gross",
                    "count": invalid_salaries,
                    "description": "Salary records where net salary > gross salary",
                }
            )

        # Check for leaves where start_date > end_date
        invalid_leaves = db.query(Leave).filter(Leave.start_date > Leave.end_date).count()

        if invalid_leaves > 0:
            issues.append(
                {
                    "table": "leaves",
                    "issue": "invalid_date_range",
                    "count": invalid_leaves,
                    "description": "Leave records where start date is after end date",
                }
            )

        # Check for loans where outstanding > amount
        invalid_loans = db.query(Loan).filter(Loan.outstanding_balance > Loan.amount).count()

        if invalid_loans > 0:
            issues.append(
                {
                    "table": "loans",
                    "issue": "invalid_balance",
                    "count": invalid_loans,
                    "description": "Loan records where outstanding balance > loan amount",
                }
            )

        # Check for assignments where start_date > end_date (if end_date exists)
        invalid_assignments = (
            db.query(Assignment)
            .filter(
                and_(Assignment.end_date.isnot(None), Assignment.start_date > Assignment.end_date)
            )
            .count()
        )

        if invalid_assignments > 0:
            issues.append(
                {
                    "table": "assignments",
                    "issue": "invalid_date_range",
                    "count": invalid_assignments,
                    "description": "Assignment records where start date is after end date",
                }
            )

        return {
            "check": "data_consistency",
            "status": "pass" if len(issues) == 0 else "fail",
            "issues_found": len(issues),
            "details": issues,
        }

    def check_reference_integrity(self, db: Session) -> Dict[str, Any]:
        """Check reference integrity"""
        issues = []

        # Check for overlapping vehicle assignments
        overlapping_assignments = db.execute(
            text(
                """
            SELECT a1.vehicle_id, COUNT(*) as overlap_count
            FROM assignments a1
            JOIN assignments a2 ON a1.vehicle_id = a2.vehicle_id
                AND a1.id != a2.id
                AND a1.start_date <= COALESCE(a2.end_date, CURRENT_DATE)
                AND COALESCE(a1.end_date, CURRENT_DATE) >= a2.start_date
            GROUP BY a1.vehicle_id
            HAVING COUNT(*) > 0
        """
            )
        ).fetchall()

        if overlapping_assignments:
            issues.append(
                {
                    "table": "assignments",
                    "issue": "overlapping_assignments",
                    "count": len(overlapping_assignments),
                    "description": "Vehicles with overlapping assignments",
                    "examples": [
                        {"vehicle_id": vid, "overlaps": count}
                        for vid, count in overlapping_assignments[:5]
                    ],
                }
            )

        return {
            "check": "reference_integrity",
            "status": "pass" if len(issues) == 0 else "fail",
            "issues_found": len(issues),
            "details": issues,
        }

    def fix_orphaned_records(self, db: Session, table: str, ids: List[int]) -> Dict[str, Any]:
        """
        Fix orphaned records by deleting them

        Args:
            db: Database session
            table: Table name
            ids: List of record IDs to delete

        Returns:
            Dictionary with fix results
        """
        try:
            if table == "salaries":
                db.query(Salary).filter(Salary.id.in_(ids)).delete(synchronize_session=False)
            elif table == "assignments":
                db.query(Assignment).filter(Assignment.id.in_(ids)).delete(
                    synchronize_session=False
                )

            db.commit()

            return {"status": "success", "table": table, "deleted_count": len(ids)}

        except Exception as e:
            db.rollback()
            return {"status": "error", "table": table, "error": str(e)}

    def validate_record(
        self, db: Session, table: str, record_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a record before insertion/update

        Args:
            db: Database session
            table: Table name
            record_data: Record data to validate

        Returns:
            Validation result
        """
        errors = []

        if table == "salary":
            # Validate salary data
            if record_data.get("net_salary", 0) > record_data.get("gross_salary", 0):
                errors.append("Net salary cannot be greater than gross salary")

            if record_data.get("gross_salary", 0) < 0:
                errors.append("Gross salary cannot be negative")

        elif table == "leave":
            # Validate leave data
            start_date = record_data.get("start_date")
            end_date = record_data.get("end_date")

            if start_date and end_date and start_date > end_date:
                errors.append("Start date cannot be after end date")

        elif table == "loan":
            # Validate loan data
            if record_data.get("outstanding_balance", 0) > record_data.get("amount", 0):
                errors.append("Outstanding balance cannot exceed loan amount")

        return {"is_valid": len(errors) == 0, "errors": errors}


# Singleton instance
data_integrity_service = DataIntegrityService()
