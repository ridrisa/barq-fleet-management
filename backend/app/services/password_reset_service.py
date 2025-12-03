"""
Password Reset Service

Handles secure password reset token generation, validation, and consumption.

Security features:
- Cryptographically secure token generation
- SHA-256 hashing of tokens (raw tokens never stored)
- Single-use tokens with automatic invalidation
- Configurable expiration (default: 24 hours)
- Audit trail with IP and user agent
- Automatic invalidation of existing tokens on new request

Author: BARQ Security Team
Last Updated: 2025-12-03
"""

import hashlib
import logging
import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken
from app.models.user import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


class PasswordResetService:
    """
    Service for secure password reset operations.

    Usage:
        service = PasswordResetService()

        # Request password reset
        raw_token, token_record = service.create_reset_token(db, user)
        # Send raw_token to user via email

        # Validate token (when user clicks reset link)
        token_record = service.validate_token(db, raw_token)
        if token_record:
            # Show password reset form

        # Complete reset (when user submits new password)
        success = service.consume_token(db, token_record, new_password)
    """

    # Token configuration
    TOKEN_LENGTH_BYTES = 32  # 256 bits of entropy
    DEFAULT_EXPIRE_HOURS = 24

    @staticmethod
    def generate_token() -> Tuple[str, str]:
        """
        Generate a secure reset token and its hash.

        Uses secrets.token_urlsafe for cryptographically secure random token
        and SHA-256 for hashing. The raw token is URL-safe for use in email links.

        Returns:
            Tuple of (raw_token, token_hash)
            - raw_token: Send this to user via email (URL-safe)
            - token_hash: Store this in database (SHA-256 hex digest)
        """
        raw_token = secrets.token_urlsafe(PasswordResetService.TOKEN_LENGTH_BYTES)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        return raw_token, token_hash

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """
        Hash a raw token for comparison.

        Args:
            raw_token: The raw token received from user

        Returns:
            SHA-256 hex digest of the token
        """
        return hashlib.sha256(raw_token.encode()).hexdigest()

    def create_reset_token(
        self,
        db: Session,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expire_hours: int = DEFAULT_EXPIRE_HOURS,
    ) -> Tuple[str, PasswordResetToken]:
        """
        Create a password reset token for a user.

        This method:
        1. Invalidates any existing unused tokens for this user
        2. Generates a new secure token
        3. Stores the token hash (never the raw token)
        4. Returns the raw token for sending via email

        Args:
            db: Database session
            user: User requesting reset
            ip_address: Client IP address for audit
            user_agent: Client user agent for audit
            expire_hours: Token expiration in hours (default: 24)

        Returns:
            Tuple of (raw_token, token_record)
            - raw_token: Send this to user via email
            - token_record: Database record (for reference only)

        Example:
            raw_token, _ = service.create_reset_token(
                db,
                user,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent"),
            )
            await send_reset_email(user.email, raw_token)
        """
        # Invalidate any existing unused tokens for this user (security measure)
        invalidated_count = db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,
        ).update({
            "used": True,
            "used_at": datetime.now(timezone.utc)
        })

        if invalidated_count > 0:
            logger.info(
                f"Invalidated {invalidated_count} existing reset token(s) for user {user.id}"
            )

        # Generate new token
        raw_token, token_hash = self.generate_token()

        # Create token record
        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=PasswordResetToken.create_expiration(expire_hours),
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,  # Truncate if needed
        )

        db.add(token_record)
        db.commit()
        db.refresh(token_record)

        logger.info(
            f"Created password reset token for user {user.id}, "
            f"expires in {expire_hours} hours"
        )

        return raw_token, token_record

    def validate_token(
        self,
        db: Session,
        raw_token: str
    ) -> Optional[PasswordResetToken]:
        """
        Validate a password reset token.

        Checks that the token:
        1. Exists in database
        2. Has not been used
        3. Has not expired

        Args:
            db: Database session
            raw_token: Raw token from user (from email link)

        Returns:
            Token record if valid, None otherwise

        Example:
            token_record = service.validate_token(db, raw_token)
            if not token_record:
                raise HTTPException(400, "Invalid or expired reset token")
        """
        token_hash = self.hash_token(raw_token)

        token_record = db.query(PasswordResetToken).filter(
            PasswordResetToken.token_hash == token_hash,
        ).first()

        if not token_record:
            logger.warning(f"Password reset token not found: {token_hash[:16]}...")
            return None

        if not token_record.is_valid:
            reason = "used" if token_record.used else "expired"
            logger.warning(
                f"Invalid password reset token for user {token_record.user_id}: {reason}"
            )
            return None

        logger.info(
            f"Password reset token validated for user {token_record.user_id}"
        )
        return token_record

    def consume_token(
        self,
        db: Session,
        token_record: PasswordResetToken,
        new_password: str,
    ) -> bool:
        """
        Consume a reset token and update user password.

        This method:
        1. Verifies the token is still valid
        2. Updates the user's password
        3. Marks the token as used
        4. Commits the transaction atomically

        Args:
            db: Database session
            token_record: Valid token record from validate_token()
            new_password: New password to set (will be hashed)

        Returns:
            True if successful, False otherwise

        Example:
            token_record = service.validate_token(db, raw_token)
            if token_record:
                success = service.consume_token(db, token_record, new_password)
                if success:
                    return {"message": "Password reset successfully"}
        """
        # Double-check validity (in case of race conditions)
        if not token_record.is_valid:
            logger.warning(
                f"Attempted to consume invalid token for user {token_record.user_id}"
            )
            return False

        # Get the user
        user = db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            logger.error(
                f"User not found for password reset token: {token_record.user_id}"
            )
            return False

        # Update user password
        user.hashed_password = get_password_hash(new_password)

        # Mark token as used
        token_record.used = True
        token_record.used_at = datetime.now(timezone.utc)

        # Commit transaction
        db.commit()

        logger.info(
            f"Password reset completed for user {user.id} ({user.email})"
        )

        return True

    def cleanup_expired_tokens(
        self,
        db: Session,
        days_old: int = 7
    ) -> int:
        """
        Clean up old expired/used tokens.

        This method should be run periodically (e.g., daily cron job)
        to clean up old tokens and maintain database performance.

        Args:
            db: Database session
            days_old: Delete tokens older than this many days (default: 7)

        Returns:
            Number of tokens deleted

        Example:
            # In a scheduled task
            deleted = service.cleanup_expired_tokens(db, days_old=30)
            logger.info(f"Cleaned up {deleted} old password reset tokens")
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)

        deleted_count = db.query(PasswordResetToken).filter(
            PasswordResetToken.created_at < cutoff,
        ).delete()

        db.commit()

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old password reset tokens")

        return deleted_count

    def get_user_token_history(
        self,
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> list:
        """
        Get recent password reset token history for a user.

        Useful for security auditing and detecting suspicious activity.

        Args:
            db: Database session
            user_id: User ID to query
            limit: Maximum number of records to return

        Returns:
            List of PasswordResetToken records
        """
        return db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
        ).order_by(
            PasswordResetToken.created_at.desc()
        ).limit(limit).all()


# Global service instance for convenience
password_reset_service = PasswordResetService()
