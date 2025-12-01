"""Admin API Keys Management API"""
import hashlib
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_superuser
from app.models.user import User
from app.models.admin.api_key import ApiKey, ApiKeyStatus
from app.schemas.admin.api_key import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeyWithSecret,
    ApiKeyListResponse,
)

router = APIRouter()


def hash_api_key(key: str) -> str:
    """Hash API key for secure storage"""
    return hashlib.sha256(key.encode()).hexdigest()


@router.get("/", response_model=ApiKeyListResponse)
def list_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List all API keys with filtering and pagination.

    Requires superuser permission.
    """
    query = db.query(ApiKey)

    # Apply filters
    if user_id:
        query = query.filter(ApiKey.user_id == user_id)
    if status:
        query = query.filter(ApiKey.status == status)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (ApiKey.name.ilike(search_pattern)) |
            (ApiKey.description.ilike(search_pattern))
        )

    # Get total count
    total = query.count()

    # Get paginated results
    api_keys = query.order_by(desc(ApiKey.created_at)).offset(skip).limit(limit).all()

    return ApiKeyListResponse(
        items=api_keys,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=ApiKeyWithSecret, status_code=status.HTTP_201_CREATED)
def create_api_key(
    api_key_in: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Create a new API key.

    Requires superuser permission.

    Returns the full API key - SAVE IT IMMEDIATELY, it won't be shown again.
    """
    # Generate API key
    secret_key = ApiKey.generate_key()
    key_prefix = secret_key[:8]
    key_hash = hash_api_key(secret_key)

    # Create API key record
    api_key = ApiKey(
        **api_key_in.dict(),
        user_id=current_user.id,
        key_prefix=key_prefix,
        key_hash=key_hash,
        status=ApiKeyStatus.ACTIVE.value,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # Return response with secret key (only time it's shown)
    response = ApiKeyWithSecret.from_orm(api_key)
    response.secret_key = secret_key

    return response


@router.get("/{api_key_id}", response_model=ApiKeyResponse)
def get_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get a specific API key by ID.

    Requires superuser permission.

    Note: Full key is never returned, only the prefix.
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {api_key_id} not found"
        )
    return api_key


@router.patch("/{api_key_id}", response_model=ApiKeyResponse)
def update_api_key(
    api_key_id: int,
    api_key_in: ApiKeyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Update an API key.

    Requires superuser permission.

    Can update name, description, scopes, rate limits, and expiration.
    Cannot update the actual key value.
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {api_key_id} not found"
        )

    update_data = api_key_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(api_key, field, value)

    db.commit()
    db.refresh(api_key)
    return api_key


@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Delete an API key.

    Requires superuser permission.

    Permanently deletes the API key. Consider revoking instead.
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {api_key_id} not found"
        )

    db.delete(api_key)
    db.commit()
    return None


@router.post("/{api_key_id}/revoke", response_model=ApiKeyResponse)
def revoke_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Revoke an API key.

    Requires superuser permission.

    Revoked keys can no longer be used but are kept for audit purposes.
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {api_key_id} not found"
        )

    api_key.status = ApiKeyStatus.REVOKED.value

    db.commit()
    db.refresh(api_key)
    return api_key


@router.post("/{api_key_id}/rotate", response_model=ApiKeyWithSecret)
def rotate_api_key(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Rotate an API key (generate new key with same settings).

    Requires superuser permission.

    Creates a new key value while preserving all other settings.
    Returns the new key - SAVE IT IMMEDIATELY, it won't be shown again.
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {api_key_id} not found"
        )

    # Generate new key
    secret_key = ApiKey.generate_key()
    key_prefix = secret_key[:8]
    key_hash = hash_api_key(secret_key)

    # Update API key
    api_key.key_prefix = key_prefix
    api_key.key_hash = key_hash
    api_key.status = ApiKeyStatus.ACTIVE.value
    api_key.last_used_at = None
    api_key.total_requests = 0

    db.commit()
    db.refresh(api_key)

    # Return response with new secret key
    response = ApiKeyWithSecret.from_orm(api_key)
    response.secret_key = secret_key

    return response


@router.get("/{api_key_id}/usage", response_model=dict)
def get_api_key_usage(
    api_key_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Get API key usage statistics.

    Requires superuser permission.

    Returns request counts, last used info, and rate limit status.
    """
    api_key = db.query(ApiKey).filter(ApiKey.id == api_key_id).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key with id {api_key_id} not found"
        )

    return {
        "api_key_id": api_key.id,
        "name": api_key.name,
        "total_requests": api_key.total_requests,
        "last_used_at": api_key.last_used_at,
        "last_request_ip": api_key.last_request_ip,
        "rate_limit_per_minute": api_key.rate_limit_per_minute,
        "rate_limit_per_hour": api_key.rate_limit_per_hour,
        "rate_limit_per_day": api_key.rate_limit_per_day,
        "is_active": api_key.is_active(),
        "status": api_key.status,
    }


@router.get("/user/{user_id}/keys", response_model=List[ApiKeyResponse])
def list_user_api_keys(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    List all API keys for a specific user.

    Requires superuser permission.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    api_keys = db.query(ApiKey).filter(ApiKey.user_id == user_id).order_by(desc(ApiKey.created_at)).all()
    return api_keys
