"""
Core dependencies for FastAPI endpoints

This module provides all authentication and authorization dependencies used
throughout the application. It centralizes user authentication, role checks,
database session management, and multi-tenant organization context.

Exports:
    - get_db: Database session dependency (re-exported from core.database)
    - get_current_user: Get authenticated user from JWT token
    - get_current_active_user: Get authenticated and active user
    - get_current_superuser: Get authenticated superuser
    - get_current_organization: Get current organization from JWT token
    - get_tenant_db_session: Get tenant-scoped database session with RLS
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.core.database import db_manager, get_db
from app.crud.user import crud_user
from app.models.tenant.organization import Organization
from app.models.user import User
from app.schemas.token import TokenPayload

# Re-export get_db for convenience
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_active_user",
    "get_current_superuser",
    "get_current_organization",
    "get_tenant_db_session",
    "oauth2_scheme",
]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
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
            options={"verify_aud": False},  # Skip audience verification for flexibility
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


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
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


def get_current_superuser(current_user: User = Depends(get_current_user)) -> User:
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
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user


# ============================================================================
# Multi-Tenancy Dependencies
# ============================================================================


def get_organization_id_from_token(token: str = Depends(oauth2_scheme)) -> Optional[int]:
    """
    Extract organization ID from JWT token without full user validation.

    Args:
        token: JWT access token

    Returns:
        Organization ID or None if not present in token
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        org_id = payload.get("org_id")
        return int(org_id) if org_id else None
    except (JWTError, ValueError, TypeError):
        return None


def get_current_organization(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Organization:
    """
    Get the current organization from JWT token.

    The organization ID is embedded in the JWT token during login.
    This dependency validates the organization exists and is active.

    Args:
        db: Database session
        token: JWT access token from Authorization header

    Returns:
        Organization: The active organization

    Raises:
        HTTPException: 401 if no organization in token
        HTTPException: 403 if organization is inactive or not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No organization context in token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_aud": False},
        )
        org_id = payload.get("org_id")
        if org_id is None:
            raise credentials_exception
        org_id = int(org_id)
    except (JWTError, ValueError, TypeError):
        raise credentials_exception

    organization = db.query(Organization).filter(Organization.id == org_id).first()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization not found")

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Organization is inactive"
        )

    return organization


def get_tenant_db_session(
    current_user: User = Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
) -> Generator[Session, None, None]:
    """
    Get a tenant-scoped database session with RLS context.

    This dependency configures PostgreSQL session variables for Row-Level Security,
    ensuring all queries are automatically filtered by the current organization.

    Args:
        current_user: The authenticated user
        current_org: The current organization from token

    Yields:
        Database session with RLS context set

    Usage:
        @router.get("/couriers")
        def list_couriers(db: Session = Depends(get_tenant_db_session)):
            # Automatically filtered by organization_id via RLS
            return db.query(Courier).all()
    """
    db = db_manager.create_session()
    try:
        # Set RLS context variables
        is_superuser = crud_user.is_superuser(current_user)
        db.execute(text(f"SET app.current_org_id = '{current_org.id}'"))
        db.execute(text(f"SET app.is_superuser = '{str(is_superuser).lower()}'"))
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        # Reset context variables
        try:
            db.execute(text("RESET app.current_org_id"))
            db.execute(text("RESET app.is_superuser"))
        except Exception:
            pass
        db.close()


def get_optional_tenant_db_session(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Generator[Session, None, None]:
    """
    Get a tenant-scoped database session if organization context is available.

    Unlike get_tenant_db_session, this dependency doesn't require an organization
    in the token - useful for endpoints that work with or without tenant context.

    Args:
        token: JWT access token
        db: Base database session

    Yields:
        Database session, optionally with RLS context
    """
    org_id = get_organization_id_from_token(token)

    if org_id:
        try:
            db.execute(text(f"SET app.current_org_id = '{org_id}'"))
            yield db
        finally:
            try:
                db.execute(text("RESET app.current_org_id"))
            except Exception:
                pass
    else:
        yield db


class TenantRequired:
    """
    Dependency class for requiring specific organization roles.

    Usage:
        @router.get("/admin")
        def admin_only(
            org: Organization = Depends(TenantRequired(roles=["OWNER", "ADMIN"]))
        ):
            return {"org": org.name}
    """

    def __init__(self, roles: Optional[list] = None):
        """
        Initialize with required roles.

        Args:
            roles: List of organization roles that can access the endpoint.
                   If None, any authenticated user with org context can access.
        """
        self.roles = roles

    def __call__(
        self,
        current_user: User = Depends(get_current_user),
        current_org: Organization = Depends(get_current_organization),
        db: Session = Depends(get_db),
    ) -> Organization:
        """
        Validate user has required role in the organization.

        Args:
            current_user: The authenticated user
            current_org: The current organization
            db: Database session

        Returns:
            Organization if user has required role

        Raises:
            HTTPException: 403 if user doesn't have required role
        """
        if self.roles:
            # Import here to avoid circular imports
            from app.models.tenant.organization_user import OrganizationUser

            org_user = (
                db.query(OrganizationUser)
                .filter(
                    OrganizationUser.organization_id == current_org.id,
                    OrganizationUser.user_id == current_user.id,
                    OrganizationUser.is_active == True,
                )
                .first()
            )

            if org_user is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a member of this organization",
                )

            if org_user.role.value not in self.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of these roles: {', '.join(self.roles)}",
                )

        return current_org
