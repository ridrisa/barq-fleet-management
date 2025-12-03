from datetime import timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_active_user
from app.config.settings import settings
from app.core.security import create_access_token
from app.crud.user import crud_user
from app.models.user import User
from app.models.tenant.organization import Organization
from app.models.tenant.organization_user import OrganizationUser, OrganizationRole
from app.schemas.token import Token, TokenWithOrganization
from app.schemas.user import User as UserSchema, UserCreate
from app.schemas.tenant.organization import OrganizationResponse
from app.schemas.tenant.organization_user import OrganizationUserWithDetails
from app.services.tenant.organization_service import organization_service
from app.services.tenant.organization_user_service import organization_user_service

router = APIRouter()


@router.post("/login", response_model=TokenWithOrganization)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login (email/password) with organization context."""
    user = crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    # Get user's primary organization (first active membership)
    memberships = organization_user_service.get_by_user(db, user.id, is_active=True)

    organization_id: Optional[int] = None
    organization_name: Optional[str] = None
    organization_role: Optional[str] = None

    if memberships:
        # Use first active organization
        primary_membership = memberships[0]
        org = organization_service.get(db, primary_membership.organization_id)
        if org and org.is_active:
            organization_id = org.id
            organization_name = org.name
            organization_role = primary_membership.role.value

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "org_id": organization_id,
            "org_role": organization_role,
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "organization_id": organization_id,
        "organization_name": organization_name,
        "organization_role": organization_role,
    }


@router.post("/google", response_model=Token)
def google_auth(*, db: Session = Depends(get_db), token_data: Dict[str, str] = Body(...)):
    """
    Google OAuth2 authentication.
    Expects: {"credential": "google_id_token"}
    """
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    credential = token_data.get("credential")
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing credential in request",
        )

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
        )

    google_id = idinfo.get("sub")
    email = idinfo.get("email")
    name = idinfo.get("name", "")
    picture = idinfo.get("picture", "")

    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google token",
        )

    user = crud_user.get_by_google_id(db, google_id=google_id)

    if not user:
        user = crud_user.get_by_email(db, email=email)
        if user:
            user.google_id = google_id
            user.picture = picture
            db.commit()
            db.refresh(user)

    if not user:
        user = crud_user.create_google_user(
            db,
            email=email,
            google_id=google_id,
            full_name=name,
            picture=picture,
        )

    if not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=TokenWithOrganization)
def register(*, db: Session = Depends(get_db), user_data: Dict[str, str] = Body(...)):
    """
    Public registration endpoint - Creates user and default organization.
    Expects: {"email": "user@example.com", "password": "password123", "full_name": "User Name", "organization_name": "My Company"}
    """
    email = user_data.get("email")
    password = user_data.get("password")
    full_name = user_data.get("full_name", "User")
    organization_name = user_data.get("organization_name")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required",
        )

    existing_user = crud_user.get_by_email(db, email=email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_count = db.query(crud_user.model).count()
    is_first_user = user_count == 0

    user_in = UserCreate(
        email=email,
        password=password,
        full_name=full_name,
        is_active=True,
        is_superuser=is_first_user,
        role="admin" if is_first_user else "user",
    )
    user = crud_user.create(db, obj_in=user_in)

    # Create default organization for user
    organization_id: Optional[int] = None
    org_name: Optional[str] = None
    organization_role: Optional[str] = None

    if organization_name:
        from app.schemas.tenant.organization import OrganizationCreate
        from app.schemas.tenant.organization_user import OrganizationUserCreate

        org_in = OrganizationCreate(name=organization_name)
        org = organization_service.create_organization(db, obj_in=org_in)

        # Add user as owner
        org_user_in = OrganizationUserCreate(
            user_id=user.id,
            role=OrganizationRole.OWNER,
        )
        organization_user_service.add_user(db, organization_id=org.id, obj_in=org_user_in)

        organization_id = org.id
        org_name = org.name
        organization_role = OrganizationRole.OWNER.value

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "org_id": organization_id,
            "org_role": organization_role,
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "organization_id": organization_id,
        "organization_name": org_name,
        "organization_role": organization_role,
    }


@router.get("/me", response_model=UserSchema)
def get_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user information (requires authentication)."""
    return current_user


@router.get("/me/organizations")
def get_user_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all organizations the current user belongs to.
    Returns list of memberships with organization details.
    """
    memberships = organization_user_service.get_by_user(db, current_user.id, is_active=True)

    result = []
    for m in memberships:
        org = organization_service.get(db, m.organization_id)
        if org and org.is_active:
            result.append({
                "organization": {
                    "id": org.id,
                    "name": org.name,
                    "slug": org.slug,
                    "is_active": org.is_active,
                    "subscription_plan": org.subscription_plan.value,
                    "subscription_status": org.subscription_status.value,
                    "max_users": org.max_users,
                    "max_couriers": org.max_couriers,
                    "max_vehicles": org.max_vehicles,
                    "trial_ends_at": org.trial_ends_at.isoformat() if org.trial_ends_at else None,
                    "settings": org.settings,
                    "created_at": org.created_at.isoformat(),
                    "updated_at": org.updated_at.isoformat() if org.updated_at else None,
                },
                "role": m.role.value,
                "is_active": m.is_active,
                "permissions": m.permissions,
            })

    return result


@router.post("/switch-organization", response_model=TokenWithOrganization)
def switch_organization(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    organization_data: Dict[str, int] = Body(...),
):
    """
    Switch to a different organization.
    Returns a new token with the selected organization context.
    Expects: {"organization_id": 123}
    """
    organization_id = organization_data.get("organization_id")
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="organization_id is required",
        )

    # Verify user is a member of the organization
    if not organization_user_service.is_member(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization",
        )

    # Get organization
    org = organization_service.get(db, organization_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        )

    if not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization is inactive",
        )

    # Get user's role in this organization
    role = organization_user_service.get_user_role(db, organization_id, current_user.id)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(current_user.id),
            "org_id": organization_id,
            "org_role": role.value if role else None,
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "organization_id": organization_id,
        "organization_name": org.name,
        "organization_role": role.value if role else None,
    }
