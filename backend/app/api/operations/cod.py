from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud.operations import cod as crud_cod
from app.schemas.operations.cod import CODCreate, CODUpdate, CODResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CODResponse])
def list_cod_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all COD transactions"""
    cod_transactions = crud_cod.get_multi(db, skip=skip, limit=limit)
    return cod_transactions

@router.get("/{cod_id}", response_model=CODResponse)
def get_cod_transaction(
    cod_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific COD transaction by ID"""
    cod = crud_cod.get(db, id=cod_id)
    if not cod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="COD transaction not found"
        )
    return cod

@router.post("/", response_model=CODResponse, status_code=status.HTTP_201_CREATED)
def create_cod_transaction(
    cod_in: CODCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new COD transaction"""
    cod = crud_cod.create(db, obj_in=cod_in)
    return cod

@router.put("/{cod_id}", response_model=CODResponse)
def update_cod_transaction(
    cod_id: int,
    cod_in: CODUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a COD transaction"""
    cod = crud_cod.get(db, id=cod_id)
    if not cod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="COD transaction not found"
        )
    cod = crud_cod.update(db, db_obj=cod, obj_in=cod_in)
    return cod

@router.delete("/{cod_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cod_transaction(
    cod_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a COD transaction"""
    cod = crud_cod.get(db, id=cod_id)
    if not cod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="COD transaction not found"
        )
    crud_cod.remove(db, id=cod_id)
    return None
