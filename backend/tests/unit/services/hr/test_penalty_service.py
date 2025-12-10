"""
Unit Tests for Penalty Service

Tests penalty management functionality:
- Reference number generation
- CRUD operations
- Status transitions (approve, reject, appeal)
- Total penalty calculations
"""

import pytest
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

from app.services.hr.penalty_service import PenaltyService, penalty_service
from app.models.hr.penalty import Penalty, PenaltyStatus, PenaltyType


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def service():
    """Create PenaltyService instance"""
    return PenaltyService()


@pytest.fixture
def sample_penalty():
    """Create a sample pending penalty"""
    penalty = MagicMock(spec=Penalty)
    penalty.id = 1
    penalty.courier_id = 100
    penalty.organization_id = 1
    penalty.penalty_type = PenaltyType.LATE_DELIVERY
    penalty.amount = Decimal("100.00")
    penalty.status = PenaltyStatus.PENDING
    penalty.reason = "Late delivery"
    penalty.is_editable = True
    penalty.is_appealable = True
    return penalty


# ==================== Reference Number Tests ====================

class TestGenerateReferenceNumber:
    """Tests for generate_reference_number method"""

    def test_reference_number_format(self, service):
        """Reference number should follow expected format"""
        ref = service.generate_reference_number()

        assert ref.startswith("PEN-")
        assert len(ref) > 10  # Should have timestamp and random suffix

    def test_reference_numbers_unique(self, service):
        """Should generate unique reference numbers"""
        refs = [service.generate_reference_number() for _ in range(100)]
        assert len(refs) == len(set(refs))

    def test_reference_number_contains_timestamp(self, service):
        """Reference number should contain timestamp"""
        ref = service.generate_reference_number()
        parts = ref.split("-")

        # Should have PEN prefix, timestamp, and random suffix
        assert len(parts) >= 3


# ==================== Get Methods Tests ====================

class TestGetMethods:
    """Tests for get methods"""

    def test_get_by_id(self, service, mock_db, sample_penalty):
        """Should retrieve penalty by ID"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_penalty

        result = service.get(mock_db, id=1)

        assert result == sample_penalty

    def test_get_by_id_not_found(self, service, mock_db):
        """Should return None when not found"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = service.get(mock_db, id=999)

        assert result is None

    def test_get_multi_with_filters(self, service, mock_db, sample_penalty):
        """Should filter by multiple criteria"""
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_penalty]

        result = service.get_multi(
            mock_db,
            organization_id=1,
            courier_id=100,
            penalty_type=PenaltyType.LATE_DELIVERY,
            status=PenaltyStatus.PENDING,
        )

        assert len(result) == 1

    def test_get_by_courier(self, service, mock_db, sample_penalty):
        """Should get penalties for specific courier"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_penalty]

        result = service.get_by_courier(
            mock_db,
            courier_id=100,
            organization_id=1,
        )

        assert len(result) == 1
        assert result[0].courier_id == 100

    def test_get_pending(self, service, mock_db, sample_penalty):
        """Should get pending penalties"""
        sample_penalty.status = PenaltyStatus.PENDING
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_penalty]

        result = service.get_pending(mock_db, organization_id=1)

        assert len(result) == 1


# ==================== Create Tests ====================

class TestCreatePenalty:
    """Tests for create method"""

    def test_create_penalty(self, service, mock_db):
        """Should create a new penalty"""
        result = service.create(
            mock_db,
            courier_id=100,
            penalty_type=PenaltyType.LATE_DELIVERY,
            amount=Decimal("100.00"),
            reason="Late delivery",
            organization_id=1,
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_penalty_with_incident_date(self, service, mock_db):
        """Should create penalty with custom incident date"""
        incident_date = datetime(2025, 1, 10)

        service.create(
            mock_db,
            courier_id=100,
            penalty_type=PenaltyType.LATE_DELIVERY,
            amount=Decimal("100.00"),
            reason="Late delivery",
            organization_id=1,
            incident_date=incident_date,
        )

        mock_db.add.assert_called_once()

    def test_create_penalty_with_related_ids(self, service, mock_db):
        """Should create penalty with related IDs"""
        service.create(
            mock_db,
            courier_id=100,
            penalty_type=PenaltyType.SLA_VIOLATION,
            amount=Decimal("50.00"),
            reason="SLA breach",
            organization_id=1,
            incident_id=5,
            delivery_id=10,
            sla_tracking_id=3,
        )

        mock_db.add.assert_called_once()


# ==================== Update Tests ====================

class TestUpdatePenalty:
    """Tests for update method"""

    def test_update_penalty(self, service, mock_db, sample_penalty):
        """Should update editable penalty"""
        result = service.update(
            mock_db,
            penalty=sample_penalty,
            amount=Decimal("150.00"),
            reason="Updated reason",
        )

        assert sample_penalty.amount == Decimal("150.00")
        assert sample_penalty.reason == "Updated reason"
        mock_db.commit.assert_called_once()

    def test_update_non_editable_raises_error(self, service, mock_db, sample_penalty):
        """Should raise error when penalty not editable"""
        sample_penalty.is_editable = False

        with pytest.raises(ValueError, match="Cannot edit penalty"):
            service.update(
                mock_db,
                penalty=sample_penalty,
                amount=Decimal("150.00"),
            )

    def test_update_partial_fields(self, service, mock_db, sample_penalty):
        """Should update only provided fields"""
        original_amount = sample_penalty.amount
        service.update(
            mock_db,
            penalty=sample_penalty,
            reason="New reason only",
        )

        assert sample_penalty.reason == "New reason only"
        assert sample_penalty.amount == original_amount


# ==================== Approve Tests ====================

class TestApprovePenalty:
    """Tests for approve method"""

    def test_approve_pending_penalty(self, service, mock_db, sample_penalty):
        """Should approve pending penalty"""
        result = service.approve(
            mock_db,
            penalty=sample_penalty,
            approved_by_id=10,
        )

        assert sample_penalty.status == PenaltyStatus.APPROVED
        assert sample_penalty.approved_by_id == 10
        assert sample_penalty.approved_at is not None

    def test_approve_non_pending_raises_error(self, service, mock_db, sample_penalty):
        """Should raise error when approving non-pending penalty"""
        sample_penalty.status = PenaltyStatus.APPROVED

        with pytest.raises(ValueError, match="Can only approve pending"):
            service.approve(
                mock_db,
                penalty=sample_penalty,
                approved_by_id=10,
            )


# ==================== Reject Tests ====================

class TestRejectPenalty:
    """Tests for reject method"""

    def test_reject_pending_penalty(self, service, mock_db, sample_penalty):
        """Should reject pending penalty"""
        result = service.reject(
            mock_db,
            penalty=sample_penalty,
            rejected_by_id=10,
        )

        assert sample_penalty.status == PenaltyStatus.REJECTED
        mock_db.commit.assert_called()

    def test_reject_with_reason(self, service, mock_db, sample_penalty):
        """Should include rejection reason in notes"""
        sample_penalty.notes = "Original notes"
        service.reject(
            mock_db,
            penalty=sample_penalty,
            rejected_by_id=10,
            rejection_reason="Insufficient evidence",
        )

        assert "Rejection reason: Insufficient evidence" in sample_penalty.notes

    def test_reject_non_pending_raises_error(self, service, mock_db, sample_penalty):
        """Should raise error when rejecting non-pending penalty"""
        sample_penalty.status = PenaltyStatus.APPROVED

        with pytest.raises(ValueError, match="Can only reject pending"):
            service.reject(
                mock_db,
                penalty=sample_penalty,
                rejected_by_id=10,
            )


# ==================== Appeal Tests ====================

class TestAppealPenalty:
    """Tests for appeal method"""

    def test_appeal_penalty(self, service, mock_db, sample_penalty):
        """Should appeal penalty"""
        result = service.appeal(
            mock_db,
            penalty=sample_penalty,
            appeal_reason="I was stuck in traffic",
        )

        assert sample_penalty.status == PenaltyStatus.APPEALED
        assert sample_penalty.appeal_reason == "I was stuck in traffic"

    def test_appeal_non_appealable_raises_error(self, service, mock_db, sample_penalty):
        """Should raise error when penalty not appealable"""
        sample_penalty.is_appealable = False

        with pytest.raises(ValueError, match="cannot be appealed"):
            service.appeal(
                mock_db,
                penalty=sample_penalty,
                appeal_reason="Reason",
            )


# ==================== Resolve Appeal Tests ====================

class TestResolveAppeal:
    """Tests for resolve_appeal method"""

    def test_resolve_appeal_keep_penalty(self, service, mock_db, sample_penalty):
        """Should resolve appeal and maintain penalty"""
        sample_penalty.status = PenaltyStatus.APPEALED

        result = service.resolve_appeal(
            mock_db,
            penalty=sample_penalty,
            resolution="Appeal rejected",
            waive=False,
            resolved_by_id=10,
        )

        assert sample_penalty.status == PenaltyStatus.APPROVED
        assert sample_penalty.appeal_resolution == "Appeal rejected"

    def test_resolve_appeal_waive_penalty(self, service, mock_db, sample_penalty):
        """Should resolve appeal and waive penalty"""
        sample_penalty.status = PenaltyStatus.APPEALED

        result = service.resolve_appeal(
            mock_db,
            penalty=sample_penalty,
            resolution="Appeal accepted",
            waive=True,
            resolved_by_id=10,
        )

        assert sample_penalty.status == PenaltyStatus.WAIVED

    def test_resolve_non_appealed_raises_error(self, service, mock_db, sample_penalty):
        """Should raise error when resolving non-appealed penalty"""
        sample_penalty.status = PenaltyStatus.PENDING

        with pytest.raises(ValueError, match="Can only resolve appealed"):
            service.resolve_appeal(
                mock_db,
                penalty=sample_penalty,
                resolution="Resolution",
                resolved_by_id=10,
            )


# ==================== Apply to Salary Tests ====================

class TestApplyToSalary:
    """Tests for apply_to_salary method"""

    def test_apply_approved_penalty(self, service, mock_db, sample_penalty):
        """Should apply approved penalty to salary"""
        sample_penalty.status = PenaltyStatus.APPROVED

        result = service.apply_to_salary(
            mock_db,
            penalty=sample_penalty,
            salary_id=50,
        )

        assert sample_penalty.status == PenaltyStatus.APPLIED
        assert sample_penalty.salary_id == 50
        assert sample_penalty.applied_at is not None

    def test_apply_non_approved_raises_error(self, service, mock_db, sample_penalty):
        """Should raise error when applying non-approved penalty"""
        sample_penalty.status = PenaltyStatus.PENDING

        with pytest.raises(ValueError, match="Can only apply approved"):
            service.apply_to_salary(
                mock_db,
                penalty=sample_penalty,
                salary_id=50,
            )


# ==================== Delete Tests ====================

class TestDeletePenalty:
    """Tests for delete method"""

    def test_delete_pending_penalty(self, service, mock_db, sample_penalty):
        """Should delete pending penalty"""
        with patch.object(service, 'get', return_value=sample_penalty):
            result = service.delete(mock_db, id=1)

            assert result is True
            mock_db.delete.assert_called_once()

    def test_delete_not_found(self, service, mock_db):
        """Should return False when penalty not found"""
        with patch.object(service, 'get', return_value=None):
            result = service.delete(mock_db, id=999)

            assert result is False

    def test_delete_non_editable_raises_error(self, service, mock_db, sample_penalty):
        """Should raise error when deleting non-editable penalty"""
        sample_penalty.is_editable = False

        with patch.object(service, 'get', return_value=sample_penalty):
            with pytest.raises(ValueError, match="Cannot delete"):
                service.delete(mock_db, id=1)


# ==================== Total Penalties Tests ====================

class TestGetTotalPenalties:
    """Tests for get_total_penalties_for_courier method"""

    def test_get_total_penalties(self, service, mock_db):
        """Should calculate total penalties"""
        mock_db.query.return_value.filter.return_value.scalar.return_value = Decimal("500.00")

        result = service.get_total_penalties_for_courier(
            mock_db,
            courier_id=100,
            organization_id=1,
        )

        assert result == Decimal("500.00")

    def test_get_total_penalties_empty(self, service, mock_db):
        """Should return zero when no penalties"""
        mock_db.query.return_value.filter.return_value.scalar.return_value = None

        result = service.get_total_penalties_for_courier(
            mock_db,
            courier_id=100,
            organization_id=1,
        )

        assert result == Decimal("0")

    def test_get_total_penalties_by_year_month(self, service, mock_db):
        """Should filter by year and month"""
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.scalar.return_value = Decimal("100.00")

        result = service.get_total_penalties_for_courier(
            mock_db,
            courier_id=100,
            organization_id=1,
            year=2025,
            month=1,
        )

        assert result == Decimal("100.00")


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_singleton_exists(self):
        """Should have a singleton instance"""
        assert penalty_service is not None

    def test_singleton_is_instance(self):
        """Should be a PenaltyService instance"""
        assert isinstance(penalty_service, PenaltyService)
