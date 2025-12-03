"""
Secure Password Reset Token Model

This model stores hashed password reset tokens with expiration for secure password recovery.
The raw token is sent to the user via email; only the hash is stored in the database.

Security features:
- Only stores token hash (SHA-256), never the raw token
- Automatic expiration (24 hours default)
- Single-use enforcement via 'used' flag
- User association for audit trail
- IP address and user agent tracking for security monitoring

Author: BARQ Security Team
Last Updated: 2025-12-03
"""

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func, Index
from sqlalchemy.orm import relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class PasswordResetToken(Base):
    """
    Secure password reset token storage.

    Security features:
    - Only stores token hash (SHA-256), never the raw token
    - Automatic expiration (24 hours default)
    - Single-use enforcement via 'used' flag
    - User association for audit trail
    - IP address and user agent tracking for security monitoring

    Usage:
        # Create token (in service)
        raw_token, token_hash = generate_token()
        token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=PasswordResetToken.create_expiration(24),
        )

        # Send raw_token to user via email
        # Store token_hash in database
    """
    __tablename__ = "password_reset_tokens"

    # Table indexes for performance
    __table_args__ = (
        Index('ix_password_reset_tokens_user_id_used', 'user_id', 'used'),
        Index('ix_password_reset_tokens_expires_at', 'expires_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    token_hash = Column(
        String(256),
        nullable=False,
        unique=True,
        index=True,
        comment="SHA-256 hash of the reset token"
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Token expiration timestamp"
    )
    used = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether the token has been used"
    )
    used_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when token was used"
    )
    ip_address = Column(
        String(45),
        nullable=True,
        comment="IP address of requester (IPv6 compatible)"
    )
    user_agent = Column(
        String(500),
        nullable=True,
        comment="User agent of requester"
    )

    # Relationship to User
    user = relationship("User", back_populates="password_reset_tokens")

    @property
    def is_expired(self) -> bool:
        """
        Check if the token has expired.

        Returns:
            True if token has expired, False otherwise
        """
        now = datetime.now(timezone.utc)
        expires = self.expires_at

        # Handle timezone-naive datetime
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)

        return now > expires

    @property
    def is_valid(self) -> bool:
        """
        Check if the token is valid (not expired and not used).

        Returns:
            True if token is valid for use, False otherwise
        """
        return not self.is_expired and not self.used

    @classmethod
    def create_expiration(cls, hours: int = 24) -> datetime:
        """
        Create expiration datetime from now.

        Args:
            hours: Number of hours until expiration (default: 24)

        Returns:
            Datetime object for expiration time
        """
        return datetime.now(timezone.utc) + timedelta(hours=hours)

    def __repr__(self) -> str:
        return (
            f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, "
            f"used={self.used}, is_valid={self.is_valid})>"
        )
