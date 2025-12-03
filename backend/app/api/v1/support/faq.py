"""FAQ API Routes"""

from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.support import FAQCategoryList, FAQCreate, FAQList, FAQResponse, FAQUpdate
from app.services.support import faq_service

router = APIRouter()


@router.get("/", response_model=List[FAQResponse])
def get_faqs(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    active_only: bool = True,
):
    """
    Get list of FAQs

    By default, returns only active FAQs
    """
    if category:
        return faq_service.get_by_category(db, category=category, skip=skip, limit=limit)

    if active_only:
        return faq_service.get_active(db, skip=skip, limit=limit)

    return faq_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
def create_faq(
    faq_in: FAQCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new FAQ"""
    return faq_service.create(db, obj_in=faq_in)


@router.get("/search", response_model=List[FAQResponse])
def search_faqs(
    q: str = Query(..., min_length=2, description="Search query"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Search FAQs by question or answer"""
    return faq_service.search(db, query=q, skip=skip, limit=limit)


@router.get("/categories", response_model=Dict[str, int])
def get_categories(
    db: Session = Depends(get_db),
):
    """Get list of FAQ categories with counts"""
    return faq_service.get_categories(db)


@router.get("/top", response_model=List[FAQResponse])
def get_top_faqs(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """Get top viewed FAQs"""
    return faq_service.get_top_viewed(db, limit=limit)


@router.get("/{faq_id}", response_model=FAQResponse)
def get_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    increment_view: bool = True,
):
    """Get FAQ by ID"""
    if increment_view:
        faq = faq_service.increment_view_count(db, faq_id=faq_id)
    else:
        faq = faq_service.get(db, id=faq_id)

    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return faq


@router.put("/{faq_id}", response_model=FAQResponse)
def update_faq(
    faq_id: int,
    faq_in: FAQUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update FAQ"""
    faq = faq_service.get(db, id=faq_id)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return faq_service.update(db, db_obj=faq, obj_in=faq_in)


@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_faq(
    faq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete FAQ"""
    faq = faq_service.get(db, id=faq_id)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    faq_service.remove(db, id=faq_id)


@router.post("/{faq_id}/reorder", response_model=FAQResponse)
def reorder_faq(
    faq_id: int,
    new_order: int = Query(..., ge=0, description="New order position"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update FAQ order"""
    faq = faq_service.reorder(db, faq_id=faq_id, new_order=new_order)
    if not faq:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
    return faq
