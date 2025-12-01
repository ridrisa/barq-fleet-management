from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.hr import leave as crud_leave
from app.schemas.hr.leave import LeaveCreate, LeaveUpdate, LeaveResponse
from app.config.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[LeaveResponse])
def list_leaves(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all leave requests"""
    leaves = crud_leave.get_multi(db, skip=skip, limit=limit)
    return leaves

@router.get("/{leave_id}", response_model=LeaveResponse)
def get_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific leave request by ID"""
    leave = crud_leave.get(db, id=leave_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    return leave

@router.post("/", response_model=LeaveResponse, status_code=status.HTTP_201_CREATED)
def create_leave(
    leave_in: LeaveCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new leave request"""
    leave = crud_leave.create(db, obj_in=leave_in)
    return leave

@router.put("/{leave_id}", response_model=LeaveResponse)
def update_leave(
    leave_id: int,
    leave_in: LeaveUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a leave request"""
    leave = crud_leave.get(db, id=leave_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    leave = crud_leave.update(db, db_obj=leave, obj_in=leave_in)
    return leave

@router.delete("/{leave_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_leave(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a leave request"""
    leave = crud_leave.get(db, id=leave_id)
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    crud_leave.remove(db, id=leave_id)
