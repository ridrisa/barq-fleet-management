"""
Unit Tests for Feedback Service

Tests customer feedback functionality:
- Feedback filtering by category, status, rating
- Positive/negative feedback retrieval
- Response handling
- Statistics calculation
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.support.feedback_service import FeedbackService, feedback_service
from app.models.support import Feedback, FeedbackCategory, FeedbackStatus


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def service():
    """Create FeedbackService instance"""
    return FeedbackService(Feedback)


@pytest.fixture
def sample_feedback():
    """Create a sample feedback"""
    feedback = MagicMock(spec=Feedback)
    feedback.id = 1
    feedback.customer_id = 100
    feedback.category = FeedbackCategory.DELIVERY
    feedback.status = FeedbackStatus.PENDING
    feedback.rating = 5
    feedback.comment = "Great service!"
    feedback.response = None
    feedback.responded_by = None
    return feedback


# ==================== Get by Category Tests ====================

class TestGetByCategory:
    """Tests for get_by_category method"""

    def test_get_by_category(self, service, mock_db, sample_feedback):
        """Should filter by category"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_feedback]

        result = service.get_by_category(
            mock_db,
            category=FeedbackCategory.DELIVERY
        )

        assert len(result) == 1

    def test_get_by_category_empty(self, service, mock_db):
        """Should return empty when no feedback in category"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = service.get_by_category(
            mock_db,
            category=FeedbackCategory.APP
        )

        assert result == []


# ==================== Get by Status Tests ====================

class TestGetByStatus:
    """Tests for get_by_status method"""

    def test_get_by_status_pending(self, service, mock_db, sample_feedback):
        """Should filter by pending status"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_feedback]

        result = service.get_by_status(
            mock_db,
            status=FeedbackStatus.PENDING
        )

        assert len(result) == 1

    def test_get_by_status_completed(self, service, mock_db, sample_feedback):
        """Should filter by completed status"""
        sample_feedback.status = FeedbackStatus.COMPLETED
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_feedback]

        result = service.get_by_status(
            mock_db,
            status=FeedbackStatus.COMPLETED
        )

        assert len(result) == 1


# ==================== Get by Rating Tests ====================

class TestGetByRating:
    """Tests for get_by_rating method"""

    def test_get_by_rating(self, service, mock_db, sample_feedback):
        """Should filter by rating"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_feedback]

        result = service.get_by_rating(mock_db, rating=5)

        assert len(result) == 1

    def test_get_by_rating_one_star(self, service, mock_db, sample_feedback):
        """Should filter by 1 star rating"""
        sample_feedback.rating = 1
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_feedback]

        result = service.get_by_rating(mock_db, rating=1)

        assert len(result) == 1


# ==================== Positive/Negative Feedback Tests ====================

class TestPositiveNegativeFeedback:
    """Tests for positive/negative feedback methods"""

    def test_get_positive_feedback(self, service, mock_db, sample_feedback):
        """Should get feedback with 4-5 stars"""
        sample_feedback.rating = 5
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_feedback]

        result = service.get_positive_feedback(mock_db)

        assert len(result) == 1

    def test_get_negative_feedback(self, service, mock_db, sample_feedback):
        """Should get feedback with 1-2 stars"""
        sample_feedback.rating = 1
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_feedback]

        result = service.get_negative_feedback(mock_db)

        assert len(result) == 1


# ==================== Respond to Feedback Tests ====================

class TestRespondToFeedback:
    """Tests for respond_to_feedback method"""

    def test_respond_success(self, service, mock_db, sample_feedback):
        """Should respond to feedback"""
        with patch.object(service, 'get', return_value=sample_feedback):
            result = service.respond_to_feedback(
                mock_db,
                feedback_id=1,
                response="Thank you for your feedback!",
                responded_by=10,
            )

            assert sample_feedback.response == "Thank you for your feedback!"
            assert sample_feedback.responded_by == 10
            assert sample_feedback.status == FeedbackStatus.COMPLETED

    def test_respond_not_found(self, service, mock_db):
        """Should return None when feedback not found"""
        with patch.object(service, 'get', return_value=None):
            result = service.respond_to_feedback(
                mock_db,
                feedback_id=999,
                response="Response",
                responded_by=10,
            )

            assert result is None


# ==================== Statistics Tests ====================

class TestGetStatistics:
    """Tests for get_statistics method"""

    def test_get_statistics_empty(self, service, mock_db):
        """Should handle empty statistics"""
        mock_db.query.return_value.scalar.return_value = 0
        mock_db.query.return_value.group_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.scalar.return_value = 0

        result = service.get_statistics(mock_db)

        assert result["total"] == 0
        assert result["response_rate"] == 0

    def test_get_statistics_structure(self, service, mock_db):
        """Should return proper statistics structure"""
        # Mock total count
        mock_db.query.return_value.scalar.side_effect = [
            10,    # total
            4.5,   # avg_rating
            8,     # positive_count
            1,     # negative_count
            5,     # responded count
        ]
        mock_db.query.return_value.group_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = []
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [
            4.5, 8, 1, 5
        ]

        result = service.get_statistics(mock_db)

        assert "total" in result
        assert "by_category" in result
        assert "by_status" in result
        assert "by_rating" in result
        assert "average_rating" in result
        assert "positive_count" in result
        assert "negative_count" in result
        assert "response_rate" in result


# ==================== Pagination Tests ====================

class TestPagination:
    """Tests for pagination in all methods"""

    def test_get_by_category_pagination(self, service, mock_db):
        """Should respect pagination in get_by_category"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        service.get_by_category(
            mock_db,
            category=FeedbackCategory.DELIVERY,
            skip=20,
            limit=10
        )

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_with(20)

    def test_get_by_status_pagination(self, service, mock_db):
        """Should respect pagination in get_by_status"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        service.get_by_status(
            mock_db,
            status=FeedbackStatus.PENDING,
            skip=10,
            limit=5
        )

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_with(10)


# ==================== Singleton Tests ====================

class TestSingleton:
    """Tests for singleton instance"""

    def test_feedback_service_exists(self):
        """Should have feedback service singleton"""
        assert feedback_service is not None

    def test_feedback_service_is_instance(self):
        """Should be a FeedbackService instance"""
        assert isinstance(feedback_service, FeedbackService)
