"""
Operations Settings CRUD Operations
"""

from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.operations.settings import (
    DispatchRule,
    NotificationSetting,
    OperationsSettings,
    SLAThreshold,
    ZoneDefault,
)
from app.schemas.operations.settings import (
    DispatchRuleCreate,
    DispatchRuleUpdate,
    NotificationSettingCreate,
    NotificationSettingUpdate,
    OperationsSettingsCreate,
    OperationsSettingsUpdate,
    SLAThresholdCreate,
    SLAThresholdUpdate,
    ZoneDefaultCreate,
    ZoneDefaultUpdate,
)


class CRUDOperationsSettings(
    CRUDBase[OperationsSettings, OperationsSettingsCreate, OperationsSettingsUpdate]
):
    def get_by_key(
        self, db: Session, *, setting_key: str, organization_id: int = None
    ) -> Optional[OperationsSettings]:
        """Get setting by key"""
        query = db.query(OperationsSettings).filter(
            OperationsSettings.setting_key == setting_key
        )
        if organization_id:
            query = query.filter(OperationsSettings.organization_id == organization_id)
        return query.first()

    def get_by_group(
        self, db: Session, *, setting_group: str, organization_id: int = None
    ) -> List[OperationsSettings]:
        """Get all settings in a group"""
        query = db.query(OperationsSettings).filter(
            OperationsSettings.setting_group == setting_group,
            OperationsSettings.is_active == True,
        )
        if organization_id:
            query = query.filter(OperationsSettings.organization_id == organization_id)
        return query.order_by(OperationsSettings.setting_key).all()

    def get_active_settings(
        self, db: Session, organization_id: int = None
    ) -> List[OperationsSettings]:
        """Get all active settings"""
        query = db.query(OperationsSettings).filter(OperationsSettings.is_active == True)
        if organization_id:
            query = query.filter(OperationsSettings.organization_id == organization_id)
        return query.order_by(
            OperationsSettings.setting_group, OperationsSettings.setting_key
        ).all()

    def get_groups(self, db: Session, organization_id: int = None) -> List[str]:
        """Get all setting groups"""
        query = db.query(OperationsSettings.setting_group).distinct()
        if organization_id:
            query = query.filter(OperationsSettings.organization_id == organization_id)
        groups = query.all()
        return [g[0] for g in groups]

    def set_value(
        self,
        db: Session,
        *,
        setting_key: str,
        value: Any,
        modified_by_id: int = None,
        organization_id: int = None,
    ) -> Optional[OperationsSettings]:
        """Set setting value"""
        setting = self.get_by_key(db, setting_key=setting_key, organization_id=organization_id)
        if not setting:
            return None

        if setting.is_readonly:
            return None

        # Set value based on type
        if setting.value_type == "string":
            setting.string_value = str(value)
        elif setting.value_type == "number":
            setting.number_value = float(value)
        elif setting.value_type == "boolean":
            setting.boolean_value = bool(value)
        elif setting.value_type == "json":
            setting.json_value = value

        setting.last_modified_by_id = modified_by_id
        setting.last_modified_at = datetime.utcnow()

        db.add(setting)
        db.commit()
        db.refresh(setting)
        return setting

    def get_value(
        self, db: Session, *, setting_key: str, default: Any = None, organization_id: int = None
    ) -> Any:
        """Get setting value"""
        setting = self.get_by_key(db, setting_key=setting_key, organization_id=organization_id)
        if not setting or not setting.is_active:
            return default
        return setting.value

    def create(
        self, db: Session, *, obj_in: OperationsSettingsCreate, organization_id: int = None
    ) -> OperationsSettings:
        """Create with organization_id"""
        from fastapi.encoders import jsonable_encoder

        obj_in_data = jsonable_encoder(obj_in)
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = OperationsSettings(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDDispatchRule(CRUDBase[DispatchRule, DispatchRuleCreate, DispatchRuleUpdate]):
    def get_by_code(
        self, db: Session, *, rule_code: str, organization_id: int = None
    ) -> Optional[DispatchRule]:
        """Get rule by code"""
        query = db.query(DispatchRule).filter(DispatchRule.rule_code == rule_code)
        if organization_id:
            query = query.filter(DispatchRule.organization_id == organization_id)
        return query.first()

    def get_active_rules(self, db: Session, organization_id: int = None) -> List[DispatchRule]:
        """Get all active rules ordered by priority"""
        query = db.query(DispatchRule).filter(DispatchRule.is_active == True)
        if organization_id:
            query = query.filter(DispatchRule.organization_id == organization_id)
        return query.order_by(DispatchRule.priority.asc()).all()

    def get_rules_for_zone(
        self, db: Session, *, zone_id: int, organization_id: int = None
    ) -> List[DispatchRule]:
        """Get rules applicable to a zone"""
        query = db.query(DispatchRule).filter(
            DispatchRule.is_active == True,
            (DispatchRule.applies_to_all_zones == True)
            | (DispatchRule.zone_ids.contains(str(zone_id))),
        )
        if organization_id:
            query = query.filter(DispatchRule.organization_id == organization_id)
        return query.order_by(DispatchRule.priority.asc()).all()

    def create(
        self, db: Session, *, obj_in: DispatchRuleCreate, organization_id: int = None
    ) -> DispatchRule:
        """Create with organization_id"""
        from fastapi.encoders import jsonable_encoder

        obj_in_data = jsonable_encoder(obj_in)
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = DispatchRule(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def increment_triggered(
        self, db: Session, *, rule_id: int, success: bool
    ) -> Optional[DispatchRule]:
        """Increment rule trigger count"""
        rule = self.get(db, id=rule_id)
        if rule:
            rule.times_triggered += 1
            if success:
                rule.successful_assignments += 1
            else:
                rule.failed_assignments += 1
            db.add(rule)
            db.commit()
            db.refresh(rule)
        return rule

    def reorder_priorities(self, db: Session, *, rule_orders: List[dict]) -> bool:
        """Reorder rule priorities"""
        for order in rule_orders:
            rule = self.get(db, id=order["rule_id"])
            if rule:
                rule.priority = order["priority"]
                db.add(rule)
        db.commit()
        return True


class CRUDSLAThreshold(CRUDBase[SLAThreshold, SLAThresholdCreate, SLAThresholdUpdate]):
    def get_by_code(
        self, db: Session, *, threshold_code: str, organization_id: int = None
    ) -> Optional[SLAThreshold]:
        """Get threshold by code"""
        query = db.query(SLAThreshold).filter(SLAThreshold.threshold_code == threshold_code)
        if organization_id:
            query = query.filter(SLAThreshold.organization_id == organization_id)
        return query.first()

    def get_active_thresholds(self, db: Session, organization_id: int = None) -> List[SLAThreshold]:
        """Get all active thresholds"""
        query = db.query(SLAThreshold).filter(SLAThreshold.is_active == True)
        if organization_id:
            query = query.filter(SLAThreshold.organization_id == organization_id)
        return query.all()

    def get_by_sla_type(
        self, db: Session, *, sla_type: str, organization_id: int = None
    ) -> List[SLAThreshold]:
        """Get thresholds by SLA type"""
        query = db.query(SLAThreshold).filter(
            SLAThreshold.sla_type == sla_type, SLAThreshold.is_active == True
        )
        if organization_id:
            query = query.filter(SLAThreshold.organization_id == organization_id)
        return query.all()

    def get_by_service_type(
        self, db: Session, *, service_type: str, organization_id: int = None
    ) -> List[SLAThreshold]:
        """Get thresholds by service type"""
        query = db.query(SLAThreshold).filter(
            SLAThreshold.service_type == service_type, SLAThreshold.is_active == True
        )
        if organization_id:
            query = query.filter(SLAThreshold.organization_id == organization_id)
        return query.all()

    def get_for_zone(
        self, db: Session, *, zone_id: int, sla_type: str = None, organization_id: int = None
    ) -> List[SLAThreshold]:
        """Get thresholds for a specific zone"""
        query = db.query(SLAThreshold).filter(
            SLAThreshold.is_active == True,
            (SLAThreshold.applies_to_all_zones == True) | (SLAThreshold.zone_id == zone_id),
        )
        if organization_id:
            query = query.filter(SLAThreshold.organization_id == organization_id)
        if sla_type:
            query = query.filter(SLAThreshold.sla_type == sla_type)
        return query.all()

    def get_threshold_for_delivery(
        self, db: Session, *, service_type: str, zone_id: int = None, organization_id: int = None
    ) -> Optional[SLAThreshold]:
        """Get applicable threshold for a delivery"""
        query = db.query(SLAThreshold).filter(
            SLAThreshold.is_active == True, SLAThreshold.sla_type == "delivery_time"
        )
        if organization_id:
            query = query.filter(SLAThreshold.organization_id == organization_id)

        # Try zone-specific first
        if zone_id:
            zone_threshold = query.filter(SLAThreshold.zone_id == zone_id).first()
            if zone_threshold:
                return zone_threshold

        # Fall back to service type
        if service_type:
            service_threshold = query.filter(
                SLAThreshold.service_type == service_type, SLAThreshold.applies_to_all_zones == True
            ).first()
            if service_threshold:
                return service_threshold

        # Fall back to global default
        return query.filter(SLAThreshold.applies_to_all_zones == True).first()

    def create(
        self, db: Session, *, obj_in: SLAThresholdCreate, organization_id: int = None
    ) -> SLAThreshold:
        """Create with organization_id"""
        from fastapi.encoders import jsonable_encoder

        obj_in_data = jsonable_encoder(obj_in)
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = SLAThreshold(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDNotificationSetting(
    CRUDBase[NotificationSetting, NotificationSettingCreate, NotificationSettingUpdate]
):
    def get_by_code(
        self, db: Session, *, setting_code: str, organization_id: int = None
    ) -> Optional[NotificationSetting]:
        """Get notification setting by code"""
        query = db.query(NotificationSetting).filter(
            NotificationSetting.setting_code == setting_code
        )
        if organization_id:
            query = query.filter(NotificationSetting.organization_id == organization_id)
        return query.first()

    def get_active_settings(
        self, db: Session, organization_id: int = None
    ) -> List[NotificationSetting]:
        """Get all active notification settings"""
        query = db.query(NotificationSetting).filter(NotificationSetting.is_active == True)
        if organization_id:
            query = query.filter(NotificationSetting.organization_id == organization_id)
        return query.all()

    def get_by_event_type(
        self, db: Session, *, event_type: str, organization_id: int = None
    ) -> Optional[NotificationSetting]:
        """Get notification setting by event type"""
        query = db.query(NotificationSetting).filter(
            NotificationSetting.event_type == event_type, NotificationSetting.is_active == True
        )
        if organization_id:
            query = query.filter(NotificationSetting.organization_id == organization_id)
        return query.first()

    def get_events_for_role(
        self, db: Session, *, role: str, organization_id: int = None
    ) -> List[NotificationSetting]:
        """Get notification settings that notify a specific role"""
        query = db.query(NotificationSetting).filter(
            NotificationSetting.notify_roles.contains(role),
            NotificationSetting.is_active == True,
        )
        if organization_id:
            query = query.filter(NotificationSetting.organization_id == organization_id)
        return query.all()

    def create(
        self, db: Session, *, obj_in: NotificationSettingCreate, organization_id: int = None
    ) -> NotificationSetting:
        """Create with organization_id"""
        from fastapi.encoders import jsonable_encoder

        obj_in_data = jsonable_encoder(obj_in)
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = NotificationSetting(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDZoneDefault(CRUDBase[ZoneDefault, ZoneDefaultCreate, ZoneDefaultUpdate]):
    def get_by_code(
        self, db: Session, *, default_code: str, organization_id: int = None
    ) -> Optional[ZoneDefault]:
        """Get zone default by code"""
        query = db.query(ZoneDefault).filter(ZoneDefault.default_code == default_code)
        if organization_id:
            query = query.filter(ZoneDefault.organization_id == organization_id)
        return query.first()

    def get_active_defaults(self, db: Session, organization_id: int = None) -> List[ZoneDefault]:
        """Get all active zone defaults"""
        query = db.query(ZoneDefault).filter(ZoneDefault.is_active == True)
        if organization_id:
            query = query.filter(ZoneDefault.organization_id == organization_id)
        return query.all()

    def get_default_template(self, db: Session, organization_id: int = None) -> Optional[ZoneDefault]:
        """Get the default template"""
        query = db.query(ZoneDefault).filter(
            ZoneDefault.is_default == True, ZoneDefault.is_active == True
        )
        if organization_id:
            query = query.filter(ZoneDefault.organization_id == organization_id)
        return query.first()

    def set_as_default(self, db: Session, *, default_id: int) -> Optional[ZoneDefault]:
        """Set a zone default as the main default"""
        # Clear current default
        db.query(ZoneDefault).filter(ZoneDefault.is_default == True).update({"is_default": False})

        # Set new default
        zone_default = self.get(db, id=default_id)
        if zone_default:
            zone_default.is_default = True
            db.add(zone_default)
            db.commit()
            db.refresh(zone_default)
        return zone_default

    def create(
        self, db: Session, *, obj_in: ZoneDefaultCreate, organization_id: int = None
    ) -> ZoneDefault:
        """Create with organization_id"""
        from fastapi.encoders import jsonable_encoder

        obj_in_data = jsonable_encoder(obj_in)
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = ZoneDefault(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


operations_settings = CRUDOperationsSettings(OperationsSettings)
dispatch_rule = CRUDDispatchRule(DispatchRule)
sla_threshold = CRUDSLAThreshold(SLAThreshold)
notification_setting = CRUDNotificationSetting(NotificationSetting)
zone_default = CRUDZoneDefault(ZoneDefault)
