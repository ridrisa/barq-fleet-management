"""Loan Management API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from decimal import Decimal

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.hr import (
    LoanCreate, LoanUpdate, LoanResponse, LoanStatus
)
from app.services.hr import loan_service


router = APIRouter()


@router.get("/", response_model=List[LoanResponse])
def get_loans(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    status: Optional[LoanStatus] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of loans with filtering

    Filters:
    - courier_id: Filter by courier ID
    - status: Filter by loan status (pending, approved, rejected, active, paid)
    """
    # If courier_id filter is provided
    if courier_id:
        return loan_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit
        )

    # Build dynamic filters
    filters = {}
    if status:
        filters["status"] = status

    return loan_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan_in: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new loan request"""
    return loan_service.create(db, obj_in=loan_in)


@router.get("/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get loan by ID"""
    loan = loan_service.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(
    loan_id: int,
    loan_in: LoanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update loan"""
    loan = loan_service.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    return loan_service.update(db, db_obj=loan, obj_in=loan_in)


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete loan"""
    loan = loan_service.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan_service.delete(db, id=loan_id)
    return None


@router.get("/courier/{courier_id}", response_model=List[LoanResponse])
def get_courier_loans(
    courier_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all loans for a specific courier"""
    return loan_service.get_by_courier(
        db, courier_id=courier_id, skip=skip, limit=limit
    )


@router.post("/{loan_id}/payment", response_model=LoanResponse)
def make_loan_payment(
    loan_id: int,
    amount: Decimal = Body(..., embed=True, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Make a payment towards a loan

    Updates the remaining amount and marks as paid if fully repaid
    """
    loan = loan_service.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.status != LoanStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Can only make payments on active loans"
        )

    updated_loan = loan_service.make_payment(db, loan_id=loan_id, amount=amount)
    if not updated_loan:
        raise HTTPException(status_code=400, detail="Payment amount exceeds remaining balance")

    return updated_loan


@router.post("/{loan_id}/approve", response_model=LoanResponse)
def approve_loan(
    loan_id: int,
    notes: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Approve a loan request

    Changes status from pending to approved/active
    """
    loan = loan_service.get(db, id=loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    if loan.status != LoanStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Can only approve pending loans"
        )

    updated_loan = loan_service.approve_loan(
        db, loan_id=loan_id, approved_by=current_user.id, notes=notes
    )

    return updated_loan


@router.get("/statistics", response_model=dict)
def get_loan_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get loan statistics

    Returns:
    - total: Total number of loans
    - active: Number of active loans
    - paid: Number of fully paid loans
    - pending: Number of pending approval
    - total_amount: Total loan amount issued
    - total_outstanding: Total amount still owed
    """
    return loan_service.get_statistics(db)
