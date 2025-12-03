"""Attendance Management API Routes"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from sqlalchemy.orm import Session
from datetime import date, datetime

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.hr import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceStatus
)
from app.services.hr import attendance_service


router = APIRouter()


@router.get("/", response_model=List[AttendanceResponse])
def get_attendances(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    courier_id: Optional[int] = None,
    status: Optional[AttendanceStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get list of attendance records with filtering

    Filters:
    - courier_id: Filter by courier ID
    - status: Filter by attendance status
    - date_from, date_to: Filter by date range
    """
    # If date range is provided
    if date_from and date_to:
        return attendance_service.get_by_date_range(
            db, start_date=date_from, end_date=date_to, skip=skip, limit=limit
        )

    # If courier_id filter is provided
    if courier_id:
        return attendance_service.get_by_courier(
            db, courier_id=courier_id, skip=skip, limit=limit
        )

    # Build dynamic filters
    filters = {}
    if status:
        filters["status"] = status

    return attendance_service.get_multi(db, skip=skip, limit=limit, filters=filters)


@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    attendance_in: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new attendance record"""
    return attendance_service.create(db, obj_in=attendance_in)


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get attendance record by ID"""
    attendance = attendance_service.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update attendance record"""
    attendance = attendance_service.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    return attendance_service.update(db, db_obj=attendance, obj_in=attendance_in)


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete attendance record"""
    attendance = attendance_service.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    attendance_service.delete(db, id=attendance_id)
    return None


@router.get("/courier/{courier_id}", response_model=List[AttendanceResponse])
def get_courier_attendance(
    courier_id: int,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get all attendance records for a specific courier"""
    return attendance_service.get_by_courier(
        db, courier_id=courier_id, skip=skip, limit=limit
    )


@router.post("/check-in", response_model=AttendanceResponse)
def check_in_courier(
    courier_id: int = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check in a courier for the day

    Creates a new attendance record with check-in time
    """
    # Check if already checked in today
    today = date.today()
    existing = attendance_service.get_by_courier_and_date(
        db, courier_id=courier_id, attendance_date=today
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Courier has already checked in today"
        )

    # Create attendance record with check-in time
    attendance_in = AttendanceCreate(
        courier_id=courier_id,
        date=today,
        check_in_time=datetime.now().time(),
        status=AttendanceStatus.PRESENT
    )

    return attendance_service.create(db, obj_in=attendance_in)


@router.post("/{attendance_id}/check-out", response_model=AttendanceResponse)
def check_out_courier(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Check out a courier

    Updates the attendance record with check-out time
    """
    attendance = attendance_service.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    if attendance.check_out_time:
        raise HTTPException(
            status_code=400,
            detail="Courier has already checked out"
        )

    return attendance_service.check_out(db, attendance_id=attendance_id)


@router.get("/statistics", response_model=dict)
def get_attendance_statistics(
    db: Session = Depends(get_db),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Get attendance statistics

    Returns:
    - total: Total attendance records
    - present: Number of present records
    - absent: Number of absent records
    - late: Number of late arrivals
    - on_leave: Number on leave
    """
    return attendance_service.get_statistics(db, start_date=date_from, end_date=date_to)
