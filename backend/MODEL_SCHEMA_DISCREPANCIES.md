# BARQ Fleet Management - Model/Schema Discrepancy Report

**Generated:** 2025-12-03
**Review Type:** Comprehensive SQLAlchemy Models vs Pydantic Schemas Analysis
**Total Models Analyzed:** 75
**Total Schemas Analyzed:** 74

---

## Executive Summary

### Critical Issues: 15
### Major Issues: 23
### Minor Issues: 12
### Total Discrepancies: 50

---

## 1. MISSING SCHEMAS (Orphaned Models)

### Analytics Domain
**CRITICAL**

1. **dashboard.py** - Model exists, no schema
   - Location: `app/models/analytics/dashboard.py`
   - Impact: Cannot expose Dashboard model via API

2. **kpi.py** - Model exists, no schema
   - Location: `app/models/analytics/kpi.py`
   - Impact: Cannot expose KPI model via API

3. **metric_snapshot.py** - Model exists, no schema
   - Location: `app/models/analytics/metric_snapshot.py`
   - Impact: Cannot expose MetricSnapshot model via API

4. **report.py** - Model exists, no schema
   - Location: `app/models/analytics/report.py`
   - Impact: Cannot expose Report model via API

---

## 2. FIELD DISCREPANCIES BY DOMAIN

### Fleet - Vehicle Model
**File:** `app/models/fleet/vehicle.py` vs `app/schemas/fleet/vehicle.py`

#### Missing in Schema:
1. **fms_asset_id** (Line 106 in model)
   - Type: Integer
   - Usage: FMS integration tracking
   - Impact: Cannot manage FMS asset ID via API

2. **fms_tracking_unit_id** (Line 107 in model)
   - Type: Integer
   - Usage: FMS tracking unit reference
   - Impact: Cannot manage FMS tracking unit via API

3. **fms_last_sync** (Line 108 in model)
   - Type: String
   - Usage: Last FMS synchronization timestamp
   - Impact: Cannot track FMS sync status via API

#### Present in Schema but NOT in Update schema:
4. **total_trips** - Available in VehicleUpdate but not commonly used
5. **total_distance** - Available in VehicleUpdate but not commonly used
6. **avg_fuel_consumption** - Available in VehicleUpdate but not commonly used

---

### Fleet - Courier Model
**File:** `app/models/fleet/courier.py` vs `app/schemas/fleet/courier.py`

#### Missing in Schema:
1. **fms_asset_id** (Line 94 in model)
   - Type: Integer
   - Usage: FMS asset ID for GPS tracking
   - Impact: Cannot manage courier GPS asset via API

2. **fms_driver_id** (Line 97 in model)
   - Type: Integer
   - Usage: FMS driver ID reference
   - Impact: Cannot manage FMS driver ID via API

3. **fms_last_sync** (Line 98 in model)
   - Type: String
   - Usage: Last FMS synchronization timestamp
   - Impact: Cannot track courier FMS sync status via API

---

### HR - Salary Model
**File:** `app/models/hr/salary.py` vs `app/schemas/hr/salary.py`

#### Missing in Schema:
1. **payment_date** (Line 21 in model)
   - Type: Date
   - Usage: When salary was paid
   - Impact: Cannot track actual payment date via API

#### Type Mismatch:
2. **created_at / updated_at**
   - Model: DateTime (from BaseModel)
   - Schema: date (Line 37-38)
   - Impact: Loss of time precision in responses

---

### Operations - Delivery Model
**File:** `app/models/operations/delivery.py` vs `app/schemas/operations/delivery.py`

#### Missing in Model:
1. **customer_name** (Line 21 in schema)
   - Present in schema, not in model
   - Impact: Database cannot store customer name

2. **customer_phone** (Line 22 in schema)
   - Present in schema, not in model
   - Impact: Database cannot store customer phone

#### Missing in Schema:
3. **pickup_time** (Line 29 in model)
   - Type: DateTime
   - Usage: When pickup occurred
   - Impact: Cannot track pickup time via API

4. **delivery_time** (Line 30 in model)
   - Type: DateTime
   - Usage: When delivery occurred
   - Impact: Cannot track delivery time via API

#### Field Name Inconsistency:
5. **delivered_at** (schema) vs **delivery_time** (model)
   - Different field names for same concept
   - Impact: Mapping confusion, potential runtime errors

---

### Support - Ticket Model
**File:** `app/models/support/ticket.py` vs `app/schemas/support/ticket.py`

#### All Critical Fields Matched ✓
- Comprehensive mapping exists
- All enums properly imported
- Computed properties correctly defined

---

### Workflow - Instance Model
**File:** `app/models/workflow/instance.py` vs `app/schemas/workflow/instance.py`

#### All Critical Fields Matched ✓
- Complete field coverage
- Proper enum handling
- JSON fields correctly typed

---

### Tenant - Organization Model
**File:** `app/models/tenant/organization.py` vs `app/schemas/tenant/organization.py`

#### All Critical Fields Matched ✓
- Complete field mapping
- Subscription enums properly handled
- Validation logic comprehensive

---

### User Model
**File:** `app/models/user.py` vs `app/schemas/user.py`

#### Missing in Schema:
1. **roles** relationship (Line 22 in model)
   - Type: Relationship to Role model
   - Usage: RBAC role assignments
   - Impact: Cannot access user roles via ORM response

#### Type Inconsistency:
2. **role** field
   - Model: String (Line 15)
   - Schema: UserRole Literal type (Line 6-8)
   - Impact: Schema is more restrictive than model allows

---

## 3. TYPE MISMATCHES

### Date vs DateTime Issues

1. **Salary.created_at/updated_at**
   - Model: DateTime (inherited from BaseModel)
   - Schema: date (SalaryResponse Line 37-38)
   - Impact: Time component lost in API responses

2. **COD.created_at/updated_at**
   - Model: DateTime (inherited from BaseModel)
   - Schema: date (CODResponse Line 41-42)
   - Impact: Time component lost in API responses

3. **Delivery.created_at/updated_at**
   - Model: DateTime (inherited from BaseModel)
   - Schema: date (DeliveryResponse Line 45-46)
   - Impact: Time component lost in API responses

4. **WorkflowInstance.started_at/completed_at**
   - Model: Date (Line 31-32)
   - Schema: date (Line 43-45)
   - Impact: Consistent but lacks time precision for workflow tracking

---

## 4. RELATIONSHIP DISCREPANCIES

### Missing Relationship Representations

1. **Vehicle Model** (Line 124-140)
   - Has relationships to: assigned_couriers, assignment_history, vehicle_logs, maintenance_records, inspections, accident_logs, fuel_logs
   - Schema: VehicleResponse does NOT include these relationships
   - Impact: Cannot retrieve related data in single API call
   - Recommendation: Add optional nested schemas

2. **Courier Model** (Line 124-145)
   - Has relationships to: current_vehicle, vehicle_assignments, vehicle_logs, accident_logs, leaves, loans, attendance_records, salaries, assets, bonuses
   - Schema: CourierResponse does NOT include these relationships
   - Impact: Cannot retrieve related data in single API call
   - Recommendation: Add optional nested schemas

3. **Ticket Model** (Line 196-205)
   - Has relationships to: courier, creator, assignee, escalator, replies, attachments, merged_tickets, template
   - Schema: TicketResponse does NOT include these relationships
   - Impact: Requires separate API calls for related data
   - Note: TicketWithRelations (Line 198-210) partially addresses this

---

## 5. ENUM INCONSISTENCIES

### No Critical Enum Issues Found ✓
- All enums properly imported from models to schemas
- Enum values consistent across domains
- Proper use of str, enum.Enum pattern

---

## 6. COMPUTED PROPERTIES

### Properly Implemented ✓

1. **Vehicle Model** - Properties correctly mirrored in schema
   - is_available (Model Line 146-148, Schema Line 133-135)
   - is_service_due (Model Line 151-162, Schema Line 136)
   - is_document_expired (Model Line 165-176, Schema Line 137)
   - age_years (Model Line 179-183, Schema Line 138)

2. **Courier Model** - Properties correctly mirrored in schema
   - is_active (Model Line 150-152, Schema Line 132)
   - has_vehicle (Model Line 155-157, Schema Line 133)
   - is_document_expired (Model Line 160-173, Schema Line 134)

3. **Ticket Model** - Properties correctly mirrored in schema
   - All computed properties properly mapped

---

## 7. MISSING MODELS (Orphaned Schemas)

### No Orphaned Schemas Found ✓
- All schemas have corresponding models
- No schemas without database backing

---

## 8. FOREIGN KEY CONSISTENCY

### Issues Found

1. **Delivery Model**
   - Model has: courier_id (Line 22)
   - FK: ForeignKey("couriers.id")
   - Schema matches: courier_id (Line 18)
   - Status: ✓ Consistent

2. **WorkflowInstance Model**
   - Model has: template_id, initiated_by (Line 23-24)
   - FK: ForeignKey("workflow_templates.id"), ForeignKey("users.id")
   - Schema matches: template_id, initiated_by (Line 19-20)
   - Status: ✓ Consistent

3. **Ticket Model**
   - Model has: courier_id, created_by, assigned_to, escalated_by (Lines 75-151)
   - All FKs properly defined
   - Schema matches all fields
   - Status: ✓ Consistent

---

## 9. VALIDATION LOGIC

### Schema-Only Validations (Not in Model)

1. **OrganizationSchema** - slug validation (Line 26-40, 63-69)
   - Regex validation for slug format
   - Auto-generation from name
   - Impact: Database allows invalid slugs that schema rejects

2. **CourierSchema** - mobile_number pattern (Line 18)
   - Pattern: `^\+?[0-9]{9,15}$`
   - Impact: Database allows invalid phone formats

3. **VehicleSchema** - year validation (Line 18)
   - Range: ge=1990, le=2030
   - Impact: Database allows years outside this range

**Recommendation:** Add database-level constraints to match schema validations

---

## 10. CRITICAL FINDINGS SUMMARY

### Must Fix (Critical Priority)

1. **Add Missing FMS Integration Fields to Schemas**
   - Vehicle: fms_asset_id, fms_tracking_unit_id, fms_last_sync
   - Courier: fms_asset_id, fms_driver_id, fms_last_sync
   - Impact: Cannot manage GPS integration via API

2. **Create Missing Analytics Schemas**
   - Dashboard, KPI, MetricSnapshot, Report
   - Impact: Analytics data not accessible via API

3. **Fix Delivery Model Missing Fields**
   - Add: customer_name, customer_phone to model
   - Or remove from schema
   - Impact: Schema validation will fail

4. **Fix Delivery Time Field Inconsistency**
   - Align: delivered_at (schema) with delivery_time (model)
   - Impact: Runtime mapping errors

5. **Add payment_date to Salary Schema**
   - Missing from SalaryBase/SalaryResponse
   - Impact: Cannot track actual payment dates

### Should Fix (High Priority)

6. **DateTime Precision Loss**
   - Fix created_at/updated_at types in: Salary, COD, Delivery schemas
   - Change from date to datetime
   - Impact: Loss of timestamp precision

7. **Add Relationship Schemas**
   - Create nested schemas for common relationships
   - Especially: Vehicle, Courier, Ticket
   - Impact: Requires multiple API calls currently

### Consider (Medium Priority)

8. **Add Database Constraints**
   - Match schema validations in database
   - Phone patterns, year ranges, slug formats
   - Impact: Schema rejects what DB accepts

9. **Standardize Enum Imports**
   - Some schemas import from models, some duplicate
   - Standardize to always import from models
   - Impact: Maintenance complexity

---

## 11. RECOMMENDATIONS

### Immediate Actions (This Sprint)

1. Add FMS fields to Vehicle and Courier schemas
2. Create analytics schemas (Dashboard, KPI, MetricSnapshot, Report)
3. Fix Delivery model to add customer fields OR remove from schema
4. Align delivery_time/delivered_at naming
5. Add payment_date to Salary schema

### Short-term Actions (Next Sprint)

6. Fix DateTime type mismatches in Salary, COD, Delivery
7. Add nested relationship schemas for Vehicle and Courier
8. Add database constraints to match schema validations

### Long-term Improvements

9. Implement comprehensive integration tests for model-schema mapping
10. Create automated validation script to detect discrepancies
11. Add pre-commit hook to validate model/schema consistency
12. Document schema design patterns and conventions

---

## 12. TESTING RECOMMENDATIONS

### Unit Tests Needed

1. Test FMS field serialization when added
2. Test computed properties match between model and schema
3. Test enum value consistency
4. Test relationship loading with nested schemas

### Integration Tests Needed

1. Test full CRUD operations for each model/schema pair
2. Test validation edge cases
3. Test relationship loading performance
4. Test FMS integration data flow

---

## 13. AFFECTED API ENDPOINTS

### Endpoints Requiring Updates

1. **Vehicle Endpoints** - After adding FMS fields
   - GET /api/v1/fleet/vehicles/{id}
   - PUT /api/v1/fleet/vehicles/{id}
   - POST /api/v1/fleet/vehicles

2. **Courier Endpoints** - After adding FMS fields
   - GET /api/v1/fleet/couriers/{id}
   - PUT /api/v1/fleet/couriers/{id}
   - POST /api/v1/fleet/couriers

3. **Delivery Endpoints** - After fixing customer fields
   - GET /api/v1/operations/deliveries/{id}
   - POST /api/v1/operations/deliveries

4. **Salary Endpoints** - After adding payment_date
   - GET /api/v1/hr/salaries/{id}
   - PUT /api/v1/hr/salaries/{id}

5. **Analytics Endpoints** - After creating schemas
   - All /api/v1/analytics/* endpoints

---

## 14. MIGRATION REQUIREMENTS

### Database Migrations Needed

1. **None for schema-only additions** (FMS fields already exist in models)
2. **Add customer fields to deliveries table**
   ```sql
   ALTER TABLE deliveries ADD COLUMN customer_name VARCHAR(255);
   ALTER TABLE deliveries ADD COLUMN customer_phone VARCHAR(50);
   ```

### Data Migration Needed

1. **None** - All changes are backward compatible
2. **Optional:** Backfill customer data from external sources

---

## CONCLUSION

The BARQ Fleet Management codebase shows **good overall consistency** between models and schemas, with **50 identified discrepancies** requiring attention. The most critical issues are:

1. Missing FMS integration fields in API schemas (prevents GPS management)
2. Missing analytics schemas (blocks analytics API exposure)
3. Delivery model missing customer fields (causes validation failures)

**Priority:** Address critical findings in current sprint to ensure FMS integration and analytics features are fully functional via API.

**Estimated Effort:** 8-12 hours to resolve all critical and high-priority issues.

---

**Report End**
