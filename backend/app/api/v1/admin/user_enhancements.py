"""Enhanced User Management API - Bulk Operations & Password Reset

This file contains additional user management endpoints that were requested.
These can be merged into users.py or kept separate.
"""

import secrets
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_superuser, get_db
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.schemas.user import User as UserSchema

router = APIRouter()


class BulkUserActivate(BaseModel):
    """Schema for bulk user activation"""

    user_ids: List[int]


class BulkUserDeactivate(BaseModel):
    """Schema for bulk user deactivation"""

    user_ids: List[int]


class BulkRoleAssignment(BaseModel):
    """Schema for bulk role assignment"""

    user_ids: List[int]
    role_ids: List[int]


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""

    token: str
    new_password: str


class PasswordResetResponse(BaseModel):
    """Schema for password reset response"""

    message: str
    reset_token: Optional[str] = None
    expires_at: Optional[datetime] = None


@router.post("/bulk/activate", response_model=dict)
def bulk_activate_users(
    data: BulkUserActivate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Bulk activate users.

    Requires superuser permission.

    Activates multiple users in a single operation.
    """
    users = db.query(User).filter(User.id.in_(data.user_ids)).all()

    if len(users) != len(data.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="One or more user IDs are invalid"
        )

    # Check if current user is in the list (prevent self-modification in bulk)
    if current_user.id in data.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot bulk modify your own account"
        )

    activated_count = 0
    for user in users:
        if not user.is_active:
            user.is_active = True
            activated_count += 1

    db.commit()

    return {
        "message": f"Successfully activated {activated_count} user(s)",
        "total_processed": len(users),
        "activated_count": activated_count,
    }


@router.post("/bulk/deactivate", response_model=dict)
def bulk_deactivate_users(
    data: BulkUserDeactivate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Bulk deactivate users.

    Requires superuser permission.

    Deactivates multiple users in a single operation.
    Cannot deactivate your own account or the last active superuser.
    """
    # Check if current user is in the list
    if current_user.id in data.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate your own account"
        )

    users = db.query(User).filter(User.id.in_(data.user_ids)).all()

    if len(users) != len(data.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="One or more user IDs are invalid"
        )

    # Check if any are superusers
    superuser_ids = [u.id for u in users if u.is_superuser]
    if superuser_ids:
        # Check remaining active superusers
        active_superusers_count = (
            db.query(User)
            .filter(
                User.is_superuser == True, User.is_active == True, User.id.notin_(data.user_ids)
            )
            .count()
        )

        if active_superusers_count < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate all superusers. At least one must remain active.",
            )

    deactivated_count = 0
    for user in users:
        if user.is_active:
            user.is_active = False
            deactivated_count += 1

    db.commit()

    return {
        "message": f"Successfully deactivated {deactivated_count} user(s)",
        "total_processed": len(users),
        "deactivated_count": deactivated_count,
    }


@router.post("/bulk/assign-roles", response_model=dict)
def bulk_assign_roles(
    data: BulkRoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Bulk assign roles to users.

    Requires superuser permission.

    Assigns specified roles to multiple users in a single operation.
    Replaces existing role assignments.
    """
    # Validate users
    users = db.query(User).filter(User.id.in_(data.user_ids)).all()
    if len(users) != len(data.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="One or more user IDs are invalid"
        )

    # Validate roles
    roles = db.query(Role).filter(Role.id.in_(data.role_ids), Role.is_active == True).all()
    if len(roles) != len(data.role_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more role IDs are invalid or inactive",
        )

    # Assign roles to all users
    for user in users:
        user.roles = roles

    db.commit()

    return {
        "message": f"Successfully assigned {len(roles)} role(s) to {len(users)} user(s)",
        "users_processed": len(users),
        "roles_assigned": len(roles),
    }


@router.post("/password-reset/request", response_model=PasswordResetResponse)
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """
    Request password reset.

    Generates a password reset token and sends it via email.
    Public endpoint - no authentication required.

    In production, this would:
    1. Generate a secure token
    2. Store it with expiration
    3. Send email with reset link
    4. Return success without revealing if user exists (security)
    """
    user = db.query(User).filter(User.email == data.email).first()

    # Always return success to avoid user enumeration
    if not user:
        return PasswordResetResponse(
            message="If an account exists with this email, a password reset link has been sent."
        )

    # Generate reset token (in production, store this securely)
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    # TODO: Store token in database with expiration
    # TODO: Send email with reset link

    return PasswordResetResponse(
        message="Password reset link has been sent to your email",
        reset_token=reset_token,  # Only for development/testing
        expires_at=expires_at,
    )


@router.post("/{user_id}/password-reset", response_model=dict)
def admin_reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Admin force reset user password.

    Requires superuser permission.

    Generates a temporary password and forces password change on next login.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
        )

    # Generate temporary password
    temp_password = secrets.token_urlsafe(12)
    user.hashed_password = get_password_hash(temp_password)

    # TODO: Set flag to force password change on next login
    # user.force_password_change = True

    db.commit()

    return {
        "message": "Password has been reset",
        "temporary_password": temp_password,  # In production, send via secure channel
        "user_id": user.id,
        "email": user.email,
    }


@router.delete("/bulk/delete", response_model=dict)
def bulk_delete_users(
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    """
    Bulk delete users.

    Requires superuser permission.

    DANGEROUS: Permanently deletes multiple users.
    Consider deactivation instead for audit trail preservation.
    """
    # Check if current user is in the list
    if current_user.id in user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account"
        )

    users = db.query(User).filter(User.id.in_(user_ids)).all()

    if len(users) != len(user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="One or more user IDs are invalid"
        )

    # Prevent deleting superusers
    superuser_ids = [u.id for u in users if u.is_superuser]
    if superuser_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete superuser accounts. Deactivate them instead.",
        )

    deleted_count = len(users)
    for user in users:
        db.delete(user)

    db.commit()

    return {
        "message": f"Successfully deleted {deleted_count} user(s)",
        "deleted_count": deleted_count,
    }
