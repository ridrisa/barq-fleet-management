# BARQ Fleet Management - Model Summary

## Quick Reference

**Total Models**: 80+
**Database**: PostgreSQL 14+
**Generated**: December 2, 2025

---

## Model Statistics by Module

| Module | Models | Key Features |
|--------|--------|--------------|
| Fleet Management | 12 | Courier tracking, vehicle management, assignments |
| HR Management | 8 | Payroll, attendance, leaves, loans, assets |
| Operations | 12 | Deliveries, COD, routes, zones, quality, SLA |
| Workflow Engine | 23 | Approvals, automations, SLA, triggers, notifications |
| Analytics | 5 | Performance, metrics, reports, dashboards, KPIs |
| Support | 11 | Tickets, KB, chat, feedback, templates |
| Accommodation | 4 | Buildings, rooms, beds, allocations |
| Admin & System | 8 | Users, roles, permissions, API keys, audit |
| Multi-Tenancy | 2 | Organizations, org-user relationships |

---

## Fleet Management Models

### Courier
**Table**: `couriers`
**Purpose**: Master data for all couriers/drivers

**Key Fields**:
- `barq_id` (UK) - Unique BARQ identifier
- `full_name` - Full name
- `email` (UK) - Email address
- `mobile_number` - Phone number
- `status` - Employment status (ACTIVE, INACTIVE, ON_LEAVE, TERMINATED, ONBOARDING, SUSPENDED)
- `sponsorship_status` - Sponsorship type (AJEER, INHOUSE, TRIAL, FREELANCER)
- `project_type` - Project assignment (ECOMMERCE, FOOD, WAREHOUSE, BARQ, MIXED)
- `current_vehicle_id` (FK) - Currently assigned vehicle

**Relationships**:
- Has many: `vehicle_assignments`, `vehicle_logs`, `accident_logs`, `leaves`, `loans`, `attendance`, `salaries`, `assets`, `bonuses`, `deliveries`, `performance_data`
- Belongs to: `vehicle` (current assignment)

**Indexes**:
- `ix_couriers_barq_id` (UK)
- `ix_couriers_email` (UK)
- `ix_couriers_status`
- `ix_couriers_city`
- Full-text search on name, email, phone

---

### Vehicle
**Table**: `vehicles`
**Purpose**: Vehicle fleet master data

**Key Fields**:
- `plate_number` (UK) - License plate
- `vehicle_type` - Type (MOTORCYCLE, CAR, VAN, TRUCK)
- `status` - Status (ACTIVE, INACTIVE, MAINTENANCE, RETIRED)
- `fuel_type` - Fuel type (GASOLINE, DIESEL, ELECTRIC, HYBRID)
- `ownership_type` - Ownership (OWNED, LEASED, RENTED)

**Relationships**:
- Has many: `assignments`, `maintenance_records`, `inspections`, `accident_logs`, `fuel_logs`
- Has many: `assigned_couriers` (through assignments)

**Indexes**:
- `ix_vehicles_plate_number` (UK)
- `ix_vehicles_status`
- `ix_vehicles_type`

---

### CourierVehicleAssignment
**Table**: `courier_vehicle_assignments`
**Purpose**: Track courier-vehicle assignments over time

**Key Fields**:
- `courier_id` (FK) - Assigned courier
- `vehicle_id` (FK) - Assigned vehicle
- `start_date` - Assignment start
- `end_date` - Assignment end (NULL if active)
- `assignment_type` - Type (PERMANENT, TEMPORARY, TRIAL)
- `status` - Status (ACTIVE, COMPLETED, CANCELLED)

**Indexes**:
- `ix_assignments_courier_id`
- `ix_assignments_vehicle_id`
- `ix_assignments_status`
- Composite: `(courier_id, start_date)`

---

## HR Management Models

### Leave
**Table**: `leaves`
**Purpose**: Leave request and approval tracking

**Key Fields**:
- `courier_id` (FK) - Requesting courier
- `leave_type` - Type (ANNUAL, SICK, EMERGENCY, UNPAID, MATERNITY, PATERNITY, HAJJ)
- `start_date` - Leave start
- `end_date` - Leave end
- `status` - Status (PENDING, APPROVED, REJECTED, CANCELLED)
- `approver_id` (FK) - Approving manager

**Indexes**:
- `ix_leaves_courier_id`
- `ix_leaves_status`
- `ix_leaves_leave_type`

---

### Attendance
**Table**: `attendance`
**Purpose**: Daily attendance tracking

**Key Fields**:
- `courier_id` (FK) - Courier
- `date` - Attendance date
- `clock_in` - Clock-in time
- `clock_out` - Clock-out time
- `hours_worked` - Calculated hours
- `status` - Status (PRESENT, ABSENT, LATE, HALF_DAY, ON_LEAVE)

**Indexes**:
- `ix_attendance_courier_id`
- `ix_attendance_date`
- Composite: `(courier_id, date)` UK

---

### Salary
**Table**: `salaries`
**Purpose**: Salary records and payroll

**Key Fields**:
- `courier_id` (FK) - Courier
- `base_salary` - Base salary amount
- `allowances` - Total allowances
- `deductions` - Total deductions
- `net_salary` - Net payable
- `payment_date` - Payment date
- `month` - Salary month
- `year` - Salary year

**Indexes**:
- `ix_salaries_courier_id`
- Composite: `(courier_id, year, month)`

---

## Operations Models

### Delivery
**Table**: `deliveries`
**Purpose**: Delivery order tracking

**Key Fields**:
- `tracking_number` (UK) - Unique tracking number
- `courier_id` (FK) - Assigned courier
- `route_id` (FK) - Assigned route
- `pickup_address` - Pickup location
- `delivery_address` - Delivery location
- `status` - Status (PENDING, IN_TRANSIT, DELIVERED, FAILED, RETURNED)
- `pickup_time` - Actual pickup time
- `delivery_time` - Actual delivery time
- `cod_amount` - COD amount

**Relationships**:
- Belongs to: `courier`, `route`
- Has many: `cod_transactions`, `quality_inspections`, `sla_tracking`

**Indexes**:
- `ix_deliveries_tracking_number` (UK)
- `ix_deliveries_courier_id`
- `ix_deliveries_status`
- Composite: `(courier_id, status, pickup_time)`

---

### COD (Cash on Delivery)
**Table**: `cod_transactions`
**Purpose**: COD collection and reconciliation

**Key Fields**:
- `courier_id` (FK) - Collecting courier
- `amount` - COD amount
- `collection_date` - Collection date
- `status` - Status (COLLECTED, PENDING_DEPOSIT, DEPOSITED, RECONCILED, DISPUTED)
- `deposit_date` - Deposit date
- `reconciliation_date` - Reconciliation date

**Indexes**:
- `ix_cod_courier_id`
- `ix_cod_status`
- `ix_cod_collection_date`

---

### Route
**Table**: `routes`
**Purpose**: Route planning and optimization

**Key Fields**:
- `name` - Route name
- `zone_id` (FK) - Service zone
- `waypoints` (JSONB) - Route waypoints
- `distance_km` - Total distance
- `estimated_time_minutes` - Estimated time
- `status` - Status (ACTIVE, COMPLETED, CANCELLED)

**Indexes**:
- `ix_routes_zone_id`
- `ix_routes_status`

---

### Zone
**Table**: `zones`
**Purpose**: Service zone definitions

**Key Fields**:
- `name` - Zone name
- `code` (UK) - Zone code
- `boundaries` (JSONB) - GeoJSON boundaries
- `status` - Status (ACTIVE, INACTIVE)
- `capacity` - Delivery capacity
- `pricing_multiplier` - Pricing multiplier

**Indexes**:
- `ix_zones_code` (UK)
- `ix_zones_status`
- GiST index on geometry (if using PostGIS)

---

## Analytics Models

### PerformanceData
**Table**: `performance_data`
**Purpose**: Daily courier performance tracking

**Key Fields**:
- `courier_id` (FK) - Courier
- `date` - Performance date
- `orders_completed` - Orders completed
- `orders_failed` - Orders failed
- `on_time_deliveries` - On-time deliveries
- `distance_covered_km` - Distance covered
- `revenue_generated` - Revenue generated
- `cod_collected` - COD collected
- `efficiency_score` - Performance score (0-100)

**Indexes**:
- `ix_performance_courier_id`
- `ix_performance_date`
- Composite: `(courier_id, date)` UK

---

### MetricSnapshot
**Table**: `metric_snapshots`
**Purpose**: Time-series metrics storage

**Key Fields**:
- `metric_name` - Metric name (e.g., 'active_couriers', 'total_deliveries')
- `metric_type` - Type (counter, gauge, histogram)
- `value` - Metric value
- `dimensions` (JSONB) - Flexible dimensions (city, zone, etc.)
- `timestamp` - Recording timestamp
- `tags` (JSONB) - Additional tags

**Indexes**:
- `ix_metric_snapshots_metric_name`
- `ix_metric_snapshots_timestamp`
- Composite: `(metric_name, timestamp)`
- GIN: `dimensions`, `tags`

**Use Cases**:
- Store time-series data for dashboards
- Track system-wide metrics
- Build custom analytics queries

---

### Report
**Table**: `reports`
**Purpose**: Generated report management

**Key Fields**:
- `name` - Report name
- `report_type` - Type (COURIER_PERFORMANCE, FLEET_UTILIZATION, DELIVERY_ANALYTICS, etc.)
- `status` - Status (PENDING, GENERATING, COMPLETED, FAILED, SCHEDULED)
- `format` - Format (PDF, EXCEL, CSV, JSON)
- `parameters` (JSONB) - Report parameters
- `generated_at` - Generation timestamp
- `file_path` - File storage path
- `generated_by_user_id` (FK) - Generator user

**Indexes**:
- `ix_reports_name`
- `ix_reports_report_type`
- `ix_reports_status`
- Composite: `(report_type, status)`

---

### Dashboard
**Table**: `dashboards`
**Purpose**: Custom user dashboards

**Key Fields**:
- `user_id` (FK) - Dashboard owner
- `name` - Dashboard name
- `widgets` (JSONB) - Widget configurations
- `layout` (JSONB) - Layout configuration
- `is_default` - Is default dashboard
- `is_shared` - Is shared with team
- `refresh_interval_seconds` - Auto-refresh interval

**Indexes**:
- `ix_dashboards_user_id`
- Composite: `(user_id, is_default)`
- GIN: `widgets`

---

### KPI
**Table**: `kpis`
**Purpose**: Key Performance Indicator tracking

**Key Fields**:
- `code` (UK) - Unique KPI code
- `name` - KPI name
- `category` - Category (operations, hr, finance, etc.)
- `current_value` - Current value
- `target_value` - Target value
- `warning_threshold` - Warning threshold
- `critical_threshold` - Critical threshold
- `trend` - Trend (UP, DOWN, STABLE)
- `period` - Period (DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY)
- `calculation_formula` - Calculation formula
- `historical_data` (JSONB) - Historical values

**Indexes**:
- `ix_kpis_code` (UK)
- `ix_kpis_category`
- `ix_kpis_is_active`
- Composite: `(category, is_active)`

**Properties**:
- `achievement_percentage` - Calculated achievement %
- `is_on_target` - Boolean target check
- `status_color` - Status color (red, yellow, green)

---

## Workflow Engine Models

### WorkflowTemplate
**Table**: `workflow_templates`
**Purpose**: Workflow process definitions

**Key Fields**:
- `name` - Template name
- `code` (UK) - Unique code
- `category` - Category
- `definition` (JSONB) - Workflow steps definition
- `version` - Template version
- `is_active` - Is active
- `is_published` - Is published

**Relationships**:
- Has many: `workflow_instances`, `workflow_sla`
- Has one: `approval_chain`

---

### WorkflowInstance
**Table**: `workflow_instances`
**Purpose**: Running workflow instances

**Key Fields**:
- `template_id` (FK) - Template
- `status` - Status (DRAFT, ACTIVE, COMPLETED, CANCELLED, FAILED)
- `current_step` - Current step number
- `data` (JSONB) - Instance data
- `initiated_by_user_id` (FK) - Initiator
- `started_at` - Start timestamp
- `completed_at` - Completion timestamp

**Relationships**:
- Belongs to: `workflow_template`, `user` (initiator)
- Has many: `approval_requests`, `comments`, `attachments`, `history`

---

## Support Models

### Ticket
**Table**: `tickets`
**Purpose**: Customer support ticket tracking

**Key Fields**:
- `ticket_number` (UK) - Unique ticket number
- `subject` - Ticket subject
- `description` - Ticket description
- `category` - Category (TECHNICAL, BILLING, GENERAL, COMPLAINT, FEATURE_REQUEST)
- `priority` - Priority (LOW, MEDIUM, HIGH, URGENT)
- `status` - Status (OPEN, IN_PROGRESS, WAITING_CUSTOMER, RESOLVED, CLOSED)
- `requester_id` (FK) - Requesting user
- `assignee_id` (FK) - Assigned agent

**Relationships**:
- Has many: `ticket_replies`, `ticket_attachments`
- Belongs to: `requester` (User), `assignee` (User)

---

### KBArticle
**Table**: `kb_articles`
**Purpose**: Knowledge base articles

**Key Fields**:
- `title` - Article title
- `slug` (UK) - URL slug
- `content` - Article content (Markdown)
- `category_id` (FK) - Category
- `status` - Status (DRAFT, PUBLISHED, ARCHIVED)
- `view_count` - View count
- `helpful_count` - Helpful votes

**Indexes**:
- `ix_kb_articles_slug` (UK)
- `ix_kb_articles_status`
- `ix_kb_articles_category_id`
- Full-text search on title and content

---

## Admin & System Models

### User
**Table**: `users`
**Purpose**: System user accounts

**Key Fields**:
- `email` (UK) - Email address
- `name` - Full name
- `is_active` - Account active status
- `is_superuser` - Superuser flag
- `hashed_password` - Password hash
- `google_id` - Google OAuth ID

**Relationships**:
- Has many: `api_keys`, `audit_logs`, `dashboards`, `reports`
- Belongs to many: `roles`, `organizations`

---

### Role
**Table**: `roles`
**Purpose**: Role-based access control

**Key Fields**:
- `name` (UK) - Role name
- `description` - Role description
- `is_system` - System role flag

**Relationships**:
- Has many: `permissions` (through role_permissions)
- Has many: `users` (through user_roles)

---

### AuditLog
**Table**: `audit_logs`
**Purpose**: Audit trail for all changes

**Key Fields**:
- `user_id` (FK) - User who made change
- `action` - Action (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.)
- `resource` - Resource type
- `resource_id` - Resource ID
- `old_value` (JSONB) - Old value
- `new_value` (JSONB) - New value
- `ip_address` - IP address
- `timestamp` - Action timestamp

**Indexes**:
- `ix_audit_logs_user_id`
- `ix_audit_logs_action`
- `ix_audit_logs_resource`
- `ix_audit_logs_timestamp`

---

## Multi-Tenancy Models

### Organization
**Table**: `organizations`
**Purpose**: Tenant organization management

**Key Fields**:
- `name` - Organization name
- `slug` (UK) - URL slug
- `subscription_plan` - Plan (FREE, BASIC, PROFESSIONAL, ENTERPRISE)
- `subscription_status` - Status (TRIAL, ACTIVE, SUSPENDED, CANCELLED)
- `max_users` - Maximum users
- `max_vehicles` - Maximum vehicles
- `features` (JSONB) - Enabled features

**Relationships**:
- Has many: `organization_users`
- Has many: `users` (through organization_users)

---

## Common Query Patterns

### Fleet Queries

```python
# Get active couriers with their vehicles
from sqlalchemy.orm import joinedload

couriers = session.query(Courier)\
    .filter(Courier.status == CourierStatus.ACTIVE)\
    .options(joinedload(Courier.current_vehicle))\
    .all()

# Get vehicles due for maintenance
from datetime import date, timedelta

vehicles = session.query(Vehicle)\
    .outerjoin(VehicleMaintenance)\
    .filter(Vehicle.status == VehicleStatus.ACTIVE)\
    .group_by(Vehicle.id)\
    .having(
        or_(
            func.max(VehicleMaintenance.service_date) < date.today() - timedelta(days=30),
            func.max(VehicleMaintenance.service_date).is_(None)
        )
    )\
    .all()
```

### Performance Queries

```python
# Get top performers this month
from datetime import datetime

month_start = datetime.now().replace(day=1)

top_performers = session.query(
    Courier.barq_id,
    Courier.full_name,
    func.sum(PerformanceData.orders_completed).label('total_orders'),
    func.avg(PerformanceData.efficiency_score).label('avg_score')
)\
    .join(PerformanceData)\
    .filter(PerformanceData.date >= month_start)\
    .group_by(Courier.id)\
    .order_by(desc('avg_score'))\
    .limit(10)\
    .all()
```

### Analytics Queries

```python
# Get metric snapshots for charting
snapshots = session.query(MetricSnapshot)\
    .filter(
        MetricSnapshot.metric_name == 'active_couriers',
        MetricSnapshot.timestamp >= datetime.now() - timedelta(days=30)
    )\
    .order_by(MetricSnapshot.timestamp)\
    .all()

# KPI achievement
kpis = session.query(KPI)\
    .filter(
        KPI.is_active == True,
        KPI.target_value > 0
    )\
    .all()

for kpi in kpis:
    print(f"{kpi.name}: {kpi.achievement_percentage:.2f}%")
```

---

## Best Practices

### Query Optimization
1. Use `joinedload()` for one-to-one/many-to-one relationships
2. Use `selectinload()` for one-to-many relationships
3. Filter on indexed columns
4. Avoid N+1 queries with proper eager loading
5. Use query profiling (`EXPLAIN ANALYZE`)

### Model Design
1. Always add indexes on foreign keys
2. Use appropriate column types (avoid generic Text for everything)
3. Add database-level constraints where possible
4. Use enums for fixed value sets
5. Add timestamps (created_at, updated_at) to all models

### Data Integrity
1. Use foreign key constraints with appropriate `ondelete` actions
2. Add unique constraints where needed
3. Use check constraints for business rules
4. Validate data in both application and database layers

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0.14 | 2025-12-02 | Added advanced analytics models (MetricSnapshot, Report, Dashboard, KPI) |
| v1.0.13 | 2025-12-01 | Added workflow versioning support |
| v1.0.12 | 2025-12-01 | Extended support models (templates, attachments, categories) |
| v1.0.11 | 2025-11-16 | Added document management |
| v1.0.0 | 2025-11-06 | Initial schema |

---

**Last Updated**: December 2, 2025
**Maintained By**: Database Architecture Team
