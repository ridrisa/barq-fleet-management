"""API Key Model for API Authentication"""
import enum
import secrets
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class ApiKeyStatus(str, enum.Enum):
    """API Key status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ApiKey(TenantMixin, BaseModel):
    """
    API Key model for programmatic API access

    API keys allow external systems and applications to access the API
    without user credentials. Each key has:
    - Unique key string (hashed for security)
    - Associated user/owner
    - Scopes/permissions
    - Expiration date
    - Usage tracking
    - Rate limits

    Use cases:
    - Third-party integrations
    - Mobile applications
    - Backend services
    - Automation scripts
    """
    __tablename__ = "api_keys"

    # Basic fields
    name = Column(String(100), nullable=False)  # Descriptive name for the key
    key_prefix = Column(String(10), nullable=False, index=True)  # First 8 chars for identification
    key_hash = Column(String(255), nullable=False, unique=True, index=True)  # Hashed full key
    description = Column(Text, nullable=True)

    # Owner
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="api_keys")

    # Status and expiration
    status = Column(String(20), default=ApiKeyStatus.ACTIVE.value, nullable=False)
    expires_at = Column(DateTime, nullable=True)  # None = no expiration
    last_used_at = Column(DateTime, nullable=True)

    # Permissions and scoping
    scopes = Column(JSON, default=list, nullable=False)  # List of allowed scopes/permissions
    ip_whitelist = Column(JSON, default=list, nullable=True)  # Allowed IP addresses (empty = any)

    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60, nullable=False)
    rate_limit_per_hour = Column(Integer, default=1000, nullable=False)
    rate_limit_per_day = Column(Integer, default=10000, nullable=False)

    # Usage tracking
    total_requests = Column(Integer, default=0, nullable=False)
    last_request_ip = Column(String(45), nullable=True)  # IPv6 compatible

    # Extra data
    extra_data = Column(JSON, default=dict, nullable=True)  # Additional custom data

    def __repr__(self):
        return f"<ApiKey(name={self.name}, key_prefix={self.key_prefix}, status={self.status})>"

    @staticmethod
    def generate_key() -> str:
        """Generate a secure random API key"""
        return f"barq_{secrets.token_urlsafe(32)}"

    def is_active(self) -> bool:
        """Check if API key is currently active"""
        if self.status != ApiKeyStatus.ACTIVE.value:
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True

    def has_scope(self, scope: str) -> bool:
        """Check if API key has a specific scope"""
        return scope in self.scopes

    def is_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        if not self.ip_whitelist or len(self.ip_whitelist) == 0:
            return True  # No whitelist = allow all
        return ip_address in self.ip_whitelist

    def increment_usage(self, ip_address: str = None):
        """Increment usage counter and update last used timestamp"""
        self.total_requests += 1
        self.last_used_at = datetime.utcnow()
        if ip_address:
            self.last_request_ip = ip_address
