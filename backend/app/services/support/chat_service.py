"""Live Chat Service"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime
import secrets

from app.services.base import CRUDBase
from app.models.support import ChatSession, ChatMessage, ChatStatus
from app.schemas.support import ChatSessionCreate, ChatSessionUpdate, ChatMessageCreate


class ChatSessionService(CRUDBase[ChatSession, ChatSessionCreate, ChatSessionUpdate]):
    """Service for chat session operations"""

    def create_session(
        self,
        db: Session,
        *,
        customer_id: int,
        initial_message: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session with unique session ID"""
        session_id = self._generate_session_id()

        session = ChatSession(
            session_id=session_id,
            customer_id=customer_id,
            initial_message=initial_message,
            status=ChatStatus.WAITING
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def assign_agent(
        self,
        db: Session,
        *,
        session_id: int,
        agent_id: int
    ) -> Optional[ChatSession]:
        """Assign chat session to an agent"""
        session = self.get(db, id=session_id)
        if session:
            session.agent_id = agent_id
            session.status = ChatStatus.ACTIVE
            session.started_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session

    def transfer_session(
        self,
        db: Session,
        *,
        session_id: int,
        new_agent_id: int
    ) -> Optional[ChatSession]:
        """Transfer chat session to another agent"""
        session = self.get(db, id=session_id)
        if session:
            old_agent_id = session.agent_id
            session.agent_id = new_agent_id
            session.status = ChatStatus.TRANSFERRED
            db.commit()
            db.refresh(session)
        return session

    def end_session(self, db: Session, *, session_id: int) -> Optional[ChatSession]:
        """End a chat session"""
        session = self.get(db, id=session_id)
        if session:
            session.status = ChatStatus.ENDED
            session.ended_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session

    def get_waiting_sessions(self, db: Session) -> List[ChatSession]:
        """Get all sessions waiting for an agent"""
        return (
            db.query(self.model)
            .filter(self.model.status == ChatStatus.WAITING)
            .order_by(self.model.created_at.asc())
            .all()
        )

    def get_active_sessions(
        self,
        db: Session,
        *,
        agent_id: Optional[int] = None
    ) -> List[ChatSession]:
        """Get active chat sessions"""
        query = db.query(self.model).filter(self.model.status == ChatStatus.ACTIVE)

        if agent_id:
            query = query.filter(self.model.agent_id == agent_id)

        return query.order_by(self.model.started_at.asc()).all()

    def get_by_customer(
        self,
        db: Session,
        *,
        customer_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatSession]:
        """Get chat sessions for a customer"""
        return (
            db.query(self.model)
            .filter(self.model.customer_id == customer_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_agent(
        self,
        db: Session,
        *,
        agent_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatSession]:
        """Get chat sessions handled by an agent"""
        return (
            db.query(self.model)
            .filter(self.model.agent_id == agent_id)
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_suffix = secrets.token_hex(4)
        return f"CHAT-{timestamp}-{random_suffix.upper()}"


class ChatMessageService(CRUDBase[ChatMessage, ChatMessageCreate, None]):
    """Service for chat message operations"""

    def create_message(
        self,
        db: Session,
        *,
        session_id: int,
        sender_id: int,
        message: str,
        is_agent: bool = False,
        is_system: bool = False
    ) -> ChatMessage:
        """Create a new chat message"""
        chat_message = ChatMessage(
            session_id=session_id,
            sender_id=sender_id,
            message=message,
            is_agent=is_agent,
            is_system=is_system
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        return chat_message

    def get_by_session(
        self,
        db: Session,
        *,
        session_id: int,
        skip: int = 0,
        limit: int = 1000
    ) -> List[ChatMessage]:
        """Get all messages for a chat session"""
        return (
            db.query(self.model)
            .filter(self.model.session_id == session_id)
            .order_by(self.model.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_session(self, db: Session, *, session_id: int) -> int:
        """Count messages in a session"""
        return db.query(self.model).filter(self.model.session_id == session_id).count()


# Create service instances
chat_session_service = ChatSessionService(ChatSession)
chat_message_service = ChatMessageService(ChatMessage)
