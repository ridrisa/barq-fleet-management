"""System Settings Model"""

import enum

from sqlalchemy import JSON, Boolean, Column, String, Text

from app.models.base import BaseModel
from app.models.mixins import TenantMixin


class SettingType(str, enum.Enum):
    """Setting data types"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    TEXT = "text"


class SettingCategory(str, enum.Enum):
    """Setting categories for organization"""

    GENERAL = "general"
    SECURITY = "security"
    EMAIL = "email"
    SMS = "sms"
    PAYMENT = "payment"
    NOTIFICATIONS = "notifications"
    INTEGRATION = "integration"
    BACKUP = "backup"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"


class SystemSetting(TenantMixin, BaseModel):
    """
    System Settings model for application configuration

    This model stores configurable system-wide settings that control
    application behavior. Settings are organized by category and can
    be of various types.

    Examples:
    - Email configuration (SMTP server, port, credentials)
    - SMS provider settings
    - Payment gateway configuration
    - Security policies (password complexity, session timeout)
    - Feature flags
    - System limits and quotas
    - Notification preferences
    - Backup schedules
    """

    __tablename__ = "system_settings"

    # Identification
    key = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Categorization
    category = Column(String(50), nullable=False, index=True)
    setting_type = Column(String(20), nullable=False)  # string, integer, boolean, json, etc.

    # Value
    value = Column(Text, nullable=True)  # Stored as text, converted based on setting_type
    default_value = Column(Text, nullable=True)

    # JSON value for complex settings
    json_value = Column(JSON, nullable=True)

    # Metadata
    is_sensitive = Column(Boolean, default=False, nullable=False)  # If true, encrypt value
    is_editable = Column(Boolean, default=True, nullable=False)  # If false, read-only
    is_public = Column(Boolean, default=False, nullable=False)  # If true, visible to non-admins

    # Validation
    validation_regex = Column(String(500), nullable=True)  # Regex for value validation
    allowed_values = Column(JSON, nullable=True)  # List of allowed values (for enum-like settings)
    min_value = Column(String(100), nullable=True)  # Min value for numeric settings
    max_value = Column(String(100), nullable=True)  # Max value for numeric settings

    # Help text
    help_text = Column(Text, nullable=True)
    example_value = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<SystemSetting(key={self.key}, category={self.category}, type={self.setting_type})>"
        )

    def get_value(self):
        """Get typed value based on setting_type"""
        if self.value is None:
            return None

        if self.setting_type == SettingType.BOOLEAN.value:
            return self.value.lower() in ("true", "1", "yes", "on")
        elif self.setting_type == SettingType.INTEGER.value:
            return int(self.value)
        elif self.setting_type == SettingType.FLOAT.value:
            return float(self.value)
        elif self.setting_type == SettingType.JSON.value:
            return self.json_value
        else:
            return self.value

    def set_value(self, value):
        """Set value with type conversion"""
        if value is None:
            self.value = None
            self.json_value = None
            return

        if self.setting_type == SettingType.JSON.value:
            self.json_value = value
            self.value = None
        else:
            self.value = str(value)
            self.json_value = None

    def validate_value(self, value) -> tuple[bool, str]:
        """
        Validate a value against setting constraints
        Returns (is_valid, error_message)
        """
        if value is None:
            return True, ""

        # Check allowed values
        if self.allowed_values and value not in self.allowed_values:
            return False, f"Value must be one of: {', '.join(self.allowed_values)}"

        # Type-specific validation
        if self.setting_type == SettingType.INTEGER.value:
            try:
                int_value = int(value)
                if self.min_value and int_value < int(self.min_value):
                    return False, f"Value must be >= {self.min_value}"
                if self.max_value and int_value > int(self.max_value):
                    return False, f"Value must be <= {self.max_value}"
            except ValueError:
                return False, "Value must be a valid integer"

        elif self.setting_type == SettingType.FLOAT.value:
            try:
                float_value = float(value)
                if self.min_value and float_value < float(self.min_value):
                    return False, f"Value must be >= {self.min_value}"
                if self.max_value and float_value > float(self.max_value):
                    return False, f"Value must be <= {self.max_value}"
            except ValueError:
                return False, "Value must be a valid number"

        return True, ""
