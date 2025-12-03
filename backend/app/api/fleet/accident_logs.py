from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.fleet.accident_log import accident_log as crud_accident_log
from app.schemas.fleet.accident_log import AccidentLogCreate, AccidentLogUpdate, AccidentLogResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AccidentLogResponse])
def list_accident_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all accident logs"""
    accident_logs = crud_accident_log.get_multi(db, skip=skip, limit=limit)
    return accident_logs

@router.get("/{accident_log_id}", response_model=AccidentLogResponse)
def get_accident_log(
    accident_log_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific accident log by ID"""
    accident_log = crud_accident_log.get(db, id=accident_log_id)
    if not accident_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accident log not found"
        )
    return accident_log

@router.post("/", response_model=AccidentLogResponse, status_code=status.HTTP_201_CREATED)
def create_accident_log(
    accident_log_in: AccidentLogCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new accident log"""
    accident_log = crud_accident_log.create(db, obj_in=accident_log_in)
    return accident_log

@router.put("/{accident_log_id}", response_model=AccidentLogResponse)
def update_accident_log(
    accident_log_id: int,
    accident_log_in: AccidentLogUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an accident log"""
    accident_log = crud_accident_log.get(db, id=accident_log_id)
    if not accident_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accident log not found"
        )
    accident_log = crud_accident_log.update(db, db_obj=accident_log, obj_in=accident_log_in)
    return accident_log

@router.delete("/{accident_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_accident_log(
    accident_log_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete an accident log"""
    accident_log = crud_accident_log.get(db, id=accident_log_id)
    if not accident_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accident log not found"
        )
    crud_accident_log.remove(db, id=accident_log_id)
    return None
