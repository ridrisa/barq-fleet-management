"""Enhanced User Management API - Bulk Operations & Password Reset

This file contains additional user management endpoints that were requested.
These can be merged into users.py or kept separate.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_superuser, get_db
from app.core.security import get_password_hash
from app.models.role import Role
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.services.password_reset_service import password_reset_service
from app.services.email_notification_service import email_notification_service, EmailRecipient

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
    """Schema for password reset response - never exposes sensitive tokens"""

    message: str
    # SECURITY: reset_token and expires_at removed - these should NEVER be in API responses
    # Tokens should only be sent via secure channels (email/SMS)


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
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request password reset.

    Sends a password reset link via email.
    Public endpoint - no authentication required.

    SECURITY:
    - Always returns generic success message to prevent user enumeration
    - NEVER returns the reset token in the response
    - Token should only be sent via secure channel (email)

    Implementation steps:
    1. Generate secure random token
    2. Store token hash (not raw token) in database with expiration
    3. Send email with reset link containing the raw token
    4. Return generic success message
    """
    user = db.query(User).filter(User.email == data.email).first()

    # Always return success to avoid user enumeration
    # (Don't reveal if email exists or not)
    if not user:
        return PasswordResetResponse(
            message="If an account exists with this email, a password reset link has been sent."
        )

    # Get client info for audit trail
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Create secure reset token using the password reset service
    # This stores the token hash (not raw token) in database
    raw_token, token_record = password_reset_service.create_reset_token(
        db=db,
        user=user,
        ip_address=client_ip,
        user_agent=user_agent,
        expire_hours=24,
    )

    # Send email with reset link containing the raw token
    frontend_url = os.getenv("FRONTEND_URL", "https://barq-web-staging-frydalfroq-ww.a.run.app")
    reset_link = f"{frontend_url}/reset-password?token={raw_token}"

    email_html = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>Dear {user.full_name or user.email},</p>
        <p>We received a request to reset your password. Click the link below to reset it:</p>
        <p><a href="{reset_link}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>Or copy and paste this link into your browser:</p>
        <p>{reset_link}</p>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't request this, please ignore this email or contact support if you have concerns.</p>
        <p>Best regards,<br>BARQ Fleet Management</p>
    </body>
    </html>
    """

    email_notification_service.send_email(
        to=EmailRecipient(email=user.email, name=user.full_name),
        subject="Password Reset Request - BARQ Fleet Management",
        html_content=email_html,
        plain_content=f"Reset your password by visiting: {reset_link}. This link expires in 24 hours.",
    )

    # Return generic success message - NEVER return the token in response
    return PasswordResetResponse(
        message="If an account exists with this email, a password reset link has been sent."
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

    SECURITY:
    - Generates a temporary password and sends it to user via secure channel (email)
    - NEVER returns the temporary password in the API response
    - Sets flag to force password change on next login

    Implementation steps:
    1. Generate secure temporary password
    2. Hash and store password
    3. Send temp password to user's email (not in API response)
    4. Set force_password_change flag
    5. Return success message only
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {user_id} not found"
        )

    # Generate temporary password
    temp_password = secrets.token_urlsafe(12)
    user.hashed_password = get_password_hash(temp_password)

    # Set flag to force password change on next login (if column exists)
    if hasattr(user, 'force_password_change'):
        user.force_password_change = True

    db.commit()

    # Send temp_password via email to user.email
    email_html = f"""
    <html>
    <body>
        <h2>Password Reset by Administrator</h2>
        <p>Dear {user.full_name or user.email},</p>
        <p>Your password has been reset by an administrator.</p>
        <p>Your temporary password is: <strong>{temp_password}</strong></p>
        <p><strong>Important:</strong> Please change this password upon your next login for security.</p>
        <p>If you did not expect this reset, please contact support immediately.</p>
        <p>Best regards,<br>BARQ Fleet Management</p>
    </body>
    </html>
    """

    email_notification_service.send_email(
        to=EmailRecipient(email=user.email, name=user.full_name),
        subject="Password Reset by Administrator - BARQ Fleet Management",
        html_content=email_html,
        plain_content=f"Your password has been reset. Temporary password: {temp_password}. Please change it upon your next login.",
    )

    # SECURITY: Don't return the password - it should be sent via email
    return {
        "message": "Password has been reset. Temporary password sent to user's email.",
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
