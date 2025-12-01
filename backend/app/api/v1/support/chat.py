"""Live Chat API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.support import ChatStatus
from app.schemas.support import (
    ChatSessionCreate, ChatSessionUpdate, ChatSessionResponse,
    ChatSessionList, ChatSessionAssign, ChatSessionTransfer,
    ChatMessageCreate, ChatMessageResponse, ChatTranscript
)
from app.services.support import chat_session_service, chat_message_service


router = APIRouter()


@router.get("/sessions", response_model=List[ChatSessionList])
def get_chat_sessions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[ChatStatus] = Query(None, alias="status"),
    agent_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of chat sessions

    Filters:
    - status: Filter by chat status
    - agent_id: Filter by assigned agent
    """
    if status_filter == ChatStatus.ACTIVE:
        return chat_session_service.get_active_sessions(db, agent_id=agent_id)

    if status_filter == ChatStatus.WAITING:
        return chat_session_service.get_waiting_sessions(db)

    if agent_id:
        return chat_session_service.get_by_agent(
            db,
            agent_id=agent_id,
            skip=skip,
            limit=limit
        )

    return chat_session_service.get_multi(db, skip=skip, limit=limit)


@router.post("/sessions", response_model=ChatSessionResponse, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    session_in: ChatSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new chat session (customer initiates chat)"""
    return chat_session_service.create_session(
        db,
        customer_id=current_user.id,
        initial_message=session_in.initial_message
    )


@router.get("/sessions/waiting", response_model=List[ChatSessionList])
def get_waiting_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat sessions waiting for an agent"""
    return chat_session_service.get_waiting_sessions(db)


@router.get("/sessions/my-chats", response_model=List[ChatSessionList])
def get_my_chat_sessions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get chat sessions for current user (as customer)"""
    return chat_session_service.get_by_customer(
        db,
        customer_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get("/sessions/assigned-to-me", response_model=List[ChatSessionList])
def get_assigned_chat_sessions(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get chat sessions assigned to current user (as agent)"""
    return chat_session_service.get_by_agent(
        db,
        agent_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat session by ID"""
    session = chat_session_service.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return session


@router.put("/sessions/{session_id}", response_model=ChatSessionResponse)
def update_chat_session(
    session_id: int,
    session_in: ChatSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update chat session"""
    session = chat_session_service.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return chat_session_service.update(db, db_obj=session, obj_in=session_in)


@router.post("/sessions/{session_id}/assign", response_model=ChatSessionResponse)
def assign_chat_session(
    session_id: int,
    assign_data: ChatSessionAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assign chat session to an agent"""
    session = chat_session_service.assign_agent(
        db,
        session_id=session_id,
        agent_id=assign_data.agent_id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return session


@router.post("/sessions/{session_id}/transfer", response_model=ChatSessionResponse)
def transfer_chat_session(
    session_id: int,
    transfer_data: ChatSessionTransfer,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Transfer chat session to another agent"""
    session = chat_session_service.transfer_session(
        db,
        session_id=session_id,
        new_agent_id=transfer_data.new_agent_id
    )
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return session


@router.post("/sessions/{session_id}/end", response_model=ChatSessionResponse)
def end_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """End chat session"""
    session = chat_session_service.end_session(db, session_id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    return session


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=5000),
    current_user: User = Depends(get_current_user),
):
    """Get all messages for a chat session"""
    session = chat_session_service.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    return chat_message_service.get_by_session(
        db,
        session_id=session_id,
        skip=skip,
        limit=limit
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def send_chat_message(
    session_id: int,
    message_in: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message in a chat session"""
    session = chat_session_service.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    # Determine if user is agent or customer
    is_agent = session.agent_id == current_user.id

    return chat_message_service.create_message(
        db,
        session_id=session_id,
        sender_id=current_user.id,
        message=message_in.message,
        is_agent=is_agent,
        is_system=False
    )


@router.get("/sessions/{session_id}/transcript")
def get_chat_transcript(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get chat transcript for download"""
    session = chat_session_service.get(db, id=session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    messages = chat_message_service.get_by_session(db, session_id=session_id)

    # Calculate duration
    duration_minutes = None
    if session.started_at and session.ended_at:
        duration_seconds = (session.ended_at - session.started_at).total_seconds()
        duration_minutes = int(duration_seconds / 60)

    return {
        "session_id": session.session_id,
        "customer_name": f"Customer {session.customer_id}",  # TODO: Get actual name
        "agent_name": f"Agent {session.agent_id}" if session.agent_id else None,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
        "duration_minutes": duration_minutes,
        "messages": messages
    }


# WebSocket endpoint for real-time chat (optional - basic implementation)
@router.websocket("/ws/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: int,
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time chat

    Note: This is a basic implementation. For production,
    consider using Redis pub/sub or a message broker
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            # Echo back (in production, save to DB and broadcast to other participants)
            await websocket.send_text(f"Message received: {data}")

    except WebSocketDisconnect:
        # Handle disconnect
        pass
