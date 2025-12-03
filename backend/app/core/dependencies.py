"""
Core dependencies for FastAPI endpoints

This module provides all authentication and authorization dependencies used
throughout the application. It centralizes user authentication, role checks,
and database session management.

Exports:
    - get_db: Database session dependency (re-exported from core.database)
    - get_current_user: Get authenticated user from JWT token
    - get_current_active_user: Get authenticated and active user
    - get_current_superuser: Get authenticated superuser
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.config.settings import settings
from app.crud.user import crud_user
from app.models.user import User
from app.schemas.token import TokenPayload

# Re-export get_db for convenience
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "oauth2_scheme",
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        db: Database session
        token: JWT access token from Authorization header

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False}  # Skip audience verification for flexibility
        )
        token_data = TokenPayload(**payload)
        if token_data.sub is None:
            raise credentials_exception
        user_id = int(token_data.sub)
    except (JWTError, ValueError):
        raise credentials_exception

    user = crud_user.get(db, id=user_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current authenticated and active user.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        User: The active user

    Raises:
        HTTPException: 400 if user is inactive
    """
    if not crud_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current authenticated superuser.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        User: The superuser

    Raises:
        HTTPException: 403 if user is not a superuser
    """
    if not crud_user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
