"""
Operations Settings API Routes
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_organization, get_current_user
from app.crud.operations.settings import (
    dispatch_rule,
    notification_setting,
    operations_settings,
    sla_threshold,
    zone_default,
)
from app.models.tenant.organization import Organization
from app.schemas.operations.settings import (
    DispatchRuleCreate,
    DispatchRuleResponse,
    DispatchRuleUpdate,
    NotificationSettingCreate,
    NotificationSettingResponse,
    NotificationSettingUpdate,
    OperationsSettingsCreate,
    OperationsSettingsResponse,
    OperationsSettingsUpdate,
    SettingsGroup,
    SettingValue,
    SLAThresholdCreate,
    SLAThresholdResponse,
    SLAThresholdUpdate,
    ZoneDefaultCreate,
    ZoneDefaultResponse,
    ZoneDefaultUpdate,
)

router = APIRouter()


# Operations Settings Endpoints
@router.get("/", response_model=List[OperationsSettingsResponse])
def list_settings(
    setting_group: str = Query(None, description="Filter by group"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all operations settings

    Groups include:
    - dispatch: Dispatch and assignment settings
    - sla: SLA configuration
    - quality: Quality control settings
    - zone: Zone management settings
    - notification: Notification settings
    """
    if setting_group:
        settings = operations_settings.get_by_group(
            db, setting_group=setting_group, organization_id=current_org.id
        )
    else:
        settings = operations_settings.get_active_settings(db, organization_id=current_org.id)
    return settings


@router.get("/groups", response_model=List[str])
def list_setting_groups(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all setting groups"""
    return operations_settings.get_groups(db, organization_id=current_org.id)


@router.get("/grouped", response_model=List[SettingsGroup])
def get_settings_grouped(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get all settings organized by group"""
    groups = operations_settings.get_groups(db, organization_id=current_org.id)
    result = []
    for group in groups:
        settings = operations_settings.get_by_group(
            db, setting_group=group, organization_id=current_org.id
        )
        result.append(SettingsGroup(group_name=group, settings=settings))
    return result


@router.get("/key/{setting_key}", response_model=OperationsSettingsResponse)
def get_setting_by_key(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific setting by key"""
    setting = operations_settings.get_by_key(
        db, setting_key=setting_key, organization_id=current_org.id
    )
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return setting


@router.get("/key/{setting_key}/value")
def get_setting_value(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get the value of a specific setting"""
    setting = operations_settings.get_by_key(
        db, setting_key=setting_key, organization_id=current_org.id
    )
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return {"key": setting_key, "value": setting.value}


@router.get("/{setting_id}", response_model=OperationsSettingsResponse)
def get_setting(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific setting by ID"""
    setting = operations_settings.get(db, id=setting_id)
    if not setting or setting.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return setting


@router.post("/", response_model=OperationsSettingsResponse, status_code=status.HTTP_201_CREATED)
def create_setting(
    setting_in: OperationsSettingsCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new operations setting

    Business Logic:
    - Validates setting key is unique within organization
    - Sets value based on value_type
    - Validates against constraints if provided
    """
    existing = operations_settings.get_by_key(
        db, setting_key=setting_in.setting_key, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting with key '{setting_in.setting_key}' already exists",
        )

    setting = operations_settings.create(db, obj_in=setting_in, organization_id=current_org.id)
    return setting


@router.put("/{setting_id}", response_model=OperationsSettingsResponse)
def update_setting(
    setting_id: int,
    setting_in: OperationsSettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a setting"""
    setting = operations_settings.get(db, id=setting_id)
    if not setting or setting.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")

    if setting.is_readonly:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This setting is read-only and cannot be modified",
        )

    setting = operations_settings.update(db, db_obj=setting, obj_in=setting_in)
    return setting


@router.put("/key/{setting_key}/value", response_model=OperationsSettingsResponse)
def set_setting_value(
    setting_key: str,
    value_in: SettingValue,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Set the value of a specific setting by key

    Business Logic:
    - Validates against constraints
    - Records who modified and when
    - Triggers related actions if configured
    """
    modified_by_id = current_user.id if hasattr(current_user, "id") else None

    setting = operations_settings.set_value(
        db,
        setting_key=setting_key,
        value=value_in.value,
        modified_by_id=modified_by_id,
        organization_id=current_org.id,
    )

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found or is read-only"
        )

    return setting


@router.delete("/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a setting"""
    setting = operations_settings.get(db, id=setting_id)
    if not setting or setting.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")

    if setting.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="System settings cannot be deleted"
        )

    operations_settings.remove(db, id=setting_id)
    return None


# Dispatch Rules Endpoints
@router.get("/dispatch-rules", response_model=List[DispatchRuleResponse])
def list_dispatch_rules(
    zone_id: int = Query(None, description="Filter by zone"),
    active_only: bool = Query(True, description="Show only active rules"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all dispatch rules

    Business Logic:
    - Returns rules ordered by priority
    - Can filter by zone applicability
    - Active rules are used by dispatch system
    """
    if zone_id:
        rules = dispatch_rule.get_rules_for_zone(
            db, zone_id=zone_id, organization_id=current_org.id
        )
    elif active_only:
        rules = dispatch_rule.get_active_rules(db, organization_id=current_org.id)
    else:
        rules = dispatch_rule.get_multi(db, skip=0, limit=100, filters={"organization_id": current_org.id})
    return rules


@router.get("/dispatch-rules/{rule_id}", response_model=DispatchRuleResponse)
def get_dispatch_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific dispatch rule"""
    rule = dispatch_rule.get(db, id=rule_id)
    if not rule or rule.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch rule not found")
    return rule


@router.post(
    "/dispatch-rules", response_model=DispatchRuleResponse, status_code=status.HTTP_201_CREATED
)
def create_dispatch_rule(
    rule_in: DispatchRuleCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new dispatch rule

    Business Logic:
    - Validates rule code is unique within organization
    - Sets conditions and actions
    - Applies to specified zones or all zones
    - Time restrictions if configured
    """
    existing = dispatch_rule.get_by_code(
        db, rule_code=rule_in.rule_code, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule with code '{rule_in.rule_code}' already exists",
        )

    rule = dispatch_rule.create(db, obj_in=rule_in, organization_id=current_org.id)
    return rule


@router.put("/dispatch-rules/{rule_id}", response_model=DispatchRuleResponse)
def update_dispatch_rule(
    rule_id: int,
    rule_in: DispatchRuleUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a dispatch rule"""
    rule = dispatch_rule.get(db, id=rule_id)
    if not rule or rule.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch rule not found")
    rule = dispatch_rule.update(db, db_obj=rule, obj_in=rule_in)
    return rule


@router.delete("/dispatch-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dispatch_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a dispatch rule"""
    rule = dispatch_rule.get(db, id=rule_id)
    if not rule or rule.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispatch rule not found")
    dispatch_rule.remove(db, id=rule_id)
    return None


@router.post("/dispatch-rules/reorder")
def reorder_dispatch_rules(
    rule_orders: List[dict],
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Reorder dispatch rules by priority

    Expects list of: [{"rule_id": 1, "priority": 10}, ...]
    """
    # Verify all rules belong to organization
    for rule_order in rule_orders:
        rule = dispatch_rule.get(db, id=rule_order.get("rule_id"))
        if not rule or rule.organization_id != current_org.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dispatch rule {rule_order.get('rule_id')} not found",
            )

    dispatch_rule.reorder_priorities(db, rule_orders=rule_orders)
    return {"message": "Rules reordered successfully"}


# SLA Thresholds Endpoints
@router.get("/sla-thresholds", response_model=List[SLAThresholdResponse])
def list_sla_thresholds(
    sla_type: str = Query(None, description="Filter by SLA type"),
    service_type: str = Query(None, description="Filter by service type"),
    zone_id: int = Query(None, description="Filter by zone"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all SLA thresholds

    SLA Types:
    - delivery_time: Time to deliver
    - response_time: Response to customer
    - pickup_time: Time to pickup
    - resolution_time: Issue resolution time
    """
    if sla_type:
        thresholds = sla_threshold.get_by_sla_type(
            db, sla_type=sla_type, organization_id=current_org.id
        )
    elif service_type:
        thresholds = sla_threshold.get_by_service_type(
            db, service_type=service_type, organization_id=current_org.id
        )
    elif zone_id:
        thresholds = sla_threshold.get_for_zone(db, zone_id=zone_id, organization_id=current_org.id)
    else:
        thresholds = sla_threshold.get_active_thresholds(db, organization_id=current_org.id)
    return thresholds


@router.get("/sla-thresholds/{threshold_id}", response_model=SLAThresholdResponse)
def get_sla_threshold(
    threshold_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific SLA threshold"""
    threshold = sla_threshold.get(db, id=threshold_id)
    if not threshold or threshold.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA threshold not found")
    return threshold


@router.post(
    "/sla-thresholds", response_model=SLAThresholdResponse, status_code=status.HTTP_201_CREATED
)
def create_sla_threshold(
    threshold_in: SLAThresholdCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new SLA threshold

    Business Logic:
    - Validates threshold code is unique within organization
    - Warning must be less than target
    - Critical must be greater than target
    - Can apply to specific zone or all zones
    """
    existing = sla_threshold.get_by_code(
        db, threshold_code=threshold_in.threshold_code, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Threshold with code '{threshold_in.threshold_code}' already exists",
        )

    threshold = sla_threshold.create(db, obj_in=threshold_in, organization_id=current_org.id)
    return threshold


@router.put("/sla-thresholds/{threshold_id}", response_model=SLAThresholdResponse)
def update_sla_threshold(
    threshold_id: int,
    threshold_in: SLAThresholdUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update an SLA threshold"""
    threshold = sla_threshold.get(db, id=threshold_id)
    if not threshold or threshold.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA threshold not found")
    threshold = sla_threshold.update(db, db_obj=threshold, obj_in=threshold_in)
    return threshold


@router.delete("/sla-thresholds/{threshold_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sla_threshold(
    threshold_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete an SLA threshold"""
    threshold = sla_threshold.get(db, id=threshold_id)
    if not threshold or threshold.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SLA threshold not found")
    sla_threshold.remove(db, id=threshold_id)
    return None


# Notification Settings Endpoints
@router.get("/notifications", response_model=List[NotificationSettingResponse])
def list_notification_settings(
    event_type: str = Query(None, description="Filter by event type"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all notification settings

    Event Types:
    - sla_warning: SLA approaching deadline
    - sla_breach: SLA breached
    - dispatch_failed: Dispatch assignment failed
    - queue_escalation: Queue entry escalated
    - quality_failed: Quality inspection failed
    - feedback_negative: Negative customer feedback
    """
    if event_type:
        setting = notification_setting.get_by_event_type(
            db, event_type=event_type, organization_id=current_org.id
        )
        return [setting] if setting else []
    else:
        return notification_setting.get_active_settings(db, organization_id=current_org.id)


@router.get("/notifications/{setting_id}", response_model=NotificationSettingResponse)
def get_notification_setting(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific notification setting"""
    setting = notification_setting.get(db, id=setting_id)
    if not setting or setting.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification setting not found"
        )
    return setting


@router.post(
    "/notifications",
    response_model=NotificationSettingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_notification_setting(
    setting_in: NotificationSettingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new notification setting

    Business Logic:
    - Configures which channels to notify
    - Sets recipients by role or user IDs
    - Configures cooldown between notifications
    - Links to email/SMS templates
    """
    existing = notification_setting.get_by_code(
        db, setting_code=setting_in.setting_code, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Notification setting with code '{setting_in.setting_code}' already exists",
        )

    setting = notification_setting.create(db, obj_in=setting_in, organization_id=current_org.id)
    return setting


@router.put("/notifications/{setting_id}", response_model=NotificationSettingResponse)
def update_notification_setting(
    setting_id: int,
    setting_in: NotificationSettingUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a notification setting"""
    setting = notification_setting.get(db, id=setting_id)
    if not setting or setting.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification setting not found"
        )
    setting = notification_setting.update(db, db_obj=setting, obj_in=setting_in)
    return setting


@router.delete("/notifications/{setting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification_setting(
    setting_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a notification setting"""
    setting = notification_setting.get(db, id=setting_id)
    if not setting or setting.organization_id != current_org.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Notification setting not found"
        )
    notification_setting.remove(db, id=setting_id)
    return None


# Zone Defaults Endpoints
@router.get("/zone-defaults", response_model=List[ZoneDefaultResponse])
def list_zone_defaults(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """List all zone default configurations"""
    return zone_default.get_active_defaults(db, organization_id=current_org.id)


@router.get("/zone-defaults/default", response_model=ZoneDefaultResponse)
def get_default_zone_template(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get the default zone configuration template"""
    default = zone_default.get_default_template(db, organization_id=current_org.id)
    if not default:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No default zone template configured"
        )
    return default


@router.get("/zone-defaults/{default_id}", response_model=ZoneDefaultResponse)
def get_zone_default(
    default_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Get a specific zone default configuration"""
    default = zone_default.get(db, id=default_id)
    if not default or default.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone default not found")
    return default


@router.post(
    "/zone-defaults", response_model=ZoneDefaultResponse, status_code=status.HTTP_201_CREATED
)
def create_zone_default(
    default_in: ZoneDefaultCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Create a new zone default configuration

    Business Logic:
    - Used when creating new zones
    - Provides default values for capacity, pricing, SLA
    - Can set as main default template
    """
    existing = zone_default.get_by_code(
        db, default_code=default_in.default_code, organization_id=current_org.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Zone default with code '{default_in.default_code}' already exists",
        )

    default = zone_default.create(db, obj_in=default_in, organization_id=current_org.id)
    return default


@router.put("/zone-defaults/{default_id}", response_model=ZoneDefaultResponse)
def update_zone_default(
    default_id: int,
    default_in: ZoneDefaultUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Update a zone default configuration"""
    default = zone_default.get(db, id=default_id)
    if not default or default.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone default not found")
    default = zone_default.update(db, db_obj=default, obj_in=default_in)
    return default


@router.post("/zone-defaults/{default_id}/set-default", response_model=ZoneDefaultResponse)
def set_as_default_template(
    default_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Set a zone default as the main default template"""
    existing = zone_default.get(db, id=default_id)
    if not existing or existing.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone default not found")

    default = zone_default.set_as_default(db, default_id=default_id)
    if not default:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone default not found")
    return default


@router.delete("/zone-defaults/{default_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_zone_default(
    default_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    current_org: Organization = Depends(get_current_organization),
):
    """Delete a zone default configuration"""
    default = zone_default.get(db, id=default_id)
    if not default or default.organization_id != current_org.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Zone default not found")
    zone_default.remove(db, id=default_id)
    return None
