"""System Setting Schemas"""
from typing import Optional, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class SystemSettingBase(BaseModel):
    """Base System Setting schema"""
    key: str = Field(..., min_length=1, max_length=100, description="Unique setting key")
    name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    description: Optional[str] = Field(None, description="Setting description")
    category: str = Field(..., description="Setting category")
    setting_type: str = Field(..., description="Data type (string, integer, boolean, json, text)")
    value: Optional[str] = Field(None, description="Setting value as string")
    default_value: Optional[str] = Field(None, description="Default value")
    json_value: Optional[Any] = Field(None, description="JSON value for complex settings")
    is_sensitive: bool = Field(False, description="Whether value should be encrypted")
    is_editable: bool = Field(True, description="Whether setting can be edited")
    is_public: bool = Field(False, description="Whether visible to non-admins")
    validation_regex: Optional[str] = Field(None, description="Validation regex pattern")
    allowed_values: Optional[List[str]] = Field(None, description="List of allowed values")
    min_value: Optional[str] = Field(None, description="Minimum value")
    max_value: Optional[str] = Field(None, description="Maximum value")
    help_text: Optional[str] = Field(None, description="Help text")
    example_value: Optional[str] = Field(None, description="Example value")


class SystemSettingCreate(SystemSettingBase):
    """Schema for creating a system setting"""
    pass


class SystemSettingUpdate(BaseModel):
    """Schema for updating a system setting"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    value: Optional[str] = None
    json_value: Optional[Any] = None
    default_value: Optional[str] = None
    is_editable: Optional[bool] = None
    is_public: Optional[bool] = None
    validation_regex: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    help_text: Optional[str] = None
    example_value: Optional[str] = None


class SystemSettingResponse(BaseModel):
    """Schema for system setting response"""
    id: int
    key: str
    name: str
    description: Optional[str]
    category: str
    setting_type: str
    value: Optional[str]
    default_value: Optional[str]
    json_value: Optional[Any]
    is_sensitive: bool
    is_editable: bool
    is_public: bool
    validation_regex: Optional[str]
    allowed_values: Optional[List[str]]
    min_value: Optional[str]
    max_value: Optional[str]
    help_text: Optional[str]
    example_value: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SystemSettingListResponse(BaseModel):
    """Schema for paginated system setting list"""
    items: List[SystemSettingResponse]
    total: int
    skip: int
    limit: int


class SystemSettingBulkUpdate(BaseModel):
    """Schema for bulk updating system settings"""
    settings: List[dict] = Field(..., description="List of {key: value} pairs")
