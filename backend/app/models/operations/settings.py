"""
Operations Settings Model
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Numeric, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class OperationsSettings(BaseModel):
    """Global operations configuration settings"""

    __tablename__ = "operations_settings"

    # Setting Identification
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_name = Column(String(200), nullable=False)
    setting_group = Column(String(100), nullable=False, index=True, comment="Group: dispatch, sla, quality, zone, etc.")
    description = Column(Text)

    # Value
    value_type = Column(String(20), nullable=False, comment="string, number, boolean, json")
    string_value = Column(Text)
    number_value = Column(Numeric(20, 4))
    boolean_value = Column(Boolean)
    json_value = Column(JSON)

    # Constraints
    min_value = Column(Numeric(20, 4))
    max_value = Column(Numeric(20, 4))
    allowed_values = Column(Text, comment="Comma-separated allowed values")

    # Status
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False, comment="System setting - cannot be deleted")
    is_readonly = Column(Boolean, default=False, comment="Cannot be modified by users")

    # Audit
    last_modified_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    last_modified_at = Column(DateTime)

    def __repr__(self):
        return f"<OperationsSettings {self.setting_key}: {self.setting_name}>"

    @property
    def value(self):
        """Get the appropriate value based on value_type"""
        if self.value_type == "string":
            return self.string_value
        elif self.value_type == "number":
            return float(self.number_value) if self.number_value else None
        elif self.value_type == "boolean":
            return self.boolean_value
        elif self.value_type == "json":
            return self.json_value
        return None


class DispatchRule(BaseModel):
    """Auto-dispatch rules and algorithms"""

    __tablename__ = "dispatch_rules"

    # Rule Details
    rule_code = Column(String(50), unique=True, nullable=False, index=True)
    rule_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Rule Priority (lower number = higher priority)
    priority = Column(Integer, default=100, index=True)
    is_active = Column(Boolean, default=True, index=True)

    # Conditions (JSON)
    conditions = Column(JSON, nullable=False, comment="Conditions for rule to apply")
    # Example: {"zone_id": [1,2,3], "priority": ["urgent", "high"], "time_range": {"start": "09:00", "end": "17:00"}}

    # Actions (JSON)
    actions = Column(JSON, nullable=False, comment="Actions to take when conditions match")
    # Example: {"algorithm": "nearest", "max_distance_km": 5, "prefer_rating_above": 4.0}

    # Algorithm Settings
    algorithm = Column(String(50), default="load_balanced", comment="nearest, load_balanced, priority_based, round_robin")
    max_distance_km = Column(Numeric(10, 2), default=10.0)
    max_courier_load = Column(Integer, default=5)
    min_courier_rating = Column(Numeric(3, 2))

    # Zone Restrictions
    zone_ids = Column(Text, comment="Comma-separated zone IDs this rule applies to")
    applies_to_all_zones = Column(Boolean, default=True)

    # Time Restrictions
    time_start = Column(String(8), comment="Start time HH:MM:SS")
    time_end = Column(String(8), comment="End time HH:MM:SS")
    days_of_week = Column(String(20), comment="Comma-separated days: mon,tue,wed,etc.")

    # Performance Tracking
    times_triggered = Column(Integer, default=0)
    successful_assignments = Column(Integer, default=0)
    failed_assignments = Column(Integer, default=0)

    # Audit
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

    def __repr__(self):
        return f"<DispatchRule {self.rule_code}: {self.rule_name}>"


class SLAThreshold(BaseModel):
    """SLA threshold configurations"""

    __tablename__ = "sla_thresholds"

    # Threshold Details
    threshold_code = Column(String(50), unique=True, nullable=False, index=True)
    threshold_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Type
    sla_type = Column(String(50), nullable=False, index=True, comment="delivery_time, response_time, pickup_time")
    service_type = Column(String(50), index=True, comment="express, standard, economy")

    # Target Values (in minutes)
    target_minutes = Column(Integer, nullable=False, comment="Target SLA in minutes")
    warning_minutes = Column(Integer, nullable=False, comment="Warning threshold in minutes")
    critical_minutes = Column(Integer, nullable=False, comment="Critical threshold in minutes")

    # Zone Specific
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="CASCADE"), index=True)
    applies_to_all_zones = Column(Boolean, default=True)

    # Penalty
    penalty_amount = Column(Numeric(10, 2), default=0.0)
    escalation_required = Column(Boolean, default=True)

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    zone = relationship("Zone")

    def __repr__(self):
        return f"<SLAThreshold {self.threshold_code}: {self.threshold_name}>"


class NotificationSetting(BaseModel):
    """Notification settings for operations events"""

    __tablename__ = "notification_settings"

    # Setting Details
    setting_code = Column(String(50), unique=True, nullable=False, index=True)
    setting_name = Column(String(200), nullable=False)
    event_type = Column(String(100), nullable=False, index=True, comment="Event that triggers notification")
    # Events: sla_warning, sla_breach, dispatch_failed, queue_escalation, quality_failed, etc.

    # Notification Channels
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_push = Column(Boolean, default=True)
    notify_in_app = Column(Boolean, default=True)
    notify_webhook = Column(Boolean, default=False)

    # Recipients
    notify_roles = Column(Text, comment="Comma-separated roles to notify")
    notify_user_ids = Column(Text, comment="Comma-separated user IDs to notify")
    webhook_url = Column(String(500))

    # Timing
    cooldown_minutes = Column(Integer, default=0, comment="Minimum time between notifications")
    batch_delay_minutes = Column(Integer, default=0, comment="Batch notifications within this window")

    # Template
    email_template = Column(String(100), comment="Email template ID")
    sms_template = Column(String(100), comment="SMS template ID")

    # Status
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<NotificationSetting {self.setting_code}: {self.event_type}>"


class ZoneDefault(BaseModel):
    """Default settings for new zones"""

    __tablename__ = "zone_defaults"

    # Default Details
    default_code = Column(String(50), unique=True, nullable=False, index=True)
    default_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Capacity Defaults
    default_max_couriers = Column(Integer, default=10)
    default_priority_level = Column(Integer, default=3)

    # Pricing Defaults
    default_service_fee = Column(Numeric(10, 2), default=0.0)
    default_peak_multiplier = Column(Numeric(5, 2), default=1.5)
    default_minimum_order = Column(Numeric(10, 2), default=0.0)

    # SLA Defaults
    default_delivery_time_minutes = Column(Integer, default=60)
    default_sla_target_minutes = Column(Integer, default=45)

    # Operating Hours
    operating_start = Column(String(8), default="08:00:00")
    operating_end = Column(String(8), default="22:00:00")

    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False, comment="Default template to use")

    def __repr__(self):
        return f"<ZoneDefault {self.default_code}: {self.default_name}>"
