from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.hr.loan import loan as crud_loan
from app.schemas.hr.loan import LoanCreate, LoanResponse, LoanUpdate

router = APIRouter()


@router.get("/", response_model=List[LoanResponse])
def list_loans(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all loans"""
    loans = crud_loan.get_multi(db, skip=skip, limit=limit)
    return loans


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get a specific loan by ID"""
    loan = crud_loan.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan_in: LoanCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Create a new loan"""
    loan = crud_loan.create(db, obj_in=loan_in)
    return loan


@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(
    loan_id: int,
    loan_in: LoanUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a loan"""
    loan = crud_loan.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    loan = crud_loan.update(db, db_obj=loan, obj_in=loan_in)
    return loan


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a loan"""
    loan = crud_loan.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    crud_loan.remove(db, id=loan_id)
    return None
