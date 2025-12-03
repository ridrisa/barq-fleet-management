"""Integration Model for Third-Party Services"""

import enum
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class IntegrationType(str, enum.Enum):
    """Types of integrations"""

    PAYMENT_GATEWAY = "payment_gateway"
    SMS_PROVIDER = "sms_provider"
    EMAIL_PROVIDER = "email_provider"
    MAPPING_SERVICE = "mapping_service"
    CLOUD_STORAGE = "cloud_storage"
    ANALYTICS = "analytics"
    CRM = "crm"
    ERP = "erp"
    WEBHOOK = "webhook"
    OAUTH_PROVIDER = "oauth_provider"
    CUSTOM = "custom"


class IntegrationStatus(str, enum.Enum):
    """Integration status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class Integration(TenantMixin, BaseModel):
    """
    Integration model for managing third-party service integrations

    This model stores configuration and credentials for external services
    that the BARQ Fleet Management system integrates with.

    Examples:
    - Payment gateways (Stripe, PayPal)
    - SMS providers (Twilio, MessageBird)
    - Email services (SendGrid, AWS SES)
    - Mapping services (Google Maps, Mapbox)
    - Cloud storage (AWS S3, Google Cloud Storage)
    - Analytics platforms
    """

    __tablename__ = "integrations"

    # Basic information
    name = Column(String(100), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    integration_type = Column(String(50), nullable=False, index=True)

    # Status
    status = Column(String(20), default=IntegrationStatus.INACTIVE.value, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)

    # Configuration
    config = Column(JSON, default=dict, nullable=False)  # Integration-specific configuration
    credentials = Column(
        JSON, default=dict, nullable=True
    )  # Encrypted credentials (API keys, tokens)

    # Endpoints and URLs
    base_url = Column(String(500), nullable=True)
    webhook_url = Column(String(500), nullable=True)
    callback_url = Column(String(500), nullable=True)

    # OAuth specific
    oauth_client_id = Column(String(255), nullable=True)
    oauth_client_secret = Column(String(255), nullable=True)  # Should be encrypted
    oauth_access_token = Column(Text, nullable=True)  # Should be encrypted
    oauth_refresh_token = Column(Text, nullable=True)  # Should be encrypted
    oauth_token_expires_at = Column(DateTime, nullable=True)

    # Health and monitoring
    last_health_check = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)

    # Rate limiting
    rate_limit_per_minute = Column(Integer, nullable=True)
    rate_limit_per_hour = Column(Integer, nullable=True)
    rate_limit_per_day = Column(Integer, nullable=True)

    # Extra data
    version = Column(String(20), nullable=True)  # Integration version/API version
    extra_data = Column(JSON, default=dict, nullable=True)

    def __repr__(self):
        return (
            f"<Integration(name={self.name}, type={self.integration_type}, status={self.status})>"
        )

    def is_healthy(self) -> bool:
        """Check if integration is healthy"""
        return self.status == IntegrationStatus.ACTIVE.value and self.is_enabled

    def record_success(self):
        """Record successful API call"""
        self.success_count += 1
        self.last_health_check = datetime.utcnow()
        if self.status == IntegrationStatus.ERROR.value:
            self.status = IntegrationStatus.ACTIVE.value
            self.error_count = 0
            self.last_error = None

    def record_error(self, error_message: str):
        """Record failed API call"""
        self.error_count += 1
        self.last_error = error_message
        self.last_error_at = datetime.utcnow()
        if self.error_count >= 5:  # Threshold for marking as ERROR
            self.status = IntegrationStatus.ERROR.value

    def needs_oauth_refresh(self) -> bool:
        """Check if OAuth token needs refresh"""
        if not self.oauth_token_expires_at:
            return False
        return datetime.utcnow() >= self.oauth_token_expires_at
