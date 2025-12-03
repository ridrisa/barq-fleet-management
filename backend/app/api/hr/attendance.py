from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.hr import attendance as crud_attendance
from app.schemas.hr.attendance import AttendanceCreate, AttendanceUpdate, AttendanceResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AttendanceResponse])
def list_attendance(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all attendance records"""
    attendance = crud_attendance.get_multi(db, skip=skip, limit=limit)
    return attendance

@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific attendance record by ID"""
    attendance = crud_attendance.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    return attendance

@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    attendance_in: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new attendance record"""
    attendance = crud_attendance.create(db, obj_in=attendance_in)
    return attendance

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an attendance record"""
    attendance = crud_attendance.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    attendance = crud_attendance.update(db, db_obj=attendance, obj_in=attendance_in)
    return attendance

@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an attendance record"""
    attendance = crud_attendance.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found"
        )
    crud_attendance.remove(db, id=attendance_id)
    return None
