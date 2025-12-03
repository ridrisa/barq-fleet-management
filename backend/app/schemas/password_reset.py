"""
Password Reset Schemas

Pydantic schemas for password reset API endpoints.

These schemas define the request/response contracts for:
- Requesting a password reset
- Validating a reset token
- Completing the password reset

Author: BARQ Security Team
Last Updated: 2025-12-03
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class PasswordResetRequest(BaseModel):
    """
    Schema for requesting a password reset.

    The user provides their email address, and if it exists in the system,
    a reset token is generated and sent via email.

    Note: For security reasons, the API should return the same response
    whether or not the email exists (to prevent email enumeration attacks).
    """
    email: EmailStr = Field(
        ...,
        description="Email address of the account to reset"
    )


class PasswordResetRequestResponse(BaseModel):
    """
    Response after requesting a password reset.

    Always returns success message to prevent email enumeration.
    """
    message: str = Field(
        default="If an account with that email exists, a password reset link has been sent.",
        description="Success message (always the same for security)"
    )


class PasswordResetValidate(BaseModel):
    """
    Schema for validating a password reset token.

    Used when user clicks the reset link to verify the token is valid
    before showing the password reset form.
    """
    token: str = Field(
        ...,
        min_length=32,
        description="The reset token from the email link"
    )


class PasswordResetValidateResponse(BaseModel):
    """
    Response after validating a reset token.
    """
    valid: bool = Field(
        ...,
        description="Whether the token is valid"
    )
    message: str = Field(
        ...,
        description="Status message"
    )
    expires_at: Optional[datetime] = Field(
        None,
        description="Token expiration time (only if valid)"
    )


class PasswordResetComplete(BaseModel):
    """
    Schema for completing a password reset.

    User provides the token and their new password.
    """
    token: str = Field(
        ...,
        min_length=32,
        description="The reset token from the email link"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password (min 8 characters)"
    )
    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Confirm new password"
    )

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate that passwords match."""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordResetCompleteResponse(BaseModel):
    """
    Response after completing a password reset.
    """
    success: bool = Field(
        ...,
        description="Whether the password was reset successfully"
    )
    message: str = Field(
        ...,
        description="Status message"
    )


class PasswordResetTokenInfo(BaseModel):
    """
    Schema for password reset token information (admin view).

    Used for security auditing and monitoring.
    """
    id: int = Field(..., description="Token ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="When token was created")
    expires_at: datetime = Field(..., description="When token expires")
    used: bool = Field(..., description="Whether token has been used")
    used_at: Optional[datetime] = Field(None, description="When token was used")
    ip_address: Optional[str] = Field(None, description="IP of requester")
    is_valid: bool = Field(..., description="Whether token is currently valid")

    model_config = {"from_attributes": True}
