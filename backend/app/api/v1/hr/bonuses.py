from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.hr.bonus import BonusCreate, BonusResponse, BonusUpdate
from app.services.hr.bonus_service import bonus_service

router = APIRouter()


@router.get("/", response_model=List[BonusResponse])
def list_bonuses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all bonuses"""
    bonuses = bonus_service.get_multi(db, skip=skip, limit=limit)
    return bonuses


@router.get("/{bonus_id}", response_model=BonusResponse)
def get_bonus(bonus_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get a specific bonus by ID"""
    bonus = bonus_service.get(db, bonus_id)
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")
    return bonus


@router.post("/", response_model=BonusResponse, status_code=status.HTTP_201_CREATED)
def create_bonus(
    bonus_in: BonusCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Create a new bonus"""
    bonus = bonus_service.create(db, obj_in=bonus_in)
    return bonus


@router.put("/{bonus_id}", response_model=BonusResponse)
def update_bonus(
    bonus_id: int,
    bonus_in: BonusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a bonus"""
    bonus = bonus_service.get(db, bonus_id)
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")
    bonus = bonus_service.update(db, db_obj=bonus, obj_in=bonus_in)
    return bonus


@router.delete("/{bonus_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bonus(
    bonus_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a bonus"""
    bonus = bonus_service.get(db, bonus_id)
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")
    bonus_service.delete(db, id=bonus_id)
    return None
