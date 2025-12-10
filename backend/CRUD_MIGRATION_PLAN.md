# CRUD to Services Layer Migration Plan

## Executive Summary

The codebase has redundant layers:
- `backend/app/crud/` - 52 files with basic CRUD operations
- `backend/app/services/` - 78+ files with business logic

This plan consolidates the CRUD layer into the Services layer to reduce redundancy while preserving all functionality.

---

## Architecture Analysis

### Current State

**CRUD Layer** (`app/crud/`):
- Uses `CRUDBase` from `app/crud/base.py` - provides generic `get`, `get_multi`, `create`, `update`, `remove`
- Most files are simple instances: `CRUDBase[Model, Create, Update](Model)`
- Some files have custom methods extending `CRUDBase`
- Includes `TenantAwareCRUD` in `tenant_crud.py` for multi-tenant operations

**Services Layer** (`app/services/`):
- Uses `CRUDBase` from `app/services/base.py` - similar but enhanced with `count`, `search`, `bulk_*` methods
- Services extend this base and add domain-specific business logic
- Services import CRUD in only 2 places (workflow approval & execution)

### Key Finding

The `app/services/base.py` already provides the same (and more) functionality as `app/crud/base.py`:
- Both have: `get`, `get_multi`, `create`, `update`
- Services base adds: `count`, `search`, `bulk_create`, `bulk_update`, `bulk_delete`, `delete` (vs `remove`)

**This means most CRUD files are redundant** - their functionality is already available through services.

---

## Files Classification

### Category 1: Files Safe to Delete (No External Imports)

These CRUD files are NOT imported anywhere outside the `crud/` directory:

```
backend/app/crud/fleet/accident_log.py
backend/app/crud/fleet/assignment.py
backend/app/crud/fleet/inspection.py
backend/app/crud/fleet/maintenance.py
backend/app/crud/fleet/vehicle_log.py
backend/app/crud/hr/asset.py
backend/app/crud/hr/attendance.py
backend/app/crud/hr/leave.py
backend/app/crud/hr/loan.py
backend/app/crud/hr/salary.py
backend/app/crud/operations/cod.py
backend/app/crud/operations/delivery.py
backend/app/crud/accommodation/allocation.py
backend/app/crud/accommodation/bed.py
backend/app/crud/accommodation/building.py
backend/app/crud/accommodation/room.py
backend/app/crud/workflow/analytics.py
backend/app/crud/workflow/attachment.py
backend/app/crud/workflow/automation.py
backend/app/crud/workflow/comment.py
backend/app/crud/workflow/history.py
backend/app/crud/workflow/notification.py
backend/app/crud/workflow/sla.py
backend/app/crud/workflow/trigger.py
```

**Reason**: Corresponding services exist and are already used by API routes.

---

### Category 2: Files Requiring Migration (Imported by APIs/Services)

#### 2.1 Fleet Domain

| CRUD File | Imported By | Migration Target |
|-----------|-------------|------------------|
| `crud/fleet/courier.py` | `api/v1/operations/handovers.py` | Create `services/fleet/courier.py` methods (already exists!) |
| `crud/fleet/vehicle.py` | `api/v1/operations/handovers.py` | Use `services/fleet/vehicle.py` (already exists!) |
| `crud/fleet/document.py` | `api/v1/fleet/documents.py` | Create `services/fleet/document_service.py` |
| `crud/fleet/fuel_log.py` | `api/v1/fleet/fuel_logs.py` | Create `services/fleet/fuel_log_service.py` |

#### 2.2 HR Domain

| CRUD File | Imported By | Migration Target |
|-----------|-------------|------------------|
| `crud/hr/bonus.py` | `api/v1/hr/bonuses.py` | Create `services/hr/bonus_service.py` |

#### 2.3 Operations Domain

| CRUD File | Imported By | Migration Target |
|-----------|-------------|------------------|
| `crud/operations/route.py` | `api/v1/operations/routes.py` | Use existing `services/operations/route_service.py` |
| `crud/operations/handover.py` | `api/v1/operations/handovers.py` | Create `services/operations/handover_service.py` |
| `crud/operations/incident.py` | `api/v1/operations/incidents.py` | Use existing `services/operations/incident_service.py` |
| `crud/operations/dispatch.py` | `api/v1/operations/dispatch.py` | Create `services/operations/dispatch_service.py` |
| `crud/operations/zone.py` | `api/v1/operations/zones.py` | Create `services/operations/zone_service.py` |
| `crud/operations/sla.py` | `api/v1/operations/sla.py` | Create `services/operations/sla_service.py` |
| `crud/operations/priority_queue.py` | `api/v1/operations/priority_queue.py` | Create `services/operations/priority_queue_service.py` |
| `crud/operations/quality.py` | `api/v1/operations/quality.py` | Create `services/operations/quality_service.py` |
| `crud/operations/feedback.py` | `api/v1/operations/feedback.py` | Create `services/operations/feedback_service.py` |
| `crud/operations/document.py` | `api/v1/operations/document.py` | Create `services/operations/document_service.py` |
| `crud/operations/settings.py` | `api/v1/operations/settings.py` | Create `services/operations/settings_service.py` (COMPLEX) |

#### 2.4 Workflow Domain

| CRUD File | Imported By | Migration Target |
|-----------|-------------|------------------|
| `crud/workflow/instance.py` | `services/workflow/approval_service.py`, `services/workflow/execution_service.py` | Use `services/workflow/instance_service.py` |
| `crud/workflow/template.py` | `services/workflow/execution_service.py` | Use `services/workflow/template_service.py` |
| `crud/workflow/approval.py` | `services/workflow/approval_service.py` | Merge into `services/workflow/approval_service.py` |

#### 2.5 Core/Auth

| CRUD File | Imported By | Migration Target |
|-----------|-------------|------------------|
| `crud/user.py` | `core/dependencies.py`, `api/v1/auth.py` | Create `services/user_service.py` |

---

### Category 3: Files to KEEP

These files should be preserved:

```
backend/app/crud/base.py          # Keep - may be used by TenantAwareCRUD
backend/app/crud/tenant_crud.py   # Keep - TenantAwareCRUD base class
backend/app/crud/__init__.py      # Update - remove deleted imports
```

**Rationale**:
- `TenantAwareCRUD` provides multi-tenant specific functionality not in services base
- Some parts of the codebase may rely on these base classes

---

## Detailed Migration Steps

### Phase 1: Create Missing Services (No Breaking Changes)

#### 1.1 Create `services/fleet/document_service.py`

```python
"""Document Service for fleet documents"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.fleet.document import Document
from app.schemas.fleet.document import DocumentCreate, DocumentUpdate
from app.services.base import CRUDBase


class DocumentService(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    """Service for document operations"""

    def get_by_entity(
        self, db: Session, *, entity_type: str, entity_id: int,
        skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """Get documents for a specific entity"""
        query = db.query(Document).filter(
            Document.entity_type == entity_type,
            Document.entity_id == entity_id
        )
        return query.offset(skip).limit(limit).all()


document_service = DocumentService(Document)
```

#### 1.2 Create `services/fleet/fuel_log_service.py`

```python
"""Fuel Log Service"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.models.fleet.fuel_log import FuelLog
from app.schemas.fleet.fuel_log import FuelLogCreate, FuelLogUpdate
from app.services.base import CRUDBase


class FuelLogService(CRUDBase[FuelLog, FuelLogCreate, FuelLogUpdate]):
    """Service for fuel log operations"""

    def get_by_vehicle(
        self, db: Session, *, vehicle_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0, limit: int = 100
    ) -> List[FuelLog]:
        """Get fuel logs for a vehicle"""
        query = db.query(FuelLog).filter(FuelLog.vehicle_id == vehicle_id)
        if start_date:
            query = query.filter(FuelLog.date >= start_date)
        if end_date:
            query = query.filter(FuelLog.date <= end_date)
        return query.order_by(FuelLog.date.desc()).offset(skip).limit(limit).all()


fuel_log_service = FuelLogService(FuelLog)
```

#### 1.3 Create `services/hr/bonus_service.py`

```python
"""Bonus Service"""
from app.models.hr.bonus import Bonus
from app.schemas.hr.bonus import BonusCreate, BonusUpdate
from app.services.base import CRUDBase


class BonusService(CRUDBase[Bonus, BonusCreate, BonusUpdate]):
    """Service for bonus operations"""
    pass


bonus_service = BonusService(Bonus)
```

#### 1.4 Create `services/operations/handover_service.py`

**IMPORTANT**: This file has custom logic - must be migrated carefully.

```python
"""Handover Service"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.operations.handover import Handover, HandoverStatus
from app.schemas.operations.handover import HandoverCreate, HandoverUpdate
from app.services.base import CRUDBase


class HandoverService(CRUDBase[Handover, HandoverCreate, HandoverUpdate]):
    """Service for handover operations with business logic"""

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100,
        organization_id: int = None
    ) -> List[Handover]:
        """Get multiple handovers with optional organization filter"""
        query = db.query(Handover)
        if organization_id:
            query = query.filter(Handover.organization_id == organization_id)
        return query.order_by(Handover.created_at.desc()).offset(skip).limit(limit).all()

    def create_with_number(
        self, db: Session, *, obj_in: HandoverCreate, organization_id: int = None
    ) -> Handover:
        """Create handover with auto-generated number"""
        last_handover = db.query(Handover).order_by(Handover.id.desc()).first()
        next_number = 1 if not last_handover else last_handover.id + 1
        handover_number = f"HO-{datetime.now().strftime('%Y%m%d')}-{next_number:04d}"

        obj_in_data = obj_in.model_dump()
        if organization_id:
            obj_in_data["organization_id"] = organization_id
        db_obj = Handover(**obj_in_data, handover_number=handover_number)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_number(
        self, db: Session, *, handover_number: str, organization_id: int = None
    ) -> Optional[Handover]:
        """Get handover by unique number"""
        query = db.query(Handover).filter(Handover.handover_number == handover_number)
        if organization_id:
            query = query.filter(Handover.organization_id == organization_id)
        return query.first()

    def get_by_courier(
        self, db: Session, *, courier_id: int, skip: int = 0,
        limit: int = 100, organization_id: int = None
    ) -> List[Handover]:
        """Get handovers involving a specific courier"""
        query = db.query(Handover).filter(
            or_(Handover.from_courier_id == courier_id, Handover.to_courier_id == courier_id)
        )
        if organization_id:
            query = query.filter(Handover.organization_id == organization_id)
        return query.order_by(Handover.created_at.desc()).offset(skip).limit(limit).all()

    def get_by_vehicle(
        self, db: Session, *, vehicle_id: int, skip: int = 0,
        limit: int = 100, organization_id: int = None
    ) -> List[Handover]:
        """Get handovers for a specific vehicle"""
        query = db.query(Handover).filter(Handover.vehicle_id == vehicle_id)
        if organization_id:
            query = query.filter(Handover.organization_id == organization_id)
        return query.order_by(Handover.created_at.desc()).offset(skip).limit(limit).all()

    def get_pending(
        self, db: Session, *, skip: int = 0, limit: int = 100,
        organization_id: int = None
    ) -> List[Handover]:
        """Get all pending handovers"""
        query = db.query(Handover).filter(Handover.status == HandoverStatus.PENDING)
        if organization_id:
            query = query.filter(Handover.organization_id == organization_id)
        return query.order_by(Handover.scheduled_at.asc()).offset(skip).limit(limit).all()

    def approve(self, db: Session, *, handover_id: int, approved_by_id: int) -> Optional[Handover]:
        """Approve a handover"""
        handover = self.get(db, id=handover_id)
        if handover and handover.status == HandoverStatus.PENDING:
            handover.status = HandoverStatus.APPROVED
            handover.approved_by_id = approved_by_id
            handover.approved_at = datetime.utcnow()
            db.add(handover)
            db.commit()
            db.refresh(handover)
        return handover

    def reject(self, db: Session, *, handover_id: int, rejection_reason: str) -> Optional[Handover]:
        """Reject a handover"""
        handover = self.get(db, id=handover_id)
        if handover and handover.status == HandoverStatus.PENDING:
            handover.status = HandoverStatus.REJECTED
            handover.rejection_reason = rejection_reason
            db.add(handover)
            db.commit()
            db.refresh(handover)
        return handover

    def complete(self, db: Session, *, handover_id: int) -> Optional[Handover]:
        """Mark handover as completed"""
        handover = self.get(db, id=handover_id)
        if handover and handover.status == HandoverStatus.APPROVED:
            handover.status = HandoverStatus.COMPLETED
            handover.completed_at = datetime.utcnow()
            db.add(handover)
            db.commit()
            db.refresh(handover)
        return handover


handover_service = HandoverService(Handover)
```

#### 1.5 Create `services/user_service.py`

```python
"""User Service"""
from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.base import CRUDBase


class UserService(CRUDBase[User, UserCreate, UserUpdate]):
    """Service for user operations"""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password) if obj_in.password else None,
            full_name=obj_in.full_name,
            role=obj_in.role,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return bool(user.is_active)

    def is_superuser(self, user: User) -> bool:
        return bool(user.is_superuser)

    def get_by_google_id(self, db: Session, *, google_id: str) -> Optional[User]:
        return db.query(User).filter(User.google_id == google_id).first()

    def create_google_user(
        self, db: Session, *, email: str, google_id: str, full_name: str, picture: str
    ) -> User:
        db_obj = User(
            email=email,
            google_id=google_id,
            full_name=full_name,
            picture=picture,
            is_active=True,
            is_superuser=False,
            role="user",
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user_service = UserService(User)
```

### Phase 2: Update Import Statements

#### 2.1 `api/v1/fleet/documents.py`

**Before:**
```python
from app.crud.fleet.document import document as crud_document
```

**After:**
```python
from app.services.fleet import document_service
```

And update all usages:
- `crud_document.get(db, id=...)` -> `document_service.get(db, id=...)`
- `crud_document.get_multi(...)` -> `document_service.get_multi(...)`
- `crud_document.create(...)` -> `document_service.create(...)`
- `crud_document.update(...)` -> `document_service.update(...)`
- `crud_document.remove(...)` -> `document_service.delete(...)`

#### 2.2 `api/v1/fleet/fuel_logs.py`

**Before:**
```python
from app.crud.fleet.fuel_log import fuel_log as crud_fuel_log
```

**After:**
```python
from app.services.fleet import fuel_log_service
```

#### 2.3 `api/v1/operations/routes.py`

**Before:**
```python
from app.crud.operations import route as crud_route
```

**After:**
```python
from app.services.operations import route_service
```

#### 2.4 `api/v1/operations/handovers.py`

**Before:**
```python
from app.crud.fleet import courier as crud_courier
from app.crud.fleet import vehicle as crud_vehicle
from app.crud.operations import handover as crud_handover
```

**After:**
```python
from app.services.fleet import courier_service, vehicle_service
from app.services.operations import handover_service
```

#### 2.5 `api/v1/hr/bonuses.py`

**Before:**
```python
from app.crud.hr.bonus import bonus as crud_bonus
```

**After:**
```python
from app.services.hr import bonus_service
```

#### 2.6 `core/dependencies.py`

**Before:**
```python
from app.crud.user import crud_user
```

**After:**
```python
from app.services.user_service import user_service
```

#### 2.7 `api/v1/auth.py`

**Before:**
```python
from app.crud.user import crud_user
```

**After:**
```python
from app.services.user_service import user_service
```

#### 2.8 `services/workflow/approval_service.py`

**Before:**
```python
from app.crud.workflow import approval_chain, approval_request, workflow_instance
```

**After:**
```python
from app.services.workflow import instance_service
# For approval_chain and approval_request, either:
# Option A: Create approval_chain_service and approval_request_service
# Option B: Inline the CRUD logic (since it's simple get/update calls)
```

#### 2.9 `services/workflow/execution_service.py`

**Before:**
```python
from app.crud.workflow import workflow_instance, workflow_template
```

**After:**
```python
from app.services.workflow import instance_service, template_service
```

---

### Phase 3: Complex Migrations

#### 3.1 Operations Settings (COMPLEX)

The `crud/operations/settings.py` file has 5 classes with significant custom logic:
- `CRUDOperationsSettings`
- `CRUDDispatchRule`
- `CRUDSLAThreshold`
- `CRUDNotificationSetting`
- `CRUDZoneDefault`

**Recommendation**: Create `services/operations/settings_service.py` that contains all 5 services, directly porting the logic from the CRUD file.

---

### Phase 4: Delete CRUD Files

After all migrations are complete and tested:

```bash
# Remove simple CRUD files (no custom logic)
rm backend/app/crud/fleet/accident_log.py
rm backend/app/crud/fleet/assignment.py
rm backend/app/crud/fleet/courier.py
rm backend/app/crud/fleet/document.py
rm backend/app/crud/fleet/fuel_log.py
rm backend/app/crud/fleet/inspection.py
rm backend/app/crud/fleet/maintenance.py
rm backend/app/crud/fleet/vehicle.py
rm backend/app/crud/fleet/vehicle_log.py

rm backend/app/crud/hr/asset.py
rm backend/app/crud/hr/attendance.py
rm backend/app/crud/hr/bonus.py
rm backend/app/crud/hr/leave.py
rm backend/app/crud/hr/loan.py
rm backend/app/crud/hr/salary.py

rm backend/app/crud/operations/cod.py
rm backend/app/crud/operations/delivery.py
rm backend/app/crud/operations/dispatch.py
rm backend/app/crud/operations/document.py
rm backend/app/crud/operations/feedback.py
rm backend/app/crud/operations/handover.py
rm backend/app/crud/operations/incident.py
rm backend/app/crud/operations/priority_queue.py
rm backend/app/crud/operations/quality.py
rm backend/app/crud/operations/route.py
rm backend/app/crud/operations/settings.py
rm backend/app/crud/operations/sla.py
rm backend/app/crud/operations/zone.py

rm backend/app/crud/accommodation/allocation.py
rm backend/app/crud/accommodation/bed.py
rm backend/app/crud/accommodation/building.py
rm backend/app/crud/accommodation/room.py

rm backend/app/crud/workflow/analytics.py
rm backend/app/crud/workflow/approval.py
rm backend/app/crud/workflow/attachment.py
rm backend/app/crud/workflow/automation.py
rm backend/app/crud/workflow/comment.py
rm backend/app/crud/workflow/history.py
rm backend/app/crud/workflow/instance.py
rm backend/app/crud/workflow/notification.py
rm backend/app/crud/workflow/sla.py
rm backend/app/crud/workflow/template.py
rm backend/app/crud/workflow/trigger.py

rm backend/app/crud/user.py

# Remove domain __init__.py files
rm backend/app/crud/fleet/__init__.py
rm backend/app/crud/hr/__init__.py
rm backend/app/crud/operations/__init__.py
rm backend/app/crud/accommodation/__init__.py
rm backend/app/crud/workflow/__init__.py
```

---

### Phase 5: Update Package Files

#### Update `backend/app/crud/__init__.py`

```python
"""
CRUD Package - Minimal base classes only

Note: Domain-specific CRUD operations have been merged into the services layer.
Use app.services for all data operations.
"""

from app.crud.base import CRUDBase
from app.crud.tenant_crud import TenantAwareCRUD, TenantCRUD

__all__ = [
    "CRUDBase",
    "TenantAwareCRUD",
    "TenantCRUD",
]
```

#### Update `backend/app/services/fleet/__init__.py`

```python
"""Fleet Management services"""

from app.services.fleet.accident_log import AccidentLogService, accident_log_service
from app.services.fleet.assignment import AssignmentService, assignment_service
from app.services.fleet.courier import CourierService, courier_service
from app.services.fleet.document_service import DocumentService, document_service  # NEW
from app.services.fleet.fuel_log_service import FuelLogService, fuel_log_service  # NEW
from app.services.fleet.inspection import InspectionService, inspection_service
from app.services.fleet.maintenance import MaintenanceService, maintenance_service
from app.services.fleet.vehicle import VehicleService, vehicle_service
from app.services.fleet.vehicle_log import VehicleLogService, vehicle_log_service

__all__ = [
    "courier_service",
    "vehicle_service",
    "assignment_service",
    "vehicle_log_service",
    "maintenance_service",
    "inspection_service",
    "accident_log_service",
    "document_service",      # NEW
    "fuel_log_service",      # NEW
    # ... service classes
]
```

---

## Migration Checklist

### Pre-Migration

- [ ] Run all tests to establish baseline
- [ ] Create backup branch: `git checkout -b backup/pre-crud-migration`

### Phase 1: Create Services

- [ ] Create `services/fleet/document_service.py`
- [ ] Create `services/fleet/fuel_log_service.py`
- [ ] Create `services/hr/bonus_service.py`
- [ ] Create `services/operations/handover_service.py`
- [ ] Create `services/operations/zone_service.py`
- [ ] Create `services/operations/sla_definition_service.py`
- [ ] Create `services/operations/priority_queue_service.py`
- [ ] Create `services/operations/quality_service.py`
- [ ] Create `services/operations/feedback_service.py`
- [ ] Create `services/operations/operations_document_service.py`
- [ ] Create `services/operations/dispatch_assignment_service.py`
- [ ] Create `services/operations/settings_service.py` (COMPLEX)
- [ ] Create `services/user_service.py`
- [ ] Update all `__init__.py` files in services

### Phase 2: Update Imports

- [ ] Update `api/v1/fleet/documents.py`
- [ ] Update `api/v1/fleet/fuel_logs.py`
- [ ] Update `api/v1/operations/routes.py`
- [ ] Update `api/v1/operations/handovers.py`
- [ ] Update `api/v1/operations/incidents.py`
- [ ] Update `api/v1/operations/dispatch.py`
- [ ] Update `api/v1/operations/zones.py`
- [ ] Update `api/v1/operations/sla.py`
- [ ] Update `api/v1/operations/priority_queue.py`
- [ ] Update `api/v1/operations/quality.py`
- [ ] Update `api/v1/operations/feedback.py`
- [ ] Update `api/v1/operations/document.py`
- [ ] Update `api/v1/operations/settings.py`
- [ ] Update `api/v1/hr/bonuses.py`
- [ ] Update `core/dependencies.py`
- [ ] Update `api/v1/auth.py`
- [ ] Update `services/workflow/approval_service.py`
- [ ] Update `services/workflow/execution_service.py`

### Phase 3: Testing

- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Manual API testing for affected endpoints
- [ ] Verify no import errors

### Phase 4: Cleanup

- [ ] Delete CRUD files (as listed above)
- [ ] Update `crud/__init__.py`
- [ ] Remove empty directories

### Post-Migration

- [ ] Run full test suite
- [ ] Update documentation
- [ ] Code review
- [ ] Deploy to staging
- [ ] Monitor for issues

---

## Risk Mitigation

1. **Gradual Migration**: Migrate one domain at a time (fleet -> hr -> operations -> workflow)
2. **Parallel Existence**: Keep old CRUD files until all tests pass
3. **Feature Flags**: Consider feature flags for critical paths
4. **Rollback Plan**: Keep backup branch, ready to revert

---

## Benefits After Migration

1. **Reduced Redundancy**: ~40 fewer files to maintain
2. **Single Source of Truth**: All data operations in services layer
3. **Consistent Patterns**: All code follows service pattern
4. **Better Testing**: Services are easier to mock and test
5. **Clearer Architecture**: API -> Service -> Model (no CRUD layer)

---

## Notes

- Method name change: `remove()` (CRUD) -> `delete()` (Services)
- The `TenantAwareCRUD` base class is kept as it provides specific multi-tenant functionality
- Some CRUD files have additional custom methods that need careful migration
- The `crud/operations/settings.py` is the most complex migration due to 5 separate classes
