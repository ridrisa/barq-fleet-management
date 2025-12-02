"""
Session Management System

This module provides enterprise-grade session management:
- Redis-based session storage for scalability
- Session lifecycle management (create, renew, destroy)
- Concurrent session limits per user
- Session fingerprinting for security
- Device tracking and management
- Automatic session cleanup

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

import redis

from app.config.settings import settings
from app.core.security_config import security_config


@dataclass
class Session:
    """Session data structure"""
    session_id: str
    user_id: int
    username: str
    organization_id: Optional[int]
    ip_address: str
    user_agent: str
    fingerprint: str
    created_at: str
    last_activity: str
    expires_at: str
    metadata: Dict[str, Any]

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Create from dictionary"""
        return cls(**data)


class SessionManager:
    """
    Redis-based session manager with advanced security features

    Features:
    - Session creation with fingerprinting
    - Concurrent session limits
    - Automatic expiration and renewal
    - Device tracking
    - IP binding (optional)
    - User agent validation
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize session manager

        Args:
            redis_client: Optional Redis client
        """
        if redis_client:
            self.redis = redis_client
        else:
            redis_url = security_config.rate_limit.storage_uri or settings.REDIS_URL
            if redis_url:
                self.redis = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                # Fall back to in-memory (development only)
                self.redis = None
                self._memory_storage: Dict[str, str] = {}

    def create_session(
        self,
        user_id: int,
        username: str,
        organization_id: Optional[int],
        ip_address: str,
        user_agent: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Session]:
        """
        Create new session

        Args:
            user_id: User ID
            username: Username
            organization_id: Organization ID
            ip_address: Client IP address
            user_agent: User agent string
            metadata: Additional session metadata

        Returns:
            Created Session object or None if limit exceeded
        """
        # Check concurrent session limit
        active_sessions = self.get_user_sessions(user_id)
        if len(active_sessions) >= security_config.session.max_concurrent_sessions:
            # Remove oldest session
            oldest = min(active_sessions, key=lambda s: s.created_at)
            self.destroy_session(oldest.session_id)

        # Generate session ID and fingerprint
        session_id = self._generate_session_id()
        fingerprint = self._generate_fingerprint(ip_address, user_agent)

        # Calculate expiration
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=security_config.session.session_lifetime_hours)

        # Create session object
        session = Session(
            session_id=session_id,
            user_id=user_id,
            username=username,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            fingerprint=fingerprint,
            created_at=now.isoformat(),
            last_activity=now.isoformat(),
            expires_at=expires_at.isoformat(),
            metadata=metadata or {}
        )

        # Store session
        self._store_session(session)

        # Track user sessions
        self._add_to_user_sessions(user_id, session_id)

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Retrieve session by ID

        Args:
            session_id: Session ID

        Returns:
            Session object or None if not found/expired
        """
        key = f"session:{session_id}"

        if self.redis:
            data = self.redis.get(key)
            if not data:
                return None
        else:
            data = self._memory_storage.get(key)
            if not data:
                return None

        session_dict = json.loads(data)
        session = Session.from_dict(session_dict)

        # Check expiration
        if datetime.fromisoformat(session.expires_at) < datetime.utcnow():
            self.destroy_session(session_id)
            return None

        return session

    def validate_session(
        self,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Session]:
        """
        Validate session and optionally check IP/user agent

        Args:
            session_id: Session ID
            ip_address: Client IP (optional, for IP binding check)
            user_agent: User agent (optional, for validation)

        Returns:
            Session object if valid, None otherwise
        """
        session = self.get_session(session_id)
        if not session:
            return None

        # IP binding check
        if security_config.session.enforce_ip_binding and ip_address:
            if session.ip_address != ip_address:
                # IP changed - potential session hijacking
                self.destroy_session(session_id)
                return None

        # User agent binding check
        if security_config.session.enforce_user_agent_binding and user_agent:
            if session.user_agent != user_agent:
                # User agent changed - potential session hijacking
                self.destroy_session(session_id)
                return None

        # Update last activity
        self.update_activity(session_id)

        return session

    def update_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp

        Args:
            session_id: Session ID

        Returns:
            True if updated successfully
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.last_activity = datetime.utcnow().isoformat()

        # Check if renewal is needed
        last_activity = datetime.fromisoformat(session.last_activity)
        expires_at = datetime.fromisoformat(session.expires_at)
        threshold = timedelta(minutes=security_config.session.session_renewal_threshold_minutes)

        if expires_at - datetime.utcnow() < threshold:
            # Renew session
            new_expires = datetime.utcnow() + timedelta(
                hours=security_config.session.session_lifetime_hours
            )
            session.expires_at = new_expires.isoformat()

        self._store_session(session)
        return True

    def destroy_session(self, session_id: str) -> bool:
        """
        Destroy session

        Args:
            session_id: Session ID

        Returns:
            True if destroyed successfully
        """
        session = self.get_session(session_id)
        if not session:
            return False

        # Remove session data
        key = f"session:{session_id}"
        if self.redis:
            self.redis.delete(key)
        else:
            self._memory_storage.pop(key, None)

        # Remove from user sessions
        self._remove_from_user_sessions(session.user_id, session_id)

        return True

    def destroy_user_sessions(self, user_id: int) -> int:
        """
        Destroy all sessions for a user

        Args:
            user_id: User ID

        Returns:
            Number of sessions destroyed
        """
        sessions = self.get_user_sessions(user_id)
        count = 0

        for session in sessions:
            if self.destroy_session(session.session_id):
                count += 1

        return count

    def get_user_sessions(self, user_id: int) -> List[Session]:
        """
        Get all active sessions for a user

        Args:
            user_id: User ID

        Returns:
            List of Session objects
        """
        key = f"user_sessions:{user_id}"

        if self.redis:
            session_ids = self.redis.smembers(key)
        else:
            session_ids_str = self._memory_storage.get(key, "[]")
            session_ids = json.loads(session_ids_str)

        sessions = []
        for session_id in session_ids:
            session = self.get_session(session_id)
            if session:
                sessions.append(session)
            else:
                # Clean up expired session reference
                self._remove_from_user_sessions(user_id, session_id)

        return sessions

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session information for display

        Args:
            session_id: Session ID

        Returns:
            Session info dictionary
        """
        session = self.get_session(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id[:16] + "...",  # Truncate for security
            "created_at": session.created_at,
            "last_activity": session.last_activity,
            "expires_at": session.expires_at,
            "ip_address": session.ip_address,
            "user_agent": session.user_agent[:100],  # Truncate
            "is_current": False,  # Set by caller
        }

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (should be run periodically)

        Returns:
            Number of sessions cleaned up
        """
        # This is a simplified version
        # In production, implement with Redis SCAN to avoid blocking
        count = 0

        if self.redis:
            # Get all session keys
            pattern = "session:*"
            for key in self.redis.scan_iter(match=pattern):
                try:
                    data = self.redis.get(key)
                    if data:
                        session_dict = json.loads(data)
                        expires_at = datetime.fromisoformat(session_dict["expires_at"])

                        if expires_at < datetime.utcnow():
                            session_id = key.split(":", 1)[1]
                            self.destroy_session(session_id)
                            count += 1
                except:
                    # Invalid session data, remove it
                    self.redis.delete(key)
                    count += 1

        return count

    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        import secrets
        return secrets.token_urlsafe(32)

    def _generate_fingerprint(self, ip_address: str, user_agent: str) -> str:
        """
        Generate session fingerprint for security

        Args:
            ip_address: Client IP
            user_agent: User agent

        Returns:
            Fingerprint hash
        """
        fingerprint_data = f"{ip_address}:{user_agent}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()

    def _store_session(self, session: Session):
        """Store session in Redis/memory"""
        key = f"session:{session.session_id}"
        data = json.dumps(session.to_dict())

        # Calculate TTL
        expires_at = datetime.fromisoformat(session.expires_at)
        ttl = int((expires_at - datetime.utcnow()).total_seconds())

        if self.redis:
            self.redis.setex(key, ttl, data)
        else:
            self._memory_storage[key] = data

    def _add_to_user_sessions(self, user_id: int, session_id: str):
        """Add session to user's session set"""
        key = f"user_sessions:{user_id}"

        if self.redis:
            self.redis.sadd(key, session_id)
            # Set expiration on user sessions set
            self.redis.expire(key, security_config.session.session_lifetime_hours * 3600)
        else:
            sessions_str = self._memory_storage.get(key, "[]")
            sessions = json.loads(sessions_str)
            if session_id not in sessions:
                sessions.append(session_id)
            self._memory_storage[key] = json.dumps(sessions)

    def _remove_from_user_sessions(self, user_id: int, session_id: str):
        """Remove session from user's session set"""
        key = f"user_sessions:{user_id}"

        if self.redis:
            self.redis.srem(key, session_id)
        else:
            sessions_str = self._memory_storage.get(key, "[]")
            sessions = json.loads(sessions_str)
            if session_id in sessions:
                sessions.remove(session_id)
            self._memory_storage[key] = json.dumps(sessions)


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """
    Get global session manager instance

    Returns:
        SessionManager instance
    """
    global _session_manager

    if _session_manager is None:
        _session_manager = SessionManager()

    return _session_manager


# Convenience functions
def create_session(user_id: int, username: str, organization_id: int, ip: str, ua: str) -> Optional[Session]:
    """Convenience function to create session"""
    return get_session_manager().create_session(user_id, username, organization_id, ip, ua)


def validate_session(session_id: str, ip: str = None, ua: str = None) -> Optional[Session]:
    """Convenience function to validate session"""
    return get_session_manager().validate_session(session_id, ip, ua)


def destroy_session(session_id: str) -> bool:
    """Convenience function to destroy session"""
    return get_session_manager().destroy_session(session_id)


def logout_all_devices(user_id: int) -> int:
    """Convenience function to logout from all devices"""
    return get_session_manager().destroy_user_sessions(user_id)
