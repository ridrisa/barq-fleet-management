from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from app.config.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


class ExpenseResponse(BaseModel):
    """Expense response schema"""
    id: int
    amount: float
    category: str
    description: str
    date: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ExpenseResponse])
def list_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all expenses - stub implementation"""
    return []


@router.post("/", response_model=ExpenseResponse, status_code=201)
def create_expense(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create expense - stub implementation"""
    pass


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update expense - stub implementation"""
    pass


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete expense - stub implementation"""
    pass
