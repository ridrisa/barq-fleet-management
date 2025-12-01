from datetime import timedelta
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.api.deps import get_db, get_current_active_user
from app.core.security import create_access_token
from app.crud.user import crud_user
from app.schemas.token import Token
from app.schemas.user import User as UserSchema
from app.models.user import User

from app.config.settings import settings

router = APIRouter()


@router.post("/login", response_model=Token)
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login (for traditional email/password)
    """
    user = crud_user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/google", response_model=Token)
def google_auth(
    *,
    db: Session = Depends(get_db),
    token_data: Dict[str, str] = Body(...)
):
    """
    Google OAuth2 authentication
    Expects: {"credential": "google_id_token"}
    """
    try:
        # Verify the Google ID token
        if not settings.GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google OAuth is not configured"
            )

        credential = token_data.get("credential")
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing credential in request"
            )

        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Extract user information
        google_id = idinfo.get("sub")
        email = idinfo.get("email")
        name = idinfo.get("name", "")
        picture = idinfo.get("picture", "")

        if not email or not google_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token"
            )

        # Check if user exists by Google ID
        user = crud_user.get_by_google_id(db, google_id=google_id)

        # If not found by Google ID, check by email
        if not user:
            user = crud_user.get_by_email(db, email=email)
            if user:
                # Update existing user with Google ID
                user.google_id = google_id
                user.picture = picture
                db.commit()
                db.refresh(user)

        # If still not found, create new user
        if not user:
            user = crud_user.create_google_user(
                db,
                email=email,
                google_id=google_id,
                full_name=name,
                picture=picture
            )

        if not crud_user.is_active(user):
            raise HTTPException(status_code=400, detail="Inactive user")

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )

        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )




@router.post("/register", response_model=Token)
def register(
    *,
    db: Session = Depends(get_db),
    user_data: Dict[str, str] = Body(...)
):
    """
    Public registration endpoint - Creates first admin user or regular users
    Expects: {"email": "user@example.com", "password": "password123", "full_name": "User Name"}
    """
    email = user_data.get("email")
    password = user_data.get("password")
    full_name = user_data.get("full_name", "User")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    # Check if user already exists
    existing_user = crud_user.get_by_email(db, email=email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if this is the first user (make them admin)
    user_count = db.query(crud_user.model).count()
    is_first_user = user_count == 0

    # Create user
    from app.schemas.user import UserCreate
    user_in = UserCreate(
        email=email,
        password=password,
        full_name=full_name,
        is_active=True,
        is_superuser=is_first_user,
        role="admin" if is_first_user else "user"
    )

    user = crud_user.create(db, obj_in=user_in)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserSchema)
def get_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    Requires authentication token
    """
    return current_user
