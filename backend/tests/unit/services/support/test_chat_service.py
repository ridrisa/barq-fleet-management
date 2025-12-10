"""
Unit Tests for Chat Service

Tests chat functionality:
- Chat session management
- Message handling
- Agent assignment and transfer
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from app.services.support.chat_service import (
    ChatSessionService,
    ChatMessageService,
    chat_session_service,
    chat_message_service,
)
from app.models.support import ChatSession, ChatMessage, ChatStatus


# ==================== Fixtures ====================

@pytest.fixture
def mock_db():
    """Create a mock database session"""
    return MagicMock()


@pytest.fixture
def session_service():
    """Create ChatSessionService instance"""
    return ChatSessionService(ChatSession)


@pytest.fixture
def message_service():
    """Create ChatMessageService instance"""
    return ChatMessageService(ChatMessage)


@pytest.fixture
def sample_session():
    """Create a sample chat session"""
    session = MagicMock(spec=ChatSession)
    session.id = 1
    session.session_id = "CHAT-20250115120000-ABCD1234"
    session.customer_id = 100
    session.agent_id = None
    session.status = ChatStatus.WAITING
    session.initial_message = "Hello, I need help"
    session.created_at = datetime.utcnow()
    return session


@pytest.fixture
def sample_message():
    """Create a sample chat message"""
    message = MagicMock(spec=ChatMessage)
    message.id = 1
    message.session_id = 1
    message.sender_id = 100
    message.message = "Hello"
    message.is_agent = False
    message.is_system = False
    return message


# ==================== Session ID Generation Tests ====================

class TestSessionIdGeneration:
    """Tests for session ID generation"""

    def test_generate_session_id_format(self, session_service):
        """Session ID should follow expected format"""
        session_id = session_service._generate_session_id()

        assert session_id.startswith("CHAT-")
        parts = session_id.split("-")
        assert len(parts) >= 3

    def test_generate_unique_session_ids(self, session_service):
        """Should generate unique session IDs"""
        ids = [session_service._generate_session_id() for _ in range(100)]
        assert len(ids) == len(set(ids))


# ==================== Create Session Tests ====================

class TestCreateSession:
    """Tests for create_session method"""

    def test_create_session_basic(self, session_service, mock_db):
        """Should create a new chat session"""
        result = session_service.create_session(
            mock_db,
            customer_id=100,
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_session_with_message(self, session_service, mock_db):
        """Should create session with initial message"""
        session_service.create_session(
            mock_db,
            customer_id=100,
            initial_message="I need help with my order",
        )

        mock_db.add.assert_called_once()


# ==================== Assign Agent Tests ====================

class TestAssignAgent:
    """Tests for assign_agent method"""

    def test_assign_agent_success(self, session_service, mock_db, sample_session):
        """Should assign agent to session"""
        with patch.object(session_service, 'get', return_value=sample_session):
            result = session_service.assign_agent(
                mock_db,
                session_id=1,
                agent_id=50,
            )

            assert sample_session.agent_id == 50
            assert sample_session.status == ChatStatus.ACTIVE
            assert sample_session.started_at is not None

    def test_assign_agent_not_found(self, session_service, mock_db):
        """Should return None when session not found"""
        with patch.object(session_service, 'get', return_value=None):
            result = session_service.assign_agent(
                mock_db,
                session_id=999,
                agent_id=50,
            )

            assert result is None


# ==================== Transfer Session Tests ====================

class TestTransferSession:
    """Tests for transfer_session method"""

    def test_transfer_session_success(self, session_service, mock_db, sample_session):
        """Should transfer session to new agent"""
        sample_session.agent_id = 50

        with patch.object(session_service, 'get', return_value=sample_session):
            result = session_service.transfer_session(
                mock_db,
                session_id=1,
                new_agent_id=60,
            )

            assert sample_session.agent_id == 60
            assert sample_session.status == ChatStatus.TRANSFERRED

    def test_transfer_session_not_found(self, session_service, mock_db):
        """Should return None when session not found"""
        with patch.object(session_service, 'get', return_value=None):
            result = session_service.transfer_session(
                mock_db,
                session_id=999,
                new_agent_id=60,
            )

            assert result is None


# ==================== End Session Tests ====================

class TestEndSession:
    """Tests for end_session method"""

    def test_end_session_success(self, session_service, mock_db, sample_session):
        """Should end chat session"""
        with patch.object(session_service, 'get', return_value=sample_session):
            result = session_service.end_session(mock_db, session_id=1)

            assert sample_session.status == ChatStatus.ENDED
            assert sample_session.ended_at is not None

    def test_end_session_not_found(self, session_service, mock_db):
        """Should return None when session not found"""
        with patch.object(session_service, 'get', return_value=None):
            result = session_service.end_session(mock_db, session_id=999)

            assert result is None


# ==================== Get Sessions Tests ====================

class TestGetSessions:
    """Tests for session query methods"""

    def test_get_waiting_sessions(self, session_service, mock_db, sample_session):
        """Should get sessions waiting for agent"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [sample_session]

        result = session_service.get_waiting_sessions(mock_db)

        assert len(result) == 1

    def test_get_active_sessions(self, session_service, mock_db, sample_session):
        """Should get active sessions"""
        sample_session.status = ChatStatus.ACTIVE
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [sample_session]

        result = session_service.get_active_sessions(mock_db)

        assert len(result) == 1

    def test_get_active_sessions_by_agent(self, session_service, mock_db, sample_session):
        """Should filter by agent ID"""
        mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [sample_session]

        result = session_service.get_active_sessions(mock_db, agent_id=50)

        assert len(result) == 1

    def test_get_by_customer(self, session_service, mock_db, sample_session):
        """Should get sessions by customer"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_session]

        result = session_service.get_by_customer(mock_db, customer_id=100)

        assert len(result) == 1

    def test_get_by_agent(self, session_service, mock_db, sample_session):
        """Should get sessions by agent"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_session]

        result = session_service.get_by_agent(mock_db, agent_id=50)

        assert len(result) == 1


# ==================== Chat Message Tests ====================

class TestChatMessageService:
    """Tests for ChatMessageService"""

    def test_create_message(self, message_service, mock_db):
        """Should create a new message"""
        result = message_service.create_message(
            mock_db,
            session_id=1,
            sender_id=100,
            message="Hello, I need help",
        )

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_agent_message(self, message_service, mock_db):
        """Should create agent message"""
        message_service.create_message(
            mock_db,
            session_id=1,
            sender_id=50,
            message="How can I help you?",
            is_agent=True,
        )

        mock_db.add.assert_called_once()

    def test_create_system_message(self, message_service, mock_db):
        """Should create system message"""
        message_service.create_message(
            mock_db,
            session_id=1,
            sender_id=0,
            message="Agent has joined the chat",
            is_system=True,
        )

        mock_db.add.assert_called_once()

    def test_get_by_session(self, message_service, mock_db, sample_message):
        """Should get messages by session"""
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [sample_message]

        result = message_service.get_by_session(mock_db, session_id=1)

        assert len(result) == 1

    def test_count_by_session(self, message_service, mock_db):
        """Should count messages in session"""
        mock_db.query.return_value.filter.return_value.count.return_value = 15

        result = message_service.count_by_session(mock_db, session_id=1)

        assert result == 15


# ==================== Singleton Tests ====================

class TestSingletons:
    """Tests for singleton instances"""

    def test_chat_session_service_exists(self):
        """Should have chat session service singleton"""
        assert chat_session_service is not None

    def test_chat_message_service_exists(self):
        """Should have chat message service singleton"""
        assert chat_message_service is not None
