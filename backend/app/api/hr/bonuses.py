from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.crud.hr.bonus import bonus as crud_bonus
from app.schemas.hr.bonus import BonusCreate, BonusResponse, BonusUpdate

router = APIRouter()


@router.get("/", response_model=List[BonusResponse])
def list_bonuses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """List all bonuses"""
    bonuses = crud_bonus.get_multi(db, skip=skip, limit=limit)
    return bonuses


@router.get("/{bonus_id}", response_model=BonusResponse)
def get_bonus(bonus_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Get a specific bonus by ID"""
    bonus = crud_bonus.get(db, id=bonus_id)
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")
    return bonus


@router.post("/", response_model=BonusResponse, status_code=status.HTTP_201_CREATED)
def create_bonus(
    bonus_in: BonusCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Create a new bonus"""
    bonus = crud_bonus.create(db, obj_in=bonus_in)
    return bonus


@router.put("/{bonus_id}", response_model=BonusResponse)
def update_bonus(
    bonus_id: int,
    bonus_in: BonusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Update a bonus"""
    bonus = crud_bonus.get(db, id=bonus_id)
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")
    bonus = crud_bonus.update(db, db_obj=bonus, obj_in=bonus_in)
    return bonus


@router.delete("/{bonus_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bonus(
    bonus_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """Delete a bonus"""
    bonus = crud_bonus.get(db, id=bonus_id)
    if not bonus:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bonus not found")
    crud_bonus.remove(db, id=bonus_id)
    return None
