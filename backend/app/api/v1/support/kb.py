"""Knowledge Base API Routes"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.support import (
    KBArticleCreate,
    KBArticleList,
    KBArticlePublish,
    KBArticleResponse,
    KBArticleSearch,
    KBArticleUpdate,
    KBArticleVote,
)
from app.services.support import kb_article_service

router = APIRouter()


@router.get("/", response_model=List[KBArticleList])
def get_articles(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    published_only: bool = True,
):
    """
    Get list of knowledge base articles

    By default, returns only published articles (for public access)
    Set published_only=false to get all articles (requires authentication)
    """
    if category:
        return kb_article_service.get_by_category(db, category=category, skip=skip, limit=limit)

    if published_only:
        return kb_article_service.get_published(db, skip=skip, limit=limit)

    return kb_article_service.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=KBArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article_in: KBArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create new knowledge base article"""
    # Check if slug already exists
    existing = kb_article_service.get_by_slug(db, slug=article_in.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Article with this slug already exists"
        )

    return kb_article_service.create(db, obj_in=article_in)


@router.get("/search", response_model=List[KBArticleList])
def search_articles(
    q: str = Query(..., min_length=2, description="Search query"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
):
    """Search knowledge base articles"""
    return kb_article_service.search(db, query=q, skip=skip, limit=limit)


@router.get("/categories", response_model=List[str])
def get_categories(
    db: Session = Depends(get_db),
):
    """Get list of all article categories"""
    return kb_article_service.get_categories(db)


@router.get("/top", response_model=List[KBArticleList])
def get_top_articles(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50),
):
    """Get top viewed articles"""
    return kb_article_service.get_top_articles(db, limit=limit)


@router.get("/{article_id}", response_model=KBArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    increment_view: bool = True,
):
    """Get article by ID"""
    if increment_view:
        article = kb_article_service.increment_view_count(db, article_id=article_id)
    else:
        article = kb_article_service.get(db, id=article_id)

    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.get("/slug/{slug}", response_model=KBArticleResponse)
def get_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    increment_view: bool = True,
):
    """Get article by slug"""
    article = kb_article_service.get_by_slug(db, slug=slug)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")

    if increment_view:
        kb_article_service.increment_view_count(db, article_id=article.id)

    return article


@router.put("/{article_id}", response_model=KBArticleResponse)
def update_article(
    article_id: int,
    article_in: KBArticleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update article"""
    article = kb_article_service.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return kb_article_service.update(db, db_obj=article, obj_in=article_in)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete article"""
    article = kb_article_service.get(db, id=article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    kb_article_service.remove(db, id=article_id)


@router.post("/{article_id}/publish", response_model=KBArticleResponse)
def publish_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Publish article"""
    article = kb_article_service.publish(db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.post("/{article_id}/unpublish", response_model=KBArticleResponse)
def unpublish_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unpublish article (set to draft)"""
    article = kb_article_service.unpublish(db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article


@router.post("/{article_id}/vote", response_model=KBArticleResponse)
def vote_article(
    article_id: int,
    vote_data: KBArticleVote,
    db: Session = Depends(get_db),
):
    """Vote on article helpfulness"""
    article = kb_article_service.vote_helpful(db, article_id=article_id, helpful=vote_data.helpful)
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
    return article
