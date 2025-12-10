"""
Unit Tests for Knowledge Service

Tests knowledge base functionality:
- FAQ management
- Knowledge base article management
- Search and filtering
"""

import pytest
from unittest.mock import MagicMock, patch

from app.services.support.knowledge_service import (
    FAQService,
    KBArticleService,
    faq_service,
    kb_article_service,
)
from app.models.support import FAQ, KBArticle, ArticleStatus


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def faq_svc():
    """Create FAQService instance"""
    return FAQService(FAQ)


@pytest.fixture
def article_svc():
    """Create KBArticleService instance"""
    return KBArticleService(KBArticle)


@pytest.fixture
def sample_faq():
    """Create a sample FAQ"""
    faq = MagicMock(spec=FAQ)
    faq.id = 1
    faq.question = "How to reset password?"
    faq.answer = "Click the forgot password link"
    faq.category = "account"
    faq.is_active = True
    faq.order = 1
    faq.view_count = 100
    return faq


@pytest.fixture
def sample_article():
    """Create a sample KB article"""
    article = MagicMock(spec=KBArticle)
    article.id = 1
    article.title = "Getting Started Guide"
    article.slug = "getting-started-guide"
    article.content = "Welcome to our platform..."
    article.category = "guides"
    article.status = ArticleStatus.PUBLISHED
    article.view_count = 500
    article.helpful_count = 45
    article.not_helpful_count = 5
    article.version = 1
    return article


# ==================== FAQ Get Active Tests ====================

class TestFAQGetActive:
    """Tests for FAQ get_active method"""

    def test_get_active_faqs(self, faq_svc, mock_db, sample_faq):
        """Should return active FAQs only"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_faq]

        result = faq_svc.get_active(mock_db)

        assert len(result) == 1
        assert result[0].is_active is True

    def test_get_active_faqs_pagination(self, faq_svc, mock_db, sample_faq):
        """Should respect pagination parameters"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_faq]

        faq_svc.get_active(mock_db, skip=10, limit=5)

        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.assert_called_once_with(10)


# ==================== FAQ Get by Category Tests ====================

class TestFAQGetByCategory:
    """Tests for FAQ get_by_category method"""

    def test_get_by_category(self, faq_svc, mock_db, sample_faq):
        """Should filter by category"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_faq]

        result = faq_svc.get_by_category(mock_db, category="account")

        assert len(result) == 1


# ==================== FAQ Search Tests ====================

class TestFAQSearch:
    """Tests for FAQ search method"""

    def test_search_faqs(self, faq_svc, mock_db, sample_faq):
        """Should search FAQs by question or answer"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_faq]

        result = faq_svc.search(mock_db, query="password")

        assert len(result) == 1

    def test_search_faqs_empty(self, faq_svc, mock_db):
        """Should return empty for no matches"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        result = faq_svc.search(mock_db, query="nonexistent")

        assert result == []


# ==================== FAQ View Count Tests ====================

class TestFAQViewCount:
    """Tests for FAQ view count methods"""

    def test_increment_view_count(self, faq_svc, mock_db, sample_faq):
        """Should increment FAQ view count"""
        sample_faq.view_count = 100
        with patch.object(faq_svc, 'get', return_value=sample_faq):
            result = faq_svc.increment_view_count(mock_db, faq_id=1)

            assert sample_faq.view_count == 101

    def test_increment_view_count_not_found(self, faq_svc, mock_db):
        """Should return None when FAQ not found"""
        with patch.object(faq_svc, 'get', return_value=None):
            result = faq_svc.increment_view_count(mock_db, faq_id=999)

            assert result is None


# ==================== FAQ Categories Tests ====================

class TestFAQCategories:
    """Tests for FAQ category methods"""

    def test_get_categories(self, faq_svc, mock_db):
        """Should return categories with counts"""
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = [
            ("account", 5),
            ("delivery", 10),
        ]

        result = faq_svc.get_categories(mock_db)

        assert result["account"] == 5
        assert result["delivery"] == 10


# ==================== FAQ Reorder Tests ====================

class TestFAQReorder:
    """Tests for FAQ reorder method"""

    def test_reorder_faq(self, faq_svc, mock_db, sample_faq):
        """Should update FAQ order"""
        sample_faq.order = 1
        with patch.object(faq_svc, 'get', return_value=sample_faq):
            result = faq_svc.reorder(mock_db, faq_id=1, new_order=5)

            assert sample_faq.order == 5


# ==================== FAQ Top Viewed Tests ====================

class TestFAQTopViewed:
    """Tests for FAQ get_top_viewed method"""

    def test_get_top_viewed(self, faq_svc, mock_db, sample_faq):
        """Should return top viewed FAQs"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [sample_faq]

        result = faq_svc.get_top_viewed(mock_db, limit=10)

        assert len(result) == 1


# ==================== KB Article Get by Slug Tests ====================

class TestKBArticleGetBySlug:
    """Tests for KB article get_by_slug method"""

    def test_get_by_slug(self, article_svc, mock_db, sample_article):
        """Should get article by slug"""
        mock_db.query.return_value.filter.return_value.first.return_value = sample_article

        result = article_svc.get_by_slug(mock_db, slug="getting-started-guide")

        assert result.slug == "getting-started-guide"

    def test_get_by_slug_not_found(self, article_svc, mock_db):
        """Should return None when slug not found"""
        mock_db.query.return_value.filter.return_value.first.return_value = None

        result = article_svc.get_by_slug(mock_db, slug="nonexistent")

        assert result is None


# ==================== KB Article Get Published Tests ====================

class TestKBArticleGetPublished:
    """Tests for KB article get_published method"""

    def test_get_published(self, article_svc, mock_db, sample_article):
        """Should return published articles only"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_article]

        result = article_svc.get_published(mock_db)

        assert len(result) == 1


# ==================== KB Article Search Tests ====================

class TestKBArticleSearch:
    """Tests for KB article search method"""

    def test_search_articles(self, article_svc, mock_db, sample_article):
        """Should search articles"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_article]

        result = article_svc.search(mock_db, query="getting started")

        assert len(result) == 1


# ==================== KB Article View Count Tests ====================

class TestKBArticleViewCount:
    """Tests for KB article view count methods"""

    def test_increment_view_count(self, article_svc, mock_db, sample_article):
        """Should increment article view count"""
        sample_article.view_count = 500
        with patch.object(article_svc, 'get', return_value=sample_article):
            result = article_svc.increment_view_count(mock_db, article_id=1)

            assert sample_article.view_count == 501


# ==================== KB Article Voting Tests ====================

class TestKBArticleVoting:
    """Tests for KB article voting methods"""

    def test_vote_helpful(self, article_svc, mock_db, sample_article):
        """Should increment helpful count"""
        sample_article.helpful_count = 45
        with patch.object(article_svc, 'get', return_value=sample_article):
            result = article_svc.vote_helpful(mock_db, article_id=1, helpful=True)

            assert sample_article.helpful_count == 46

    def test_vote_not_helpful(self, article_svc, mock_db, sample_article):
        """Should increment not helpful count"""
        sample_article.not_helpful_count = 5
        with patch.object(article_svc, 'get', return_value=sample_article):
            result = article_svc.vote_helpful(mock_db, article_id=1, helpful=False)

            assert sample_article.not_helpful_count == 6


# ==================== KB Article Publish Tests ====================

class TestKBArticlePublish:
    """Tests for KB article publish/unpublish methods"""

    def test_publish_article(self, article_svc, mock_db, sample_article):
        """Should publish article"""
        sample_article.status = ArticleStatus.DRAFT
        sample_article.version = 1
        with patch.object(article_svc, 'get', return_value=sample_article):
            result = article_svc.publish(mock_db, article_id=1)

            assert sample_article.status == ArticleStatus.PUBLISHED
            assert sample_article.version == 2

    def test_unpublish_article(self, article_svc, mock_db, sample_article):
        """Should unpublish article"""
        sample_article.status = ArticleStatus.PUBLISHED
        with patch.object(article_svc, 'get', return_value=sample_article):
            result = article_svc.unpublish(mock_db, article_id=1)

            assert sample_article.status == ArticleStatus.DRAFT


# ==================== KB Article Categories Tests ====================

class TestKBArticleCategories:
    """Tests for KB article category methods"""

    def test_get_categories(self, article_svc, mock_db):
        """Should return unique categories"""
        mock_db.query.return_value.filter.return_value.distinct.return_value.all.return_value = [
            ("guides",),
            ("tutorials",),
        ]

        result = article_svc.get_categories(mock_db)

        assert "guides" in result
        assert "tutorials" in result


# ==================== KB Article Top Articles Tests ====================

class TestKBArticleTopArticles:
    """Tests for KB article get_top_articles method"""

    def test_get_top_articles(self, article_svc, mock_db, sample_article):
        """Should return top viewed articles"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [sample_article]

        result = article_svc.get_top_articles(mock_db, limit=10)

        assert len(result) == 1


# ==================== Singleton Tests ====================

class TestSingletons:
    """Tests for singleton instances"""

    def test_faq_service_exists(self):
        """Should have FAQ service singleton"""
        assert faq_service is not None

    def test_kb_article_service_exists(self):
        """Should have KB article service singleton"""
        assert kb_article_service is not None
