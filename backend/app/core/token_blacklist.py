"""
Token Blacklist Management

This module provides token revocation and blacklisting using Redis:
- Token blacklisting (for logout, security incidents)
- Refresh token rotation tracking
- Token family invalidation (invalidate all tokens for a user)
- Automatic cleanup of expired tokens

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Set

import redis
from jose import jwt

from app.config.settings import settings
from app.core.security_config import security_config


class TokenBlacklist:
    """
    Redis-based token blacklist for JWT revocation

    Features:
    - Blacklist individual tokens
    - Blacklist all tokens for a user
    - Automatic expiration (TTL matches token expiration)
    - Token family tracking for refresh token rotation
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize token blacklist

        Args:
            redis_client: Optional Redis client (creates new if not provided)
        """
        if redis_client:
            self.redis = redis_client
        else:
            # Create Redis client from configuration
            redis_url = security_config.rate_limit.storage_uri or settings.REDIS_URL
            if not redis_url:
                # Fall back to in-memory storage (development only)
                self.redis = None
                self._memory_storage: Set[str] = set()
            else:
                self.redis = redis.from_url(
                    redis_url, decode_responses=True, socket_connect_timeout=5, socket_timeout=5
                )

    def blacklist_token(self, token: str, reason: Optional[str] = None) -> bool:
        """
        Add token to blacklist

        Args:
            token: JWT token to blacklist
            reason: Optional reason for blacklisting

        Returns:
            True if successfully blacklisted
        """
        try:
            # Extract token JTI and expiration
            payload = jwt.get_unverified_claims(token)
            jti = payload.get("jti")
            exp = payload.get("exp")

            if not jti:
                # If no JTI, use token hash
                import hashlib

                jti = hashlib.sha256(token.encode()).hexdigest()[:16]

            # Calculate TTL (time until token expires)
            if exp:
                ttl = max(0, exp - int(datetime.utcnow().timestamp()))
            else:
                # Default to access token expiration
                ttl = security_config.token.access_token_expire_minutes * 60

            # Store in Redis with expiration
            key = f"blacklist:token:{jti}"

            if self.redis:
                data = {
                    "jti": jti,
                    "reason": reason or "manual_revocation",
                    "blacklisted_at": datetime.utcnow().isoformat(),
                }
                self.redis.setex(key, ttl, json.dumps(data))
            else:
                # In-memory storage (development)
                self._memory_storage.add(jti)

            return True

        except Exception as e:
            # Log error but don't fail
            print(f"Failed to blacklist token: {str(e)}")
            return False

    def is_blacklisted(self, token: str) -> bool:
        """
        Check if token is blacklisted

        Args:
            token: JWT token to check

        Returns:
            True if blacklisted, False otherwise
        """
        try:
            # Extract JTI
            payload = jwt.get_unverified_claims(token)
            jti = payload.get("jti")

            if not jti:
                import hashlib

                jti = hashlib.sha256(token.encode()).hexdigest()[:16]

            key = f"blacklist:token:{jti}"

            if self.redis:
                return self.redis.exists(key) > 0
            else:
                return jti in self._memory_storage

        except Exception:
            # If we can't verify, assume not blacklisted (fail open)
            return False

    def blacklist_user_tokens(self, user_id: int, reason: Optional[str] = None) -> bool:
        """
        Blacklist all tokens for a user

        Use cases:
        - User logout from all devices
        - Security incident (compromised account)
        - Password change

        Args:
            user_id: User ID
            reason: Reason for blacklisting

        Returns:
            True if successful
        """
        try:
            key = f"blacklist:user:{user_id}"

            # Set a marker that all tokens for this user are invalid
            # TTL = longest possible token lifetime (refresh token)
            ttl = security_config.token.refresh_token_expire_days * 24 * 60 * 60

            if self.redis:
                data = {
                    "user_id": user_id,
                    "reason": reason or "user_logout_all",
                    "blacklisted_at": datetime.utcnow().isoformat(),
                }
                self.redis.setex(key, ttl, json.dumps(data))
            else:
                self._memory_storage.add(f"user:{user_id}")

            return True

        except Exception as e:
            print(f"Failed to blacklist user tokens: {str(e)}")
            return False

    def is_user_blacklisted(self, user_id: int) -> bool:
        """
        Check if all tokens for a user are blacklisted

        Args:
            user_id: User ID to check

        Returns:
            True if user is blacklisted
        """
        try:
            key = f"blacklist:user:{user_id}"

            if self.redis:
                return self.redis.exists(key) > 0
            else:
                return f"user:{user_id}" in self._memory_storage

        except Exception:
            return False

    def remove_user_blacklist(self, user_id: int) -> bool:
        """
        Remove user from blacklist (e.g., after password reset)

        Args:
            user_id: User ID

        Returns:
            True if successful
        """
        try:
            key = f"blacklist:user:{user_id}"

            if self.redis:
                self.redis.delete(key)
            else:
                self._memory_storage.discard(f"user:{user_id}")

            return True

        except Exception:
            return False

    def track_refresh_token_family(
        self, token_id: str, user_id: int, parent_token_id: Optional[str] = None
    ) -> bool:
        """
        Track refresh token families for rotation detection

        Detects token replay attacks:
        - If a revoked refresh token is used, invalidate entire family

        Args:
            token_id: Current token ID
            user_id: User ID
            parent_token_id: Parent token ID (if rotated from another token)

        Returns:
            True if successful
        """
        try:
            # Store token family relationship
            key = f"token_family:{token_id}"
            ttl = security_config.token.refresh_token_expire_days * 24 * 60 * 60

            if self.redis:
                data = {
                    "token_id": token_id,
                    "user_id": user_id,
                    "parent_token_id": parent_token_id,
                    "created_at": datetime.utcnow().isoformat(),
                }
                self.redis.setex(key, ttl, json.dumps(data))

            return True

        except Exception:
            return False

    def invalidate_token_family(self, token_id: str) -> bool:
        """
        Invalidate entire token family (used when refresh token replay detected)

        Args:
            token_id: Token ID that was replayed

        Returns:
            True if successful
        """
        try:
            # Get token family
            key = f"token_family:{token_id}"

            if self.redis:
                data_str = self.redis.get(key)
                if data_str:
                    data = json.loads(data_str)
                    user_id = data.get("user_id")

                    # Blacklist all tokens for this user
                    return self.blacklist_user_tokens(
                        user_id, reason="refresh_token_replay_detected"
                    )

            return False

        except Exception:
            return False

    def get_blacklist_stats(self) -> dict:
        """
        Get blacklist statistics

        Returns:
            Dictionary with statistics
        """
        try:
            if self.redis:
                # Count blacklisted tokens
                token_keys = self.redis.keys("blacklist:token:*")
                user_keys = self.redis.keys("blacklist:user:*")

                return {
                    "blacklisted_tokens": len(token_keys),
                    "blacklisted_users": len(user_keys),
                    "storage": "redis",
                }
            else:
                return {
                    "blacklisted_tokens": len(
                        [k for k in self._memory_storage if not k.startswith("user:")]
                    ),
                    "blacklisted_users": len(
                        [k for k in self._memory_storage if k.startswith("user:")]
                    ),
                    "storage": "memory",
                }

        except Exception:
            return {"blacklisted_tokens": 0, "blacklisted_users": 0, "storage": "unknown"}


# Global blacklist instance
_blacklist_instance: Optional[TokenBlacklist] = None


def get_blacklist() -> TokenBlacklist:
    """
    Get global token blacklist instance

    Returns:
        TokenBlacklist instance
    """
    global _blacklist_instance

    if _blacklist_instance is None:
        _blacklist_instance = TokenBlacklist()

    return _blacklist_instance


def blacklist_token(token: str, reason: Optional[str] = None) -> bool:
    """Convenience function to blacklist a token"""
    return get_blacklist().blacklist_token(token, reason)


def is_token_blacklisted(token: str) -> bool:
    """Convenience function to check if token is blacklisted"""
    return get_blacklist().is_blacklisted(token)


def logout_user_all_devices(user_id: int) -> bool:
    """Convenience function to logout user from all devices"""
    return get_blacklist().blacklist_user_tokens(user_id, "user_logout_all")
