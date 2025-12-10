"""
Unit Tests for Data Integrity Service

Tests data integrity checking functionality:
- Full integrity check
- Orphaned record detection
- Duplicate detection
- Data consistency validation
- Reference integrity checks
- Record validation
- Fix orphaned records
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock

from app.services.data_integrity_service import DataIntegrityService, data_integrity_service


# ==================== Fixtures ====================

@pytest.fixture
def service():
    """Create DataIntegrityService instance"""
    return DataIntegrityService()


@pytest.fixture
def mock_db():
    """Create mock database session"""
    db = MagicMock()
    db.commit = MagicMock()
    db.rollback = MagicMock()
    return db


# ==================== Full Integrity Check Tests ====================

class TestRunFullIntegrityCheck:
    """Tests for run_full_integrity_check method"""

    def test_returns_complete_structure(self, service, mock_db):
        """Should return complete check structure"""
        with patch.object(service, 'check_orphaned_records', return_value={"check": "orphaned", "issues_found": 0}):
            with patch.object(service, 'check_duplicates', return_value={"check": "duplicates", "issues_found": 0}):
                with patch.object(service, 'check_data_consistency', return_value={"check": "consistency", "issues_found": 0}):
                    with patch.object(service, 'check_reference_integrity', return_value={"check": "reference", "issues_found": 0}):
                        result = service.run_full_integrity_check(mock_db)

        assert "timestamp" in result
        assert "checks" in result
        assert "summary" in result
        assert "orphaned_records" in result["checks"]
        assert "duplicates" in result["checks"]
        assert "consistency" in result["checks"]
        assert "reference_integrity" in result["checks"]

    def test_healthy_status_when_no_issues(self, service, mock_db):
        """Should return healthy status when no issues found"""
        with patch.object(service, 'check_orphaned_records', return_value={"issues_found": 0}):
            with patch.object(service, 'check_duplicates', return_value={"issues_found": 0}):
                with patch.object(service, 'check_data_consistency', return_value={"issues_found": 0}):
                    with patch.object(service, 'check_reference_integrity', return_value={"issues_found": 0}):
                        result = service.run_full_integrity_check(mock_db)

        assert result["summary"]["status"] == "healthy"
        assert result["summary"]["total_issues"] == 0

    def test_issues_found_status_when_problems(self, service, mock_db):
        """Should return issues_found status when problems exist"""
        with patch.object(service, 'check_orphaned_records', return_value={"issues_found": 2}):
            with patch.object(service, 'check_duplicates', return_value={"issues_found": 1}):
                with patch.object(service, 'check_data_consistency', return_value={"issues_found": 0}):
                    with patch.object(service, 'check_reference_integrity', return_value={"issues_found": 3}):
                        result = service.run_full_integrity_check(mock_db)

        assert result["summary"]["status"] == "issues_found"
        assert result["summary"]["total_issues"] == 6

    def test_includes_timestamp(self, service, mock_db):
        """Should include ISO format timestamp"""
        with patch.object(service, 'check_orphaned_records', return_value={"issues_found": 0}):
            with patch.object(service, 'check_duplicates', return_value={"issues_found": 0}):
                with patch.object(service, 'check_data_consistency', return_value={"issues_found": 0}):
                    with patch.object(service, 'check_reference_integrity', return_value={"issues_found": 0}):
                        result = service.run_full_integrity_check(mock_db)

        # Should be valid ISO format timestamp
        assert "T" in result["timestamp"]


# ==================== Orphaned Records Tests ====================

class TestCheckOrphanedRecords:
    """Tests for check_orphaned_records method"""

    def test_pass_when_no_orphans(self, service, mock_db):
        """Should pass when no orphaned records"""
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.count.return_value = 0

        result = service.check_orphaned_records(mock_db)

        assert result["status"] == "pass"
        assert result["issues_found"] == 0
        assert result["details"] == []

    def test_fail_with_orphaned_salaries(self, service, mock_db):
        """Should fail when orphaned salary records exist"""
        # First query returns orphaned salaries
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.count.side_effect = [5, 0, 0]

        result = service.check_orphaned_records(mock_db)

        assert result["status"] == "fail"
        assert result["issues_found"] >= 1
        assert any("salaries" in d.get("table", "") for d in result["details"])

    def test_fail_with_orphaned_assignments_courier(self, service, mock_db):
        """Should detect assignments without courier"""
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.count.side_effect = [0, 3, 0]

        result = service.check_orphaned_records(mock_db)

        assert result["status"] == "fail"
        assert any(d.get("issue") == "orphaned_courier" for d in result["details"])

    def test_fail_with_orphaned_assignments_vehicle(self, service, mock_db):
        """Should detect assignments without vehicle"""
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.count.side_effect = [0, 0, 2]

        result = service.check_orphaned_records(mock_db)

        assert result["status"] == "fail"
        assert any(d.get("issue") == "orphaned_vehicle" for d in result["details"])

    def test_details_include_count(self, service, mock_db):
        """Should include count of orphaned records"""
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.count.side_effect = [10, 0, 0]

        result = service.check_orphaned_records(mock_db)

        assert result["details"][0]["count"] == 10


# ==================== Duplicates Tests ====================

class TestCheckDuplicates:
    """Tests for check_duplicates method"""

    def test_pass_when_no_duplicates(self, service, mock_db):
        """Should pass when no duplicates"""
        mock_db.query.return_value.group_by.return_value.having.return_value.all.return_value = []

        result = service.check_duplicates(mock_db)

        assert result["status"] == "pass"
        assert result["issues_found"] == 0

    def test_fail_with_duplicate_employee_ids(self, service, mock_db):
        """Should fail with duplicate employee IDs"""
        mock_db.query.return_value.group_by.return_value.having.return_value.all.side_effect = [
            [("EMP001", 2), ("EMP002", 3)],  # Duplicate employee IDs
            [],  # No duplicate plates
        ]

        result = service.check_duplicates(mock_db)

        assert result["status"] == "fail"
        assert any(d.get("issue") == "duplicate_employee_ids" for d in result["details"])

    def test_fail_with_duplicate_license_plates(self, service, mock_db):
        """Should fail with duplicate license plates"""
        mock_db.query.return_value.group_by.return_value.having.return_value.all.side_effect = [
            [],  # No duplicate employee IDs
            [("ABC-123", 2)],  # Duplicate plates
        ]

        result = service.check_duplicates(mock_db)

        assert result["status"] == "fail"
        assert any(d.get("issue") == "duplicate_license_plates" for d in result["details"])

    def test_includes_examples(self, service, mock_db):
        """Should include examples of duplicates"""
        mock_db.query.return_value.group_by.return_value.having.return_value.all.side_effect = [
            [("EMP001", 2)],
            [],
        ]

        result = service.check_duplicates(mock_db)

        assert "examples" in result["details"][0]
        assert result["details"][0]["examples"][0]["employee_id"] == "EMP001"


# ==================== Data Consistency Tests ====================

class TestCheckDataConsistency:
    """Tests for check_data_consistency method"""

    def test_pass_when_consistent(self, service, mock_db):
        """Should pass when data is consistent"""
        mock_db.query.return_value.filter.return_value.count.return_value = 0

        result = service.check_data_consistency(mock_db)

        assert result["status"] == "pass"
        assert result["issues_found"] == 0

    def test_fail_net_greater_than_gross(self, service, mock_db):
        """Should fail when net salary > gross salary"""
        mock_db.query.return_value.filter.return_value.count.side_effect = [5, 0, 0, 0]

        result = service.check_data_consistency(mock_db)

        assert result["status"] == "fail"
        assert any(d.get("issue") == "net_greater_than_gross" for d in result["details"])

    def test_fail_invalid_leave_dates(self, service, mock_db):
        """Should fail when leave start_date > end_date"""
        mock_db.query.return_value.filter.return_value.count.side_effect = [0, 3, 0, 0]

        result = service.check_data_consistency(mock_db)

        assert result["status"] == "fail"
        assert any(d.get("issue") == "invalid_date_range" for d in result["details"])

    def test_fail_invalid_loan_balance(self, service, mock_db):
        """Should fail when outstanding > loan amount"""
        mock_db.query.return_value.filter.return_value.count.side_effect = [0, 0, 2, 0]

        result = service.check_data_consistency(mock_db)

        assert result["status"] == "fail"
        assert any(d.get("issue") == "invalid_balance" for d in result["details"])

    def test_fail_invalid_assignment_dates(self, service, mock_db):
        """Should fail when assignment start_date > end_date"""
        mock_db.query.return_value.filter.return_value.count.side_effect = [0, 0, 0, 1]

        result = service.check_data_consistency(mock_db)

        assert result["status"] == "fail"
        assert any("assignment" in d.get("table", "") for d in result["details"])


# ==================== Reference Integrity Tests ====================

class TestCheckReferenceIntegrity:
    """Tests for check_reference_integrity method"""

    def test_pass_no_overlapping_assignments(self, service, mock_db):
        """Should pass with no overlapping assignments"""
        mock_db.execute.return_value.fetchall.return_value = []

        result = service.check_reference_integrity(mock_db)

        assert result["status"] == "pass"
        assert result["issues_found"] == 0

    def test_fail_overlapping_assignments(self, service, mock_db):
        """Should fail with overlapping vehicle assignments"""
        mock_db.execute.return_value.fetchall.return_value = [
            (1, 3),  # Vehicle 1 has 3 overlaps
            (2, 2),  # Vehicle 2 has 2 overlaps
        ]

        result = service.check_reference_integrity(mock_db)

        assert result["status"] == "fail"
        assert result["issues_found"] >= 1
        assert any(d.get("issue") == "overlapping_assignments" for d in result["details"])

    def test_includes_overlap_examples(self, service, mock_db):
        """Should include examples of overlaps"""
        mock_db.execute.return_value.fetchall.return_value = [(10, 5)]

        result = service.check_reference_integrity(mock_db)

        assert "examples" in result["details"][0]


# ==================== Fix Orphaned Records Tests ====================

class TestFixOrphanedRecords:
    """Tests for fix_orphaned_records method"""

    def test_fix_salaries_success(self, service, mock_db):
        """Should delete orphaned salary records"""
        mock_db.query.return_value.filter.return_value.delete.return_value = None

        result = service.fix_orphaned_records(mock_db, "salaries", [1, 2, 3])

        assert result["status"] == "success"
        assert result["table"] == "salaries"
        assert result["deleted_count"] == 3
        mock_db.commit.assert_called_once()

    def test_fix_assignments_success(self, service, mock_db):
        """Should delete orphaned assignment records"""
        mock_db.query.return_value.filter.return_value.delete.return_value = None

        result = service.fix_orphaned_records(mock_db, "assignments", [4, 5])

        assert result["status"] == "success"
        assert result["table"] == "assignments"
        assert result["deleted_count"] == 2

    def test_fix_error_rollback(self, service, mock_db):
        """Should rollback on error"""
        mock_db.query.return_value.filter.return_value.delete.side_effect = Exception("Database error")

        result = service.fix_orphaned_records(mock_db, "salaries", [1])

        assert result["status"] == "error"
        assert "error" in result
        mock_db.rollback.assert_called_once()


# ==================== Validate Record Tests ====================

class TestValidateRecord:
    """Tests for validate_record method"""

    def test_valid_salary_record(self, service, mock_db):
        """Should validate correct salary record"""
        record_data = {
            "gross_salary": 10000,
            "net_salary": 8000,
        }

        result = service.validate_record(mock_db, "salary", record_data)

        assert result["is_valid"] is True
        assert result["errors"] == []

    def test_invalid_salary_net_greater_gross(self, service, mock_db):
        """Should reject salary where net > gross"""
        record_data = {
            "gross_salary": 5000,
            "net_salary": 6000,
        }

        result = service.validate_record(mock_db, "salary", record_data)

        assert result["is_valid"] is False
        assert "Net salary cannot be greater than gross salary" in result["errors"]

    def test_invalid_salary_negative_gross(self, service, mock_db):
        """Should reject negative gross salary"""
        record_data = {
            "gross_salary": -5000,
            "net_salary": -6000,
        }

        result = service.validate_record(mock_db, "salary", record_data)

        assert result["is_valid"] is False
        assert "Gross salary cannot be negative" in result["errors"]

    def test_valid_leave_record(self, service, mock_db):
        """Should validate correct leave record"""
        record_data = {
            "start_date": date(2025, 1, 1),
            "end_date": date(2025, 1, 10),
        }

        result = service.validate_record(mock_db, "leave", record_data)

        assert result["is_valid"] is True

    def test_invalid_leave_dates(self, service, mock_db):
        """Should reject leave where start > end"""
        record_data = {
            "start_date": date(2025, 1, 10),
            "end_date": date(2025, 1, 1),
        }

        result = service.validate_record(mock_db, "leave", record_data)

        assert result["is_valid"] is False
        assert "Start date cannot be after end date" in result["errors"]

    def test_valid_loan_record(self, service, mock_db):
        """Should validate correct loan record"""
        record_data = {
            "amount": 10000,
            "outstanding_balance": 5000,
        }

        result = service.validate_record(mock_db, "loan", record_data)

        assert result["is_valid"] is True

    def test_invalid_loan_balance(self, service, mock_db):
        """Should reject loan where outstanding > amount"""
        record_data = {
            "amount": 5000,
            "outstanding_balance": 6000,
        }

        result = service.validate_record(mock_db, "loan", record_data)

        assert result["is_valid"] is False
        assert "Outstanding balance cannot exceed loan amount" in result["errors"]

    def test_unknown_table_passes(self, service, mock_db):
        """Should pass validation for unknown table"""
        result = service.validate_record(mock_db, "unknown_table", {})

        assert result["is_valid"] is True


# ==================== Check Structure Tests ====================

class TestCheckStructure:
    """Tests for check result structure"""

    def test_orphaned_records_structure(self, service, mock_db):
        """Should return standard check structure"""
        mock_db.query.return_value.outerjoin.return_value.filter.return_value.count.return_value = 0

        result = service.check_orphaned_records(mock_db)

        assert "check" in result
        assert "status" in result
        assert "issues_found" in result
        assert "details" in result
        assert result["check"] == "orphaned_records"

    def test_duplicates_structure(self, service, mock_db):
        """Should return standard check structure"""
        mock_db.query.return_value.group_by.return_value.having.return_value.all.return_value = []

        result = service.check_duplicates(mock_db)

        assert result["check"] == "duplicates"

    def test_consistency_structure(self, service, mock_db):
        """Should return standard check structure"""
        mock_db.query.return_value.filter.return_value.count.return_value = 0

        result = service.check_data_consistency(mock_db)

        assert result["check"] == "data_consistency"

    def test_reference_integrity_structure(self, service, mock_db):
        """Should return standard check structure"""
        mock_db.execute.return_value.fetchall.return_value = []

        result = service.check_reference_integrity(mock_db)

        assert result["check"] == "reference_integrity"


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have a singleton instance"""
        assert data_integrity_service is not None

    def test_singleton_is_instance(self):
        """Should be a DataIntegrityService instance"""
        assert isinstance(data_integrity_service, DataIntegrityService)
