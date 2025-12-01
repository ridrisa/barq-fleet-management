from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.config.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


class BudgetResponse(BaseModel):
    """Budget response schema"""
    id: int
    amount: float
    category: str
    period: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all budgets - stub implementation"""
    return []


@router.post("/", response_model=BudgetResponse, status_code=201)
def create_budget(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create budget - stub implementation"""
    pass


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update budget - stub implementation"""
    pass


@router.delete("/{budget_id}", status_code=204)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete budget - stub implementation"""
    pass
