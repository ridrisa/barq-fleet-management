"""API Key Schemas"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ApiKeyBase(BaseModel):
    """Base API Key schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Descriptive name for the API key")
    description: Optional[str] = Field(None, description="Detailed description of the API key's purpose")
    scopes: List[str] = Field(default_factory=list, description="List of allowed scopes/permissions")
    ip_whitelist: Optional[List[str]] = Field(default_factory=list, description="Allowed IP addresses")
    rate_limit_per_minute: int = Field(60, ge=1, le=1000, description="Requests per minute limit")
    rate_limit_per_hour: int = Field(1000, ge=1, le=100000, description="Requests per hour limit")
    rate_limit_per_day: int = Field(10000, ge=1, le=1000000, description="Requests per day limit")
    expires_at: Optional[datetime] = Field(None, description="Expiration date (None = no expiration)")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional custom data")


class ApiKeyCreate(ApiKeyBase):
    """Schema for creating an API key"""
    pass


class ApiKeyUpdate(BaseModel):
    """Schema for updating an API key"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    scopes: Optional[List[str]] = None
    ip_whitelist: Optional[List[str]] = None
    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    rate_limit_per_hour: Optional[int] = Field(None, ge=1, le=100000)
    rate_limit_per_day: Optional[int] = Field(None, ge=1, le=1000000)
    expires_at: Optional[datetime] = None
    status: Optional[str] = None
    metadata: Optional[dict] = None


class ApiKeyResponse(BaseModel):
    """Schema for API key response (without full key)"""
    id: int
    name: str
    key_prefix: str
    description: Optional[str]
    user_id: int
    status: str
    scopes: List[str]
    ip_whitelist: List[str]
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    rate_limit_per_day: int
    expires_at: Optional[datetime]
    last_used_at: Optional[datetime]
    total_requests: int
    last_request_ip: Optional[str]
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiKeyWithSecret(ApiKeyResponse):
    """Schema for API key with the full secret key (only shown once on creation)"""
    secret_key: str = Field(..., description="Full API key - save this, it won't be shown again")


class ApiKeyListResponse(BaseModel):
    """Schema for paginated API key list"""
    items: List[ApiKeyResponse]
    total: int
    skip: int
    limit: int
