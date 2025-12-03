"""Integration Schemas"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class IntegrationBase(BaseModel):
    """Base Integration schema"""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Unique integration identifier"
    )
    display_name: str = Field(..., min_length=1, max_length=100, description="Human-readable name")
    description: Optional[str] = Field(None, description="Integration description")
    integration_type: str = Field(..., description="Type of integration")
    is_enabled: bool = Field(False, description="Whether integration is enabled")
    config: Dict[str, Any] = Field(default_factory=dict, description="Integration configuration")
    base_url: Optional[str] = Field(None, description="Base URL for API calls")
    webhook_url: Optional[str] = Field(None, description="Webhook URL")
    callback_url: Optional[str] = Field(None, description="OAuth callback URL")
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, description="Rate limit per minute")
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, description="Rate limit per hour")
    rate_limit_per_day: Optional[int] = Field(None, ge=1, description="Rate limit per day")
    version: Optional[str] = Field(None, description="API version")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional metadata"
    )


class IntegrationCreate(IntegrationBase):
    """Schema for creating an integration"""

    credentials: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="API credentials"
    )
    oauth_client_id: Optional[str] = Field(None, description="OAuth client ID")
    oauth_client_secret: Optional[str] = Field(None, description="OAuth client secret")


class IntegrationUpdate(BaseModel):
    """Schema for updating an integration"""

    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    credentials: Optional[Dict[str, Any]] = None
    base_url: Optional[str] = None
    webhook_url: Optional[str] = None
    callback_url: Optional[str] = None
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1)
    rate_limit_per_day: Optional[int] = Field(None, ge=1)
    version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IntegrationResponse(BaseModel):
    """Schema for integration response"""

    id: int
    name: str
    display_name: str
    description: Optional[str]
    integration_type: str
    status: str
    is_enabled: bool
    config: Dict[str, Any]
    base_url: Optional[str]
    webhook_url: Optional[str]
    callback_url: Optional[str]
    last_health_check: Optional[datetime]
    last_error: Optional[str]
    last_error_at: Optional[datetime]
    error_count: int
    success_count: int
    rate_limit_per_minute: Optional[int]
    rate_limit_per_hour: Optional[int]
    rate_limit_per_day: Optional[int]
    version: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IntegrationTestRequest(BaseModel):
    """Schema for testing an integration"""

    test_endpoint: Optional[str] = Field(None, description="Specific endpoint to test")
    test_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Test data")


class IntegrationTestResponse(BaseModel):
    """Schema for integration test result"""

    success: bool
    message: str
    response_time_ms: Optional[int]
    status_code: Optional[int]
    response_data: Optional[Dict[str, Any]]
    error: Optional[str]


class IntegrationListResponse(BaseModel):
    """Schema for paginated integration list"""

    items: List[IntegrationResponse]
    total: int
    skip: int
    limit: int
