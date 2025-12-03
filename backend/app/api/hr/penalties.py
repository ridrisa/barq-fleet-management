from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


class PenaltyResponse(BaseModel):
    """Penalty response schema"""
    id: int
    courier_id: int
    penalty_type: str
    amount: float
    reason: str
    date: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PenaltyResponse])
def list_penalties(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all penalties - stub implementation"""
    # TODO: Implement actual penalty retrieval
    return []


@router.post("/", response_model=PenaltyResponse, status_code=201)
def create_penalty(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create penalty - stub implementation"""
    # TODO: Implement actual penalty creation
    pass


@router.put("/{penalty_id}", response_model=PenaltyResponse)
def update_penalty(
    penalty_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update penalty - stub implementation"""
    # TODO: Implement actual penalty update
    pass


@router.delete("/{penalty_id}", status_code=204)
def delete_penalty(
    penalty_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete penalty - stub implementation"""
    # TODO: Implement actual penalty deletion
    return None
