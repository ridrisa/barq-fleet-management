from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.fleet import AccidentLogCreate, AccidentLogUpdate, AccidentLogResponse, AccidentLogList
from app.services.fleet import accident_log_service

router = APIRouter()

@router.get("/", response_model=List[AccidentLogList])
def get_accident_logs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    vehicle_id: int = None,
    courier_id: int = None,
    current_user: User = Depends(get_current_user),
):
    """Get accident logs"""
    if vehicle_id:
        return accident_log_service.get_for_vehicle(db, vehicle_id=vehicle_id, skip=skip, limit=limit)
    elif courier_id:
        return accident_log_service.get_for_courier(db, courier_id=courier_id, skip=skip, limit=limit)
    return accident_log_service.get_multi(db, skip=skip, limit=limit)

@router.get("/open", response_model=List[AccidentLogList])
def get_open_accidents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Get open accident cases"""
    return accident_log_service.get_open_cases(db, skip=skip, limit=limit)

@router.get("/{accident_id}", response_model=AccidentLogResponse)
def get_accident_log(accident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get accident log by ID"""
    accident = accident_log_service.get(db, id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident log not found")
    return accident

@router.post("/", response_model=AccidentLogResponse, status_code=status.HTTP_201_CREATED)
def create_accident_log(accident_in: AccidentLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create new accident log"""
    return accident_log_service.create(db, obj_in=accident_in)

@router.put("/{accident_id}", response_model=AccidentLogResponse)
def update_accident_log(accident_id: int, accident_in: AccidentLogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update accident log"""
    accident = accident_log_service.get(db, id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident log not found")
    return accident_log_service.update(db, db_obj=accident, obj_in=accident_in)

@router.delete("/{accident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accident_log(accident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete accident log"""
    accident = accident_log_service.get(db, id=accident_id)
    if not accident:
        raise HTTPException(status_code=404, detail="Accident log not found")
    accident_log_service.delete(db, id=accident_id)
    return None
