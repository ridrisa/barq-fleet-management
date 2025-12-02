"""
Operations Settings Schemas
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal


# Operations Settings Schemas
class OperationsSettingsBase(BaseModel):
    setting_key: str = Field(..., min_length=2, max_length=100)
    setting_name: str = Field(..., min_length=3, max_length=200)
    setting_group: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    value_type: str = Field(..., pattern="^(string|number|boolean|json)$")


class OperationsSettingsCreate(OperationsSettingsBase):
    string_value: Optional[str] = None
    number_value: Optional[Decimal] = None
    boolean_value: Optional[bool] = None
    json_value: Optional[Dict[str, Any]] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    allowed_values: Optional[str] = None
    is_system: bool = False
    is_readonly: bool = False


class OperationsSettingsUpdate(BaseModel):
    setting_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    string_value: Optional[str] = None
    number_value: Optional[Decimal] = None
    boolean_value: Optional[bool] = None
    json_value: Optional[Dict[str, Any]] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    allowed_values: Optional[str] = None
    is_active: Optional[bool] = None


class OperationsSettingsResponse(OperationsSettingsBase):
    id: int
    string_value: Optional[str] = None
    number_value: Optional[Decimal] = None
    boolean_value: Optional[bool] = None
    json_value: Optional[Dict[str, Any]] = None
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    allowed_values: Optional[str] = None
    is_active: bool
    is_system: bool
    is_readonly: bool
    last_modified_by_id: Optional[int] = None
    last_modified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SettingValue(BaseModel):
    """Schema for setting a value"""
    value: Union[str, int, float, bool, Dict[str, Any]]


# Dispatch Rule Schemas
class DispatchRuleBase(BaseModel):
    rule_code: str = Field(..., min_length=2, max_length=50)
    rule_name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    priority: int = Field(100, ge=1, le=1000)
    algorithm: str = Field("load_balanced", pattern="^(nearest|load_balanced|priority_based|round_robin|ai_optimized)$")
    max_distance_km: Optional[Decimal] = Field(None, ge=0, le=100)
    max_courier_load: Optional[int] = Field(None, ge=1, le=20)
    min_courier_rating: Optional[Decimal] = Field(None, ge=0, le=5)


class DispatchRuleCreate(DispatchRuleBase):
    conditions: Dict[str, Any] = Field(..., description="Conditions for rule to apply")
    actions: Dict[str, Any] = Field(..., description="Actions to take")
    zone_ids: Optional[str] = None
    applies_to_all_zones: bool = True
    time_start: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$")
    time_end: Optional[str] = Field(None, pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$")
    days_of_week: Optional[str] = None
    is_active: bool = True


class DispatchRuleUpdate(BaseModel):
    rule_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=1000)
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[Dict[str, Any]] = None
    algorithm: Optional[str] = Field(None, pattern="^(nearest|load_balanced|priority_based|round_robin|ai_optimized)$")
    max_distance_km: Optional[Decimal] = Field(None, ge=0, le=100)
    max_courier_load: Optional[int] = Field(None, ge=1, le=20)
    min_courier_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    zone_ids: Optional[str] = None
    applies_to_all_zones: Optional[bool] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    days_of_week: Optional[str] = None
    is_active: Optional[bool] = None


class DispatchRuleResponse(DispatchRuleBase):
    id: int
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    zone_ids: Optional[str] = None
    applies_to_all_zones: bool
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    days_of_week: Optional[str] = None
    is_active: bool
    times_triggered: int
    successful_assignments: int
    failed_assignments: int
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# SLA Threshold Schemas
class SLAThresholdBase(BaseModel):
    threshold_code: str = Field(..., min_length=2, max_length=50)
    threshold_name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    sla_type: str = Field(..., pattern="^(delivery_time|response_time|pickup_time|resolution_time)$")
    service_type: Optional[str] = Field(None, pattern="^(express|standard|economy)$")
    target_minutes: int = Field(..., ge=1, le=10000)
    warning_minutes: int = Field(..., ge=1, le=10000)
    critical_minutes: int = Field(..., ge=1, le=10000)

    @field_validator('warning_minutes')
    @classmethod
    def warning_less_than_target(cls, v, info):
        target = info.data.get('target_minutes')
        if target and v >= target:
            raise ValueError('Warning minutes must be less than target minutes')
        return v


class SLAThresholdCreate(SLAThresholdBase):
    zone_id: Optional[int] = None
    applies_to_all_zones: bool = True
    penalty_amount: Decimal = Field(Decimal("0.0"), ge=0)
    escalation_required: bool = True
    is_active: bool = True


class SLAThresholdUpdate(BaseModel):
    threshold_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    service_type: Optional[str] = None
    target_minutes: Optional[int] = Field(None, ge=1, le=10000)
    warning_minutes: Optional[int] = Field(None, ge=1, le=10000)
    critical_minutes: Optional[int] = Field(None, ge=1, le=10000)
    zone_id: Optional[int] = None
    applies_to_all_zones: Optional[bool] = None
    penalty_amount: Optional[Decimal] = Field(None, ge=0)
    escalation_required: Optional[bool] = None
    is_active: Optional[bool] = None


class SLAThresholdResponse(SLAThresholdBase):
    id: int
    zone_id: Optional[int] = None
    applies_to_all_zones: bool
    penalty_amount: Decimal
    escalation_required: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Notification Setting Schemas
class NotificationSettingBase(BaseModel):
    setting_code: str = Field(..., min_length=2, max_length=50)
    setting_name: str = Field(..., min_length=3, max_length=200)
    event_type: str = Field(..., min_length=3, max_length=100)


class NotificationSettingCreate(NotificationSettingBase):
    notify_email: bool = True
    notify_sms: bool = False
    notify_push: bool = True
    notify_in_app: bool = True
    notify_webhook: bool = False
    notify_roles: Optional[str] = None
    notify_user_ids: Optional[str] = None
    webhook_url: Optional[str] = Field(None, max_length=500)
    cooldown_minutes: int = Field(0, ge=0, le=1440)
    batch_delay_minutes: int = Field(0, ge=0, le=60)
    email_template: Optional[str] = Field(None, max_length=100)
    sms_template: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class NotificationSettingUpdate(BaseModel):
    setting_name: Optional[str] = Field(None, min_length=3, max_length=200)
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    notify_push: Optional[bool] = None
    notify_in_app: Optional[bool] = None
    notify_webhook: Optional[bool] = None
    notify_roles: Optional[str] = None
    notify_user_ids: Optional[str] = None
    webhook_url: Optional[str] = Field(None, max_length=500)
    cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440)
    batch_delay_minutes: Optional[int] = Field(None, ge=0, le=60)
    email_template: Optional[str] = None
    sms_template: Optional[str] = None
    is_active: Optional[bool] = None


class NotificationSettingResponse(NotificationSettingBase):
    id: int
    notify_email: bool
    notify_sms: bool
    notify_push: bool
    notify_in_app: bool
    notify_webhook: bool
    notify_roles: Optional[str] = None
    notify_user_ids: Optional[str] = None
    webhook_url: Optional[str] = None
    cooldown_minutes: int
    batch_delay_minutes: int
    email_template: Optional[str] = None
    sms_template: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Zone Default Schemas
class ZoneDefaultBase(BaseModel):
    default_code: str = Field(..., min_length=2, max_length=50)
    default_name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None


class ZoneDefaultCreate(ZoneDefaultBase):
    default_max_couriers: int = Field(10, ge=1, le=100)
    default_priority_level: int = Field(3, ge=1, le=5)
    default_service_fee: Decimal = Field(Decimal("0.0"), ge=0)
    default_peak_multiplier: Decimal = Field(Decimal("1.5"), ge=1, le=5)
    default_minimum_order: Decimal = Field(Decimal("0.0"), ge=0)
    default_delivery_time_minutes: int = Field(60, ge=10, le=1440)
    default_sla_target_minutes: int = Field(45, ge=5, le=1440)
    operating_start: str = Field("08:00:00", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$")
    operating_end: str = Field("22:00:00", pattern="^([0-1]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$")
    is_active: bool = True
    is_default: bool = False


class ZoneDefaultUpdate(BaseModel):
    default_name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    default_max_couriers: Optional[int] = Field(None, ge=1, le=100)
    default_priority_level: Optional[int] = Field(None, ge=1, le=5)
    default_service_fee: Optional[Decimal] = Field(None, ge=0)
    default_peak_multiplier: Optional[Decimal] = Field(None, ge=1, le=5)
    default_minimum_order: Optional[Decimal] = Field(None, ge=0)
    default_delivery_time_minutes: Optional[int] = Field(None, ge=10, le=1440)
    default_sla_target_minutes: Optional[int] = Field(None, ge=5, le=1440)
    operating_start: Optional[str] = None
    operating_end: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class ZoneDefaultResponse(ZoneDefaultBase):
    id: int
    default_max_couriers: int
    default_priority_level: int
    default_service_fee: Decimal
    default_peak_multiplier: Decimal
    default_minimum_order: Decimal
    default_delivery_time_minutes: int
    default_sla_target_minutes: int
    operating_start: str
    operating_end: str
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Settings Group Schema
class SettingsGroup(BaseModel):
    """Group of related settings"""
    group_name: str
    settings: List[OperationsSettingsResponse]

    model_config = ConfigDict(from_attributes=True)
