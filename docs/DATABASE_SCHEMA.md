# BARQ Fleet Management - Database Schema Documentation

**Version:** 1.2.0
**Database:** PostgreSQL 16
**Last Updated:** December 9, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Schema Diagram](#schema-diagram)
3. [Core Module](#core-module)
4. [Fleet Module](#fleet-module)
5. [HR & Finance Module](#hr--finance-module)
6. [Operations Module](#operations-module)
7. [Accommodation Module](#accommodation-module)
8. [Workflow Module](#workflow-module)
9. [Support Module](#support-module)
10. [Analytics Module](#analytics-module)
11. [Admin Module](#admin-module)
12. [Integrations Module](#integrations-module)
13. [Enums Reference](#enums-reference)
14. [Migration History](#migration-history)

---

## Overview

### Database Information

- **Name:** barq_fleet
- **Engine:** PostgreSQL 16
- **Character Set:** UTF-8
- **Collation:** en_US.UTF-8
- **Total Tables:** 93+
- **Total Migrations:** 20+

### Design Principles

1. **Multi-Tenancy:** TenantMixin adds `organization_id` to all tenant-aware tables
2. **Base Fields:** All models have `id`, `created_at`, `updated_at` via BaseModel
3. **Primary Keys:** Integer (SERIAL) for all entities
4. **Soft Deletes:** Optional via SoftDeleteMixin (`is_deleted`, `deleted_at`)
5. **Audit Trail:** AuditMixin adds `created_by`, `updated_by` tracking
6. **Enums:** PostgreSQL native enums for type safety
7. **Indexes:** Strategic indexing on foreign keys and frequently queried columns

### Common Mixins

```python
# TenantMixin - Added to all tenant-aware models
organization_id: Integer  # FK to organizations.id, CASCADE delete

# SoftDeleteMixin - Optional soft delete support
is_deleted: Boolean
deleted_at: DateTime
deleted_by: Integer (FK users.id)

# AuditMixin - Optional audit trail
created_by: Integer (FK users.id)
updated_by: Integer (FK users.id)
```

---

## Schema Diagram

### Entity Relationship Overview

```
┌─────────────────────────┐
│     organizations       │
└────────────┬────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼───┐        ┌───▼────┐
│ users │        │  roles │
└───┬───┘        └───┬────┘
    │                │
    └───────┬────────┘
            │
    ┌───────▼────────────────┐
    │                        │
┌───▼────┐            ┌─────▼────┐
│couriers│            │ vehicles │
└───┬────┘            └────┬─────┘
    │                      │
    └──────────┬───────────┘
               │
    ┌──────────▼──────────────────┐
    │ courier_vehicle_assignments │
    └──────────┬──────────────────┘
               │
      ┌────────┴─────────┐
      │                  │
┌─────▼────┐      ┌─────▼──────┐
│attendance│      │ deliveries │
└──────────┘      └─────┬──────┘
                        │
          ┌─────────────┼─────────────┐
          │             │             │
   ┌──────▼──────┐ ┌───▼────┐ ┌─────▼──────┐
   │dispatch_    │ │priority│ │sla_tracking│
   │assignments  │ │_queue  │ │            │
   └─────────────┘ └────────┘ └────────────┘
```

---

## Core Module

### Table: users

**Purpose:** System users (admins, managers, dispatchers, etc.)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| hashed_password | VARCHAR(255) | NOT NULL | Argon2 password hash |
| full_name | VARCHAR(200) | NOT NULL | Full name |
| phone | VARCHAR(20) | NULL | Phone number |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| is_superuser | BOOLEAN | DEFAULT FALSE | Superuser flag |
| role_id | INTEGER | FK roles.id | User role |
| last_login | TIMESTAMP | NULL | Last login time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**Relationships:**
- `role` → Role (many-to-one)
- `password_reset_tokens` → PasswordResetToken (one-to-many)
- `audit_logs` → AuditLog (one-to-many)

---

### Table: roles

**Purpose:** User roles for access control

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Role name |
| display_name | VARCHAR(100) | NULL | Display name |
| description | TEXT | NULL | Role description |
| is_system | BOOLEAN | DEFAULT FALSE | System-defined role |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**Relationships:**
- `permissions` → Permission (many-to-many via role_permissions)
- `users` → User (one-to-many)

---

### Table: permissions

**Purpose:** Granular permissions for RBAC

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| name | VARCHAR(100) | NOT NULL, UNIQUE | Permission name |
| action | ENUM | NOT NULL | PermissionAction enum |
| resource | ENUM | NOT NULL | PermissionResource enum |
| description | TEXT | NULL | Description |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**PermissionAction Enum:** `CREATE`, `READ`, `UPDATE`, `DELETE`, `MANAGE`, `EXPORT`, `IMPORT`, `APPROVE`, `REJECT`

**PermissionResource Enum:** `USERS`, `ROLES`, `COURIERS`, `VEHICLES`, `DELIVERIES`, `ZONES`, `ROUTES`, `LEAVES`, `LOANS`, `SALARIES`, `ATTENDANCE`, `ASSETS`, `BUILDINGS`, `ROOMS`, `TICKETS`, `REPORTS`, `SETTINGS`, `ORGANIZATIONS`, `AUDIT_LOGS`, `API_KEYS`, `BACKUPS`, `INTEGRATIONS`, `WORKFLOWS`, `ALL`

---

### Table: role_permissions

**Purpose:** Junction table for roles and permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| role_id | INTEGER | FK roles.id | Role reference |
| permission_id | INTEGER | FK permissions.id | Permission reference |

**Constraints:** PRIMARY KEY (role_id, permission_id)

---

### Table: organizations

**Purpose:** Multi-tenancy support (tenant isolation)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| name | VARCHAR(200) | NOT NULL | Organization name |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | URL-safe identifier |
| email | VARCHAR(200) | NULL | Contact email |
| phone | VARCHAR(20) | NULL | Contact phone |
| address | TEXT | NULL | Address |
| logo_url | VARCHAR(500) | NULL | Logo URL |
| subscription_plan | ENUM | DEFAULT 'FREE' | SubscriptionPlan enum |
| subscription_status | ENUM | DEFAULT 'TRIAL' | SubscriptionStatus enum |
| trial_ends_at | TIMESTAMP | NULL | Trial expiration |
| max_users | INTEGER | DEFAULT 5 | Max users allowed |
| max_couriers | INTEGER | DEFAULT 50 | Max couriers allowed |
| max_vehicles | INTEGER | DEFAULT 25 | Max vehicles allowed |
| settings | JSONB | NULL | Organization settings |
| is_active | BOOLEAN | DEFAULT TRUE | Status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**SubscriptionPlan Enum:** `FREE`, `BASIC`, `PROFESSIONAL`, `ENTERPRISE`
**SubscriptionStatus Enum:** `TRIAL`, `ACTIVE`, `SUSPENDED`, `CANCELLED`

---

### Table: organization_users

**Purpose:** Organization membership and roles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Organization |
| user_id | INTEGER | FK users.id | User |
| role | ENUM | NOT NULL | OrganizationRole enum |
| is_primary | BOOLEAN | DEFAULT FALSE | Primary org for user |
| is_active | BOOLEAN | DEFAULT TRUE | Membership status |
| joined_at | TIMESTAMP | NOT NULL | Join timestamp |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**OrganizationRole Enum:** `OWNER`, `ADMIN`, `MANAGER`, `MEMBER`, `VIEWER`

**Constraints:** UNIQUE (organization_id, user_id)

---

### Table: audit_logs

**Purpose:** Comprehensive audit trail for all operations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| user_id | INTEGER | FK users.id | Actor user |
| action | ENUM | NOT NULL | AuditAction enum |
| entity_type | VARCHAR(100) | NOT NULL | Entity type (e.g., 'courier') |
| entity_id | INTEGER | NULL | Entity ID |
| old_values | JSONB | NULL | Previous values |
| new_values | JSONB | NULL | New values |
| ip_address | VARCHAR(45) | NULL | Client IP (IPv6 compatible) |
| user_agent | TEXT | NULL | Client user agent |
| request_id | VARCHAR(100) | NULL | Request correlation ID |
| created_at | TIMESTAMP | NOT NULL | Action timestamp |

**AuditAction Enum:** `CREATE`, `UPDATE`, `DELETE`, `LOGIN`, `LOGOUT`, `PASSWORD_CHANGE`, `PASSWORD_RESET`, `EXPORT`, `IMPORT`, `APPROVE`, `REJECT`

---

### Table: password_reset_tokens

**Purpose:** Secure password reset token storage

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| user_id | INTEGER | FK users.id (CASCADE) | User reference |
| token_hash | VARCHAR(256) | UNIQUE, NOT NULL | SHA-256 hash of token |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| expires_at | TIMESTAMP | NOT NULL | Expiration time |
| used | BOOLEAN | DEFAULT FALSE | Whether token was used |
| used_at | TIMESTAMP | NULL | When token was used |
| ip_address | VARCHAR(45) | NULL | Requester IP |
| user_agent | VARCHAR(500) | NULL | Requester user agent |

---

## Fleet Module

### Table: couriers

**Purpose:** Courier workforce management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| barq_id | VARCHAR(50) | UNIQUE, NOT NULL | BARQ identifier |
| full_name | VARCHAR(200) | NOT NULL | Full name |
| email | VARCHAR(255) | UNIQUE | Email address |
| mobile_number | VARCHAR(20) | NOT NULL | Phone number |
| employee_id | VARCHAR(50) | NULL | Employee ID |
| status | ENUM | DEFAULT 'ONBOARDING' | CourierStatus enum |
| city | VARCHAR(100) | NULL | City |
| joining_date | DATE | NULL | Hire date |
| national_id | VARCHAR(20) | NULL | National ID |
| nationality | VARCHAR(100) | NULL | Nationality |
| iqama_number | VARCHAR(20) | NULL | Iqama number |
| iqama_expiry_date | DATE | NULL | Iqama expiry |
| license_number | VARCHAR(50) | NULL | License number |
| license_expiry_date | DATE | NULL | License expiry |
| current_vehicle_id | INTEGER | FK vehicles.id | Current vehicle |
| accommodation_building_id | INTEGER | FK buildings.id | Building |
| accommodation_room_id | INTEGER | FK rooms.id | Room |
| bank_iban | VARCHAR(34) | NULL | Bank IBAN |
| bank_name | VARCHAR(100) | NULL | Bank name |
| basic_salary | NUMERIC(10,2) | DEFAULT 0 | Base salary |
| housing_allowance | NUMERIC(10,2) | DEFAULT 0 | Housing allowance |
| transportation_allowance | NUMERIC(10,2) | DEFAULT 0 | Transport allowance |
| gosi_number | VARCHAR(20) | NULL | GOSI number |
| sponsorship_status | ENUM | DEFAULT 'COMPANY' | SponsorshipStatus |
| project_type | ENUM | DEFAULT 'BARQ' | ProjectType |
| project_name | VARCHAR(100) | NULL | Project name |
| performance_score | NUMERIC(5,2) | DEFAULT 0 | Performance score |
| total_deliveries | INTEGER | DEFAULT 0 | Total deliveries |
| average_rating | NUMERIC(3,2) | DEFAULT 0 | Average rating |
| emergency_contact_name | VARCHAR(200) | NULL | Emergency contact |
| emergency_contact_phone | VARCHAR(20) | NULL | Emergency phone |
| notes | TEXT | NULL | Notes |
| fms_driver_id | VARCHAR(100) | NULL | FMS driver ID |
| syarah_driver_id | VARCHAR(100) | NULL | Syarah driver ID |
| nana_driver_id | VARCHAR(100) | NULL | Nana driver ID |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**CourierStatus Enum (UPPERCASE):** `ACTIVE`, `INACTIVE`, `ON_LEAVE`, `TERMINATED`, `ONBOARDING`, `SUSPENDED`
**SponsorshipStatus Enum (UPPERCASE):** `COMPANY`, `PERSONAL`, `TRANSFER_IN_PROGRESS`
**ProjectType Enum (UPPERCASE):** `BARQ`, `SYARAH`, `NANA`, `OTHER`

---

### Table: vehicles

**Purpose:** Fleet vehicle inventory

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| plate_number | VARCHAR(20) | UNIQUE, NOT NULL | License plate |
| vehicle_type | ENUM | NOT NULL | VehicleType enum |
| make | VARCHAR(100) | NOT NULL | Manufacturer |
| model | VARCHAR(100) | NOT NULL | Model name |
| year | INTEGER | NOT NULL | Manufacture year |
| color | VARCHAR(50) | NULL | Color |
| status | ENUM | DEFAULT 'ACTIVE' | VehicleStatus enum |
| ownership_type | ENUM | DEFAULT 'OWNED' | OwnershipType enum |
| fuel_type | ENUM | DEFAULT 'GASOLINE' | FuelType enum |
| vin_number | VARCHAR(17) | UNIQUE | VIN number |
| engine_number | VARCHAR(50) | NULL | Engine number |
| registration_number | VARCHAR(50) | NULL | Registration number |
| registration_expiry_date | DATE | NULL | Registration expiry |
| insurance_company | VARCHAR(100) | NULL | Insurance provider |
| insurance_policy_number | VARCHAR(50) | NULL | Policy number |
| insurance_expiry_date | DATE | NULL | Insurance expiry |
| purchase_date | DATE | NULL | Purchase date |
| purchase_price | NUMERIC(12,2) | NULL | Purchase price |
| current_mileage | NUMERIC(12,2) | DEFAULT 0 | Current mileage (km) |
| last_service_date | DATE | NULL | Last service |
| next_service_due_date | DATE | NULL | Next service due |
| gps_device_id | VARCHAR(100) | NULL | GPS tracker ID |
| is_gps_active | BOOLEAN | DEFAULT FALSE | GPS active status |
| fms_asset_id | VARCHAR(100) | NULL | FMS asset ID |
| fms_tracking_unit_id | VARCHAR(100) | NULL | FMS tracking unit |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**VehicleStatus Enum (UPPERCASE):** `ACTIVE`, `MAINTENANCE`, `INACTIVE`, `RETIRED`, `REPAIR`
**VehicleType Enum (UPPERCASE):** `MOTORCYCLE`, `CAR`, `VAN`, `TRUCK`, `BICYCLE`
**FuelType Enum (UPPERCASE):** `GASOLINE`, `DIESEL`, `ELECTRIC`, `HYBRID`
**OwnershipType Enum (UPPERCASE):** `OWNED`, `LEASED`, `RENTED`

---

### Table: courier_vehicle_assignments

**Purpose:** Courier-vehicle assignment history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id | Courier |
| vehicle_id | INTEGER | FK vehicles.id | Vehicle |
| assignment_type | ENUM | DEFAULT 'PERMANENT' | AssignmentType enum |
| status | ENUM | DEFAULT 'ACTIVE' | AssignmentStatus enum |
| start_date | DATE | NOT NULL | Assignment start |
| end_date | DATE | NULL | Assignment end |
| start_mileage | INTEGER | NULL | Starting mileage |
| end_mileage | INTEGER | NULL | Ending mileage |
| assigned_by | VARCHAR(200) | NULL | Assigned by name |
| assignment_reason | TEXT | NULL | Assignment reason |
| termination_reason | TEXT | NULL | Termination reason |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**AssignmentType Enum (lowercase):** `permanent`, `temporary`, `trial`
**AssignmentStatus Enum (lowercase):** `active`, `completed`, `cancelled`

---

### Table: vehicle_maintenance

**Purpose:** Vehicle maintenance records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| vehicle_id | INTEGER | FK vehicles.id (CASCADE) | Vehicle |
| maintenance_number | VARCHAR(50) | UNIQUE, NOT NULL | Reference number |
| maintenance_type | ENUM | NOT NULL | MaintenanceType enum |
| status | ENUM | DEFAULT 'SCHEDULED' | MaintenanceStatus enum |
| priority | VARCHAR(20) | DEFAULT 'NORMAL' | Priority level |
| service_provider | ENUM | NULL | ServiceProvider enum |
| service_provider_name | VARCHAR(200) | NULL | Provider name |
| scheduled_date | DATE | NOT NULL | Scheduled date |
| started_at | TIMESTAMP | NULL | Start time |
| completed_at | TIMESTAMP | NULL | Completion time |
| mileage_at_service | NUMERIC(10,2) | NULL | Mileage at service |
| description | TEXT | NULL | Description |
| diagnosis | TEXT | NULL | Diagnosis |
| work_performed | TEXT | NULL | Work performed |
| parts_replaced | TEXT | NULL | Parts replaced |
| labor_cost | NUMERIC(10,2) | DEFAULT 0 | Labor cost |
| parts_cost | NUMERIC(10,2) | DEFAULT 0 | Parts cost |
| total_cost | NUMERIC(10,2) | DEFAULT 0 | Total cost |
| is_warranty | BOOLEAN | DEFAULT FALSE | Warranty work |
| warranty_claim_number | VARCHAR(100) | NULL | Warranty claim # |
| invoice_number | VARCHAR(100) | NULL | Invoice number |
| invoice_url | VARCHAR(500) | NULL | Invoice URL |
| photos_urls | TEXT | NULL | Photo URLs (JSON) |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**MaintenanceType Enum (UPPERCASE):** `SCHEDULED`, `PREVENTIVE`, `CORRECTIVE`, `EMERGENCY`, `INSPECTION`, `RECALL`, `OTHER`
**MaintenanceStatus Enum (UPPERCASE):** `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `ON_HOLD`, `WAITING_PARTS`
**ServiceProvider Enum (UPPERCASE):** `AUTHORIZED_DEALER`, `INDEPENDENT_SHOP`, `IN_HOUSE`, `OTHER`

---

### Table: vehicle_inspections

**Purpose:** Vehicle inspection checklists

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| vehicle_id | INTEGER | FK vehicles.id (CASCADE) | Vehicle |
| courier_id | INTEGER | FK couriers.id | Inspector |
| inspection_number | VARCHAR(50) | UNIQUE, NOT NULL | Reference number |
| inspection_type | ENUM | NOT NULL | InspectionType enum |
| status | ENUM | DEFAULT 'SCHEDULED' | InspectionStatus enum |
| scheduled_date | DATE | NOT NULL | Scheduled date |
| inspection_date | TIMESTAMP | NULL | Actual date |
| mileage_at_inspection | NUMERIC(10,2) | NULL | Mileage |
| overall_condition | ENUM | NULL | VehicleCondition enum |
| overall_score | INTEGER | NULL | Score (0-100) |
| exterior_condition/interior_condition/engine_condition/... | BOOLEAN | NULL | 37+ checklist items |
| issues_found | TEXT | NULL | Issues found |
| recommendations | TEXT | NULL | Recommendations |
| photos_urls | TEXT | NULL | Photo URLs (JSON) |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**InspectionType Enum (UPPERCASE):** `PRE_TRIP`, `POST_TRIP`, `WEEKLY`, `MONTHLY`, `INCIDENT`, `TRANSFER`, `OTHER`
**InspectionStatus Enum (UPPERCASE):** `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`
**VehicleCondition Enum (UPPERCASE):** `EXCELLENT`, `GOOD`, `FAIR`, `POOR`, `CRITICAL`

---

### Table: vehicle_logs

**Purpose:** Daily vehicle operation logs and trip records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| vehicle_id | INTEGER | FK vehicles.id (CASCADE) | Vehicle |
| courier_id | INTEGER | FK couriers.id | Driver |
| log_type | ENUM | DEFAULT 'DAILY_LOG' | LogType enum |
| log_date | DATE | NOT NULL | Log date |
| log_time | TIME | NULL | Log time |
| start_mileage | NUMERIC(10,2) | NULL | Starting mileage |
| end_mileage | NUMERIC(10,2) | NULL | Ending mileage |
| distance_covered | NUMERIC(10,2) | NULL | Distance covered |
| start_location | VARCHAR(300) | NULL | Start location |
| end_location | VARCHAR(300) | NULL | End location |
| route_description | TEXT | NULL | Route description |
| fuel_refilled | NUMERIC(8,2) | NULL | Fuel (liters) |
| fuel_cost | NUMERIC(10,2) | NULL | Fuel cost (SAR) |
| fuel_provider | ENUM | NULL | FuelProvider enum |
| fuel_station_location | VARCHAR(300) | NULL | Station location |
| fuel_receipt_number | VARCHAR(100) | NULL | Receipt number |
| number_of_deliveries | INTEGER | DEFAULT 0 | Deliveries count |
| number_of_orders | INTEGER | DEFAULT 0 | Orders count |
| revenue_generated | NUMERIC(10,2) | DEFAULT 0 | Revenue (SAR) |
| vehicle_condition | VARCHAR(50) | NULL | Condition |
| issues_reported | TEXT | NULL | Issues reported |
| has_issues | BOOLEAN | DEFAULT FALSE | Has issues flag |
| start_time | TIMESTAMP | NULL | Start time |
| end_time | TIMESTAMP | NULL | End time |
| working_hours | NUMERIC(5,2) | NULL | Working hours |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**LogType Enum (UPPERCASE):** `DAILY_LOG`, `FUEL_REFILL`, `TRIP`, `DELIVERY`
**FuelProvider Enum (UPPERCASE):** `ARAMCO`, `ADNOC`, `PETROL`, `OTHER`

---

### Table: fuel_logs

**Purpose:** Fuel consumption tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| vehicle_id | INTEGER | FK vehicles.id (CASCADE) | Vehicle |
| courier_id | INTEGER | FK couriers.id | Driver |
| fill_date | DATE | NOT NULL | Fill date |
| fill_time | TIME | NULL | Fill time |
| fuel_type | ENUM | NOT NULL | FuelType enum |
| quantity_liters | NUMERIC(8,2) | NOT NULL | Quantity (liters) |
| price_per_liter | NUMERIC(6,2) | NOT NULL | Price per liter |
| total_cost | NUMERIC(10,2) | NOT NULL | Total cost |
| mileage_at_fill | NUMERIC(10,2) | NULL | Mileage at fill |
| station_name | VARCHAR(200) | NULL | Station name |
| station_location | VARCHAR(300) | NULL | Station location |
| receipt_number | VARCHAR(100) | NULL | Receipt number |
| receipt_image_url | VARCHAR(500) | NULL | Receipt image URL |
| payment_method | VARCHAR(50) | NULL | Payment method |
| is_full_tank | BOOLEAN | DEFAULT TRUE | Full tank flag |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: accident_logs

**Purpose:** Comprehensive accident/incident tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| vehicle_id | INTEGER | FK vehicles.id | Vehicle |
| courier_id | INTEGER | FK couriers.id | Driver |
| accident_number | VARCHAR(50) | UNIQUE, NOT NULL | Reference number |
| accident_type | ENUM | NOT NULL | AccidentType enum |
| severity | ENUM | DEFAULT 'MINOR' | AccidentSeverity enum |
| status | ENUM | DEFAULT 'REPORTED' | AccidentStatus enum |
| fault_status | ENUM | DEFAULT 'UNDER_INVESTIGATION' | FaultStatus enum |
| accident_date | DATE | NOT NULL | Accident date |
| accident_time | TIME | NULL | Accident time |
| location | VARCHAR(500) | NULL | Location |
| city | VARCHAR(100) | NULL | City |
| latitude | NUMERIC(11,8) | NULL | Latitude |
| longitude | NUMERIC(11,8) | NULL | Longitude |
| description | TEXT | NULL | Description |
| weather_conditions | VARCHAR(100) | NULL | Weather |
| road_conditions | VARCHAR(100) | NULL | Road conditions |
| third_party_involved | BOOLEAN | DEFAULT FALSE | Third party flag |
| third_party_details | TEXT | NULL | Third party info |
| injuries | BOOLEAN | DEFAULT FALSE | Injuries flag |
| injuries_description | TEXT | NULL | Injury details |
| police_report_number | VARCHAR(100) | NULL | Police report # |
| police_report_url | VARCHAR(500) | NULL | Police report URL |
| insurance_claim_number | VARCHAR(100) | NULL | Insurance claim # |
| insurance_claim_status | VARCHAR(50) | NULL | Claim status |
| estimated_repair_cost | NUMERIC(12,2) | NULL | Estimated cost |
| actual_repair_cost | NUMERIC(12,2) | NULL | Actual cost |
| repair_completion_date | DATE | NULL | Repair completion |
| days_out_of_service | INTEGER | NULL | Days out of service |
| photos_urls | TEXT | NULL | Photo URLs (JSON) |
| documents_urls | TEXT | NULL | Document URLs (JSON) |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**AccidentType Enum (UPPERCASE):** `COLLISION`, `ROLLOVER`, `HIT_AND_RUN`, `PEDESTRIAN`, `PROPERTY_DAMAGE`, `MECHANICAL_FAILURE`, `THEFT`, `VANDALISM`, `OTHER`
**AccidentSeverity Enum (UPPERCASE):** `MINOR`, `MODERATE`, `MAJOR`, `TOTAL_LOSS`
**AccidentStatus Enum (UPPERCASE):** `REPORTED`, `UNDER_INVESTIGATION`, `INSURANCE_PENDING`, `REPAIR_IN_PROGRESS`, `RESOLVED`, `CLOSED`
**FaultStatus Enum (UPPERCASE):** `OUR_FAULT`, `OTHER_PARTY_FAULT`, `SHARED_FAULT`, `NO_FAULT`, `UNDER_INVESTIGATION`

---

### Table: documents (Fleet)

**Purpose:** Document management for couriers and vehicles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| document_type | ENUM | NOT NULL | DocumentType enum |
| entity_type | ENUM | NOT NULL | DocumentEntity enum |
| entity_id | INTEGER | NOT NULL | Entity ID |
| document_name | VARCHAR(200) | NOT NULL | Document name |
| document_number | VARCHAR(100) | NULL | Document number |
| issue_date | DATE | NULL | Issue date |
| expiry_date | DATE | NULL | Expiry date |
| issuing_authority | VARCHAR(200) | NULL | Issuing authority |
| file_url | VARCHAR(500) | NULL | File URL |
| file_name | VARCHAR(255) | NULL | File name |
| file_type | VARCHAR(100) | NULL | MIME type |
| file_size | BIGINT | NULL | File size (bytes) |
| status | VARCHAR(50) | DEFAULT 'ACTIVE' | Status |
| is_verified | BOOLEAN | DEFAULT FALSE | Verified flag |
| verified_by | INTEGER | FK users.id | Verifier |
| verified_at | TIMESTAMP | NULL | Verification time |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**DocumentType Enum (UPPERCASE):** `NATIONAL_ID`, `IQAMA`, `LICENSE`, `PASSPORT`, `VEHICLE_REGISTRATION`, `INSURANCE`, `CONTRACT`, `CERTIFICATE`, `OTHER`
**DocumentEntity Enum (UPPERCASE):** `COURIER`, `VEHICLE`

---

## HR & Finance Module

### Table: attendance

**Purpose:** Daily courier attendance tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id (CASCADE) | Courier |
| date | DATE | NOT NULL | Attendance date |
| status | ENUM | NOT NULL | AttendanceStatus enum |
| check_in_time | TIME | NULL | Check-in time |
| check_out_time | TIME | NULL | Check-out time |
| check_in_location | VARCHAR(300) | NULL | Check-in location |
| check_out_location | VARCHAR(300) | NULL | Check-out location |
| hours_worked | NUMERIC(5,2) | NULL | Hours worked |
| overtime_hours | NUMERIC(5,2) | DEFAULT 0 | Overtime hours |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**AttendanceStatus Enum (UPPERCASE):** `PRESENT`, `ABSENT`, `LATE`, `LEAVE`, `HOLIDAY`, `HALF_DAY`

**Constraints:** UNIQUE (courier_id, date)

---

### Table: salaries

**Purpose:** Monthly salary/payroll records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id (CASCADE) | Courier |
| month | INTEGER | NOT NULL | Month (1-12) |
| year | INTEGER | NOT NULL | Year |
| base_salary | NUMERIC(10,2) | NOT NULL | Base salary |
| housing_allowance | NUMERIC(10,2) | DEFAULT 0 | Housing allowance |
| transportation_allowance | NUMERIC(10,2) | DEFAULT 0 | Transport allowance |
| other_allowances | NUMERIC(10,2) | DEFAULT 0 | Other allowances |
| bonuses | NUMERIC(10,2) | DEFAULT 0 | Bonuses |
| overtime_pay | NUMERIC(10,2) | DEFAULT 0 | Overtime pay |
| deductions | NUMERIC(10,2) | DEFAULT 0 | Deductions |
| loan_deduction | NUMERIC(10,2) | DEFAULT 0 | Loan deduction |
| gosi_employee | NUMERIC(10,2) | DEFAULT 0 | GOSI (employee) |
| gosi_company | NUMERIC(10,2) | DEFAULT 0 | GOSI (company) |
| gross_salary | NUMERIC(10,2) | NOT NULL | Gross salary |
| net_salary | NUMERIC(10,2) | NOT NULL | Net salary |
| payment_date | DATE | NULL | Payment date |
| payment_method | VARCHAR(50) | NULL | Payment method |
| payment_reference | VARCHAR(100) | NULL | Payment reference |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**Constraints:** UNIQUE (courier_id, month, year)

---

### Table: loans

**Purpose:** Courier loan management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id (CASCADE) | Courier |
| loan_number | VARCHAR(50) | UNIQUE, NOT NULL | Loan reference |
| amount | NUMERIC(10,2) | NOT NULL | Total loan amount |
| outstanding_balance | NUMERIC(10,2) | NOT NULL | Remaining balance |
| monthly_deduction | NUMERIC(10,2) | NOT NULL | Monthly deduction |
| total_installments | INTEGER | NOT NULL | Total installments |
| paid_installments | INTEGER | DEFAULT 0 | Paid installments |
| start_date | DATE | NOT NULL | Start date |
| end_date | DATE | NULL | End date |
| status | ENUM | DEFAULT 'ACTIVE' | LoanStatus enum |
| reason | TEXT | NULL | Loan reason |
| approved_by | INTEGER | FK users.id | Approver |
| approved_at | TIMESTAMP | NULL | Approval time |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**LoanStatus Enum (lowercase):** `active`, `completed`, `cancelled`

---

### Table: leaves

**Purpose:** Leave request management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id (CASCADE) | Courier |
| leave_type | ENUM | NOT NULL | LeaveType enum |
| start_date | DATE | NOT NULL | Leave start |
| end_date | DATE | NOT NULL | Leave end |
| days | INTEGER | NOT NULL | Total days |
| reason | TEXT | NULL | Leave reason |
| status | ENUM | DEFAULT 'PENDING' | LeaveStatus enum |
| approved_by | INTEGER | FK users.id | Approver |
| approved_at | TIMESTAMP | NULL | Approval time |
| rejection_reason | TEXT | NULL | Rejection reason |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**LeaveType Enum (lowercase):** `annual`, `sick`, `emergency`, `unpaid`
**LeaveStatus Enum (lowercase):** `pending`, `approved`, `rejected`, `cancelled`

---

### Table: assets

**Purpose:** Company asset assignment to couriers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id | Assignee |
| asset_number | VARCHAR(50) | UNIQUE, NOT NULL | Asset number |
| asset_type | ENUM | NOT NULL | AssetType enum |
| asset_name | VARCHAR(200) | NOT NULL | Asset name |
| make | VARCHAR(100) | NULL | Make/brand |
| model | VARCHAR(100) | NULL | Model |
| serial_number | VARCHAR(100) | NULL | Serial/IMEI |
| purchase_date | DATE | NULL | Purchase date |
| purchase_price | NUMERIC(10,2) | NULL | Purchase price |
| status | ENUM | DEFAULT 'AVAILABLE' | AssetStatus enum |
| condition | VARCHAR(50) | NULL | Condition |
| assigned_date | DATE | NULL | Assignment date |
| return_date | DATE | NULL | Return date |
| warranty_expiry_date | DATE | NULL | Warranty expiry |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**AssetType Enum (UPPERCASE):** `PHONE`, `TABLET`, `UNIFORM`, `BAG`, `HELMET`, `POWER_BANK`, `SIM_CARD`, `OTHER`
**AssetStatus Enum (UPPERCASE):** `AVAILABLE`, `ASSIGNED`, `MAINTENANCE`, `DAMAGED`, `RETIRED`, `LOST`

---

### Table: bonuses

**Purpose:** Bonus and incentive tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id (CASCADE) | Courier |
| bonus_type | ENUM | NOT NULL | BonusType enum |
| amount | NUMERIC(10,2) | NOT NULL | Bonus amount |
| bonus_date | DATE | NOT NULL | Bonus date |
| reason | TEXT | NULL | Reason |
| payment_status | ENUM | DEFAULT 'PENDING' | PaymentStatus enum |
| paid_at | TIMESTAMP | NULL | Payment time |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**BonusType Enum (UPPERCASE):** `PERFORMANCE`, `REFERRAL`, `ATTENDANCE`, `SAFETY`, `HOLIDAY`, `SPECIAL`, `OTHER`
**PaymentStatus Enum (UPPERCASE):** `PENDING`, `APPROVED`, `PAID`, `CANCELLED`

---

## Operations Module

### Table: deliveries

**Purpose:** Delivery task management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| tracking_number | VARCHAR(50) | UNIQUE, NOT NULL | Tracking number |
| courier_id | INTEGER | FK couriers.id | Assigned courier |
| zone_id | INTEGER | FK zones.id | Delivery zone |
| route_id | INTEGER | FK routes.id | Route |
| status | ENUM | DEFAULT 'PENDING' | DeliveryStatus enum |
| service_level | VARCHAR(50) | DEFAULT 'STANDARD' | Service level |
| priority | VARCHAR(20) | DEFAULT 'NORMAL' | Priority |
| customer_name | VARCHAR(200) | NOT NULL | Customer name |
| customer_phone | VARCHAR(20) | NOT NULL | Customer phone |
| pickup_address | TEXT | NULL | Pickup address |
| pickup_latitude | NUMERIC(11,8) | NULL | Pickup lat |
| pickup_longitude | NUMERIC(11,8) | NULL | Pickup lng |
| delivery_address | TEXT | NOT NULL | Delivery address |
| delivery_latitude | NUMERIC(11,8) | NULL | Delivery lat |
| delivery_longitude | NUMERIC(11,8) | NULL | Delivery lng |
| scheduled_pickup_time | TIMESTAMP | NULL | Scheduled pickup |
| scheduled_delivery_time | TIMESTAMP | NULL | Scheduled delivery |
| actual_pickup_time | TIMESTAMP | NULL | Actual pickup |
| actual_delivery_time | TIMESTAMP | NULL | Actual delivery |
| cod_amount | NUMERIC(10,2) | DEFAULT 0 | COD amount |
| is_cod | BOOLEAN | DEFAULT FALSE | Is COD flag |
| delivery_fee | NUMERIC(10,2) | DEFAULT 0 | Delivery fee |
| distance_km | NUMERIC(10,2) | NULL | Distance (km) |
| estimated_time_minutes | INTEGER | NULL | Estimated time |
| package_weight | NUMERIC(8,2) | NULL | Weight (kg) |
| package_dimensions | VARCHAR(50) | NULL | Dimensions |
| recipient_signature_url | VARCHAR(500) | NULL | Signature URL |
| delivery_photo_url | VARCHAR(500) | NULL | Photo URL |
| failure_reason | TEXT | NULL | Failure reason |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**DeliveryStatus Enum (UPPERCASE):** `PENDING`, `ASSIGNED`, `ACCEPTED`, `PICKUP_STARTED`, `PICKED_UP`, `IN_TRANSIT`, `ARRIVED`, `DELIVERED`, `FAILED`, `CANCELLED`, `RETURNED`

---

### Table: zones

**Purpose:** Geographic zone management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| zone_code | VARCHAR(50) | UNIQUE, NOT NULL | Zone code |
| name | VARCHAR(200) | NOT NULL | Zone name |
| city | VARCHAR(100) | NOT NULL | City |
| description | TEXT | NULL | Description |
| status | ENUM | DEFAULT 'ACTIVE' | ZoneStatus enum |
| boundaries | JSONB | NULL | GeoJSON boundaries |
| center_latitude | NUMERIC(11,8) | NULL | Center lat |
| center_longitude | NUMERIC(11,8) | NULL | Center lng |
| radius_km | NUMERIC(10,2) | NULL | Radius |
| base_delivery_fee | NUMERIC(10,2) | DEFAULT 0 | Base fee |
| priority_multiplier | NUMERIC(4,2) | DEFAULT 1 | Priority multiplier |
| max_couriers | INTEGER | NULL | Max couriers |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**ZoneStatus Enum (UPPERCASE):** `ACTIVE`, `INACTIVE`, `SUSPENDED`

---

### Table: routes

**Purpose:** Delivery route management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| route_code | VARCHAR(50) | UNIQUE, NOT NULL | Route code |
| name | VARCHAR(200) | NOT NULL | Route name |
| description | TEXT | NULL | Description |
| status | ENUM | DEFAULT 'ACTIVE' | RouteStatus enum |
| zone_id | INTEGER | FK zones.id | Zone |
| start_location | VARCHAR(300) | NULL | Start location |
| end_location | VARCHAR(300) | NULL | End location |
| waypoints | JSONB | NULL | Waypoints (JSON) |
| estimated_distance_km | NUMERIC(10,2) | NULL | Distance |
| estimated_duration_minutes | INTEGER | NULL | Duration |
| optimal_vehicle_type | VARCHAR(50) | NULL | Vehicle type |
| max_stops | INTEGER | NULL | Max stops |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**RouteStatus Enum (UPPERCASE):** `ACTIVE`, `INACTIVE`, `OPTIMIZING`

---

### Table: dispatch_assignments

**Purpose:** Delivery-courier dispatch assignments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| assignment_number | VARCHAR(50) | UNIQUE, NOT NULL | Assignment number |
| delivery_id | INTEGER | FK deliveries.id (CASCADE) | Delivery |
| courier_id | INTEGER | FK couriers.id | Assigned courier |
| zone_id | INTEGER | FK zones.id | Zone |
| status | ENUM | DEFAULT 'PENDING' | DispatchStatus enum |
| priority | ENUM | DEFAULT 'NORMAL' | DispatchPriority enum |
| assignment_algorithm | VARCHAR(50) | DEFAULT 'MANUAL' | Algorithm used |
| distance_to_pickup_km | NUMERIC(10,2) | NULL | Distance to pickup |
| estimated_time_minutes | INTEGER | NULL | Estimated time |
| courier_current_load | INTEGER | DEFAULT 0 | Current load |
| courier_max_capacity | INTEGER | DEFAULT 10 | Max capacity |
| courier_rating | NUMERIC(3,2) | NULL | Courier rating |
| assigned_at | TIMESTAMP | NULL | Assignment time |
| accepted_at | TIMESTAMP | NULL | Acceptance time |
| started_at | TIMESTAMP | NULL | Start time |
| completed_at | TIMESTAMP | NULL | Completion time |
| rejection_reason | TEXT | NULL | Rejection reason |
| rejected_at | TIMESTAMP | NULL | Rejection time |
| rejection_count | INTEGER | DEFAULT 0 | Rejection count |
| is_reassignment | BOOLEAN | DEFAULT FALSE | Is reassignment |
| previous_courier_id | INTEGER | FK couriers.id | Previous courier |
| reassignment_reason | TEXT | NULL | Reassignment reason |
| assigned_by_id | INTEGER | FK users.id | Assigned by |
| assignment_notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**DispatchStatus Enum (UPPERCASE):** `PENDING`, `ASSIGNED`, `ACCEPTED`, `REJECTED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`
**DispatchPriority Enum (UPPERCASE):** `URGENT`, `HIGH`, `NORMAL`, `LOW`

---

### Table: priority_queue_entries

**Purpose:** Priority queue for delivery scheduling

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| queue_number | VARCHAR(50) | UNIQUE, NOT NULL | Queue number |
| delivery_id | INTEGER | FK deliveries.id (CASCADE) | Delivery (unique) |
| priority | ENUM | NOT NULL | QueuePriority enum |
| status | ENUM | DEFAULT 'QUEUED' | QueueStatus enum |
| base_priority_score | INTEGER | NOT NULL | Base score (1-100) |
| time_factor_score | INTEGER | DEFAULT 0 | Time urgency score |
| customer_tier_score | INTEGER | DEFAULT 0 | Customer tier score |
| sla_factor_score | INTEGER | DEFAULT 0 | SLA score |
| total_priority_score | INTEGER | NOT NULL | Composite score |
| sla_deadline | TIMESTAMP | NOT NULL | SLA deadline |
| sla_buffer_minutes | INTEGER | DEFAULT 30 | Buffer time |
| warning_threshold | TIMESTAMP | NULL | Warning time |
| customer_tier | VARCHAR(20) | NULL | Customer tier |
| is_vip_customer | BOOLEAN | DEFAULT FALSE | VIP flag |
| queue_position | INTEGER | NULL | Position in queue |
| estimated_wait_time_minutes | INTEGER | NULL | Est. wait time |
| required_zone_id | INTEGER | FK zones.id | Required zone |
| required_vehicle_type | VARCHAR(50) | NULL | Required vehicle |
| preferred_courier_id | INTEGER | FK couriers.id | Preferred courier |
| excluded_courier_ids | TEXT | NULL | Excluded couriers |
| min_courier_rating | NUMERIC(3,2) | NULL | Min rating |
| max_assignment_attempts | INTEGER | DEFAULT 3 | Max attempts |
| assignment_attempts | INTEGER | DEFAULT 0 | Attempt count |
| is_escalated | BOOLEAN | DEFAULT FALSE | Escalated flag |
| escalated_at | TIMESTAMP | NULL | Escalation time |
| escalation_reason | TEXT | NULL | Escalation reason |
| queued_at | TIMESTAMP | NOT NULL | Queued time |
| assigned_at | TIMESTAMP | NULL | Assignment time |
| completed_at | TIMESTAMP | NULL | Completion time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**QueuePriority Enum (UPPERCASE):** `CRITICAL`, `URGENT`, `HIGH`, `NORMAL`, `LOW`
**QueueStatus Enum (UPPERCASE):** `QUEUED`, `PROCESSING`, `ASSIGNED`, `COMPLETED`, `EXPIRED`, `CANCELLED`

---

### Table: sla_definitions

**Purpose:** SLA target definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(200) | NOT NULL | SLA name |
| sla_code | VARCHAR(50) | UNIQUE, NOT NULL | SLA code |
| description | TEXT | NULL | Description |
| sla_type | ENUM | NOT NULL | SLAType enum |
| priority | ENUM | DEFAULT 'MEDIUM' | SLAPriority enum |
| target_time_minutes | INTEGER | NOT NULL | Target time |
| warning_threshold_minutes | INTEGER | NULL | Warning threshold |
| critical_threshold_minutes | INTEGER | NULL | Critical threshold |
| applies_to_zone_ids | TEXT | NULL | Applicable zones |
| applies_to_service_levels | TEXT | NULL | Applicable levels |
| is_active | BOOLEAN | DEFAULT TRUE | Active flag |
| business_hours_only | BOOLEAN | DEFAULT FALSE | Business hours only |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**SLAType Enum (UPPERCASE):** `PICKUP`, `DELIVERY`, `RESPONSE`, `RESOLUTION`, `FIRST_CONTACT`
**SLAPriority Enum (UPPERCASE):** `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`

---

### Table: sla_tracking

**Purpose:** SLA compliance monitoring

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| sla_definition_id | INTEGER | FK sla_definitions.id | SLA definition |
| delivery_id | INTEGER | FK deliveries.id | Delivery |
| status | ENUM | DEFAULT 'ON_TRACK' | SLAStatus enum |
| started_at | TIMESTAMP | NOT NULL | Start time |
| target_time | TIMESTAMP | NOT NULL | Target time |
| warning_time | TIMESTAMP | NULL | Warning time |
| critical_time | TIMESTAMP | NULL | Critical time |
| completed_at | TIMESTAMP | NULL | Completion time |
| actual_time_minutes | INTEGER | NULL | Actual time |
| variance_minutes | INTEGER | NULL | Variance |
| was_sla_met | BOOLEAN | NULL | SLA met flag |
| breach_reason | TEXT | NULL | Breach reason |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**SLAStatus Enum (UPPERCASE):** `ON_TRACK`, `AT_RISK`, `WARNING`, `BREACHED`, `MET`, `CANCELLED`

---

### Table: cod_entries

**Purpose:** Cash on delivery tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| cod_number | VARCHAR(50) | UNIQUE, NOT NULL | COD number |
| delivery_id | INTEGER | FK deliveries.id | Delivery |
| courier_id | INTEGER | FK couriers.id | Collector |
| amount | NUMERIC(10,2) | NOT NULL | COD amount |
| collected_amount | NUMERIC(10,2) | DEFAULT 0 | Collected |
| status | ENUM | DEFAULT 'PENDING' | CODStatus enum |
| collection_date | DATE | NULL | Collection date |
| remittance_date | DATE | NULL | Remittance date |
| remitted_to | VARCHAR(200) | NULL | Remitted to |
| receipt_number | VARCHAR(100) | NULL | Receipt number |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**CODStatus Enum (UPPERCASE):** `PENDING`, `COLLECTED`, `REMITTED`, `PARTIALLY_COLLECTED`, `FAILED`, `CANCELLED`

---

### Table: incidents

**Purpose:** Operational incident reporting

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| incident_number | VARCHAR(50) | UNIQUE, NOT NULL | Incident number |
| incident_type | ENUM | NOT NULL | IncidentType enum |
| status | ENUM | DEFAULT 'REPORTED' | IncidentStatus enum |
| severity | VARCHAR(20) | DEFAULT 'MEDIUM' | Severity |
| courier_id | INTEGER | FK couriers.id | Involved courier |
| delivery_id | INTEGER | FK deliveries.id | Related delivery |
| vehicle_id | INTEGER | FK vehicles.id | Related vehicle |
| incident_date | DATE | NOT NULL | Incident date |
| incident_time | TIME | NULL | Incident time |
| location | VARCHAR(500) | NULL | Location |
| description | TEXT | NOT NULL | Description |
| root_cause | TEXT | NULL | Root cause |
| resolution | TEXT | NULL | Resolution |
| resolved_at | TIMESTAMP | NULL | Resolution time |
| resolved_by | INTEGER | FK users.id | Resolver |
| escalated_to | INTEGER | FK users.id | Escalated to |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**IncidentType Enum (UPPERCASE):** `DELIVERY_DELAY`, `PACKAGE_DAMAGE`, `CUSTOMER_COMPLAINT`, `COURIER_MISCONDUCT`, `VEHICLE_BREAKDOWN`, `TRAFFIC_ACCIDENT`, `THEFT`, `LOST_PACKAGE`, `WRONG_DELIVERY`, `SYSTEM_ERROR`, `OTHER`
**IncidentStatus Enum (UPPERCASE):** `REPORTED`, `INVESTIGATING`, `ESCALATED`, `RESOLVED`, `CLOSED`

---

### Table: customer_feedbacks

**Purpose:** Customer feedback for deliveries

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| delivery_id | INTEGER | FK deliveries.id | Delivery |
| courier_id | INTEGER | FK couriers.id | Courier |
| feedback_type | ENUM | NOT NULL | FeedbackType enum |
| rating | INTEGER | NULL | Rating (1-5) |
| sentiment | ENUM | NULL | FeedbackSentiment enum |
| status | ENUM | DEFAULT 'NEW' | FeedbackStatus enum |
| customer_name | VARCHAR(200) | NULL | Customer name |
| customer_phone | VARCHAR(20) | NULL | Customer phone |
| feedback_text | TEXT | NULL | Feedback text |
| categories | TEXT | NULL | Categories (JSON) |
| response_text | TEXT | NULL | Response |
| responded_by | INTEGER | FK users.id | Responder |
| responded_at | TIMESTAMP | NULL | Response time |
| is_public | BOOLEAN | DEFAULT FALSE | Public flag |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**FeedbackType Enum (UPPERCASE):** `DELIVERY`, `COURIER`, `SERVICE`, `APP`, `OTHER`
**FeedbackSentiment Enum (UPPERCASE):** `POSITIVE`, `NEUTRAL`, `NEGATIVE`
**FeedbackStatus Enum (UPPERCASE):** `NEW`, `REVIEWED`, `RESPONDED`, `RESOLVED`, `ARCHIVED`

---

### Table: handovers

**Purpose:** Package/COD handover tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| handover_number | VARCHAR(50) | UNIQUE, NOT NULL | Handover number |
| handover_type | ENUM | NOT NULL | HandoverType enum |
| status | ENUM | DEFAULT 'PENDING' | HandoverStatus enum |
| from_courier_id | INTEGER | FK couriers.id | From courier |
| to_courier_id | INTEGER | FK couriers.id | To courier |
| to_hub_name | VARCHAR(200) | NULL | Hub name |
| delivery_ids | TEXT | NULL | Delivery IDs (JSON) |
| total_packages | INTEGER | DEFAULT 0 | Package count |
| total_cod_amount | NUMERIC(12,2) | DEFAULT 0 | COD total |
| collected_cod_amount | NUMERIC(12,2) | DEFAULT 0 | COD collected |
| scheduled_time | TIMESTAMP | NULL | Scheduled time |
| completed_time | TIMESTAMP | NULL | Completed time |
| verified_by | INTEGER | FK users.id | Verifier |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**HandoverType Enum (UPPERCASE):** `COURIER_TO_COURIER`, `COURIER_TO_HUB`, `HUB_TO_COURIER`, `SHIFT_CHANGE`
**HandoverStatus Enum (UPPERCASE):** `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`, `DISPUTED`

---

### Table: quality_metrics

**Purpose:** Quality measurement definitions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| metric_code | VARCHAR(50) | UNIQUE, NOT NULL | Metric code |
| name | VARCHAR(200) | NOT NULL | Metric name |
| description | TEXT | NULL | Description |
| metric_type | ENUM | NOT NULL | QualityMetricType enum |
| target_value | NUMERIC(10,2) | NULL | Target value |
| warning_threshold | NUMERIC(10,2) | NULL | Warning threshold |
| critical_threshold | NUMERIC(10,2) | NULL | Critical threshold |
| unit | VARCHAR(50) | NULL | Unit of measure |
| is_active | BOOLEAN | DEFAULT TRUE | Active flag |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**QualityMetricType Enum (UPPERCASE):** `ON_TIME_DELIVERY`, `CUSTOMER_RATING`, `DAMAGE_RATE`, `RETURN_RATE`, `COMPLETION_RATE`, `RESPONSE_TIME`, `CUSTOM`

---

### Table: quality_inspections

**Purpose:** Quality inspection records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| inspection_number | VARCHAR(50) | UNIQUE, NOT NULL | Inspection number |
| courier_id | INTEGER | FK couriers.id | Inspected courier |
| inspector_id | INTEGER | FK users.id | Inspector |
| status | ENUM | DEFAULT 'SCHEDULED' | InspectionStatus enum |
| inspection_date | DATE | NOT NULL | Inspection date |
| overall_score | INTEGER | NULL | Overall score (0-100) |
| checklist_results | JSONB | NULL | Checklist (JSON) |
| issues_found | TEXT | NULL | Issues found |
| recommendations | TEXT | NULL | Recommendations |
| follow_up_required | BOOLEAN | DEFAULT FALSE | Follow-up flag |
| follow_up_date | DATE | NULL | Follow-up date |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: operations_settings

**Purpose:** Operations configuration settings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| auto_dispatch_enabled | BOOLEAN | DEFAULT FALSE | Auto-dispatch |
| auto_dispatch_algorithm | VARCHAR(50) | NULL | Algorithm |
| max_concurrent_deliveries | INTEGER | DEFAULT 10 | Max concurrent |
| default_delivery_radius_km | NUMERIC(10,2) | DEFAULT 10 | Radius |
| working_hours_start | TIME | NULL | Work start |
| working_hours_end | TIME | NULL | Work end |
| business_days | TEXT | NULL | Business days (JSON) |
| settings_json | JSONB | NULL | Additional settings |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: operations_documents

**Purpose:** Operations SOPs and documents

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| document_code | VARCHAR(50) | UNIQUE, NOT NULL | Document code |
| title | VARCHAR(300) | NOT NULL | Title |
| category | ENUM | NOT NULL | DocumentCategory enum |
| description | TEXT | NULL | Description |
| content | TEXT | NULL | Content (Markdown) |
| file_url | VARCHAR(500) | NULL | File URL |
| version | VARCHAR(20) | DEFAULT '1.0' | Version |
| status | VARCHAR(50) | DEFAULT 'DRAFT' | Status |
| effective_date | DATE | NULL | Effective date |
| expiry_date | DATE | NULL | Expiry date |
| created_by | INTEGER | FK users.id | Author |
| approved_by | INTEGER | FK users.id | Approver |
| approved_at | TIMESTAMP | NULL | Approval time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**DocumentCategory Enum (UPPERCASE):** `SOP`, `POLICY`, `TRAINING`, `SAFETY`, `COMPLIANCE`, `GUIDE`, `OTHER`

---

## Accommodation Module

### Table: buildings

**Purpose:** Property/building management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(200) | NOT NULL | Building name |
| address | TEXT | NOT NULL | Full address |
| city | VARCHAR(100) | NULL | City |
| district | VARCHAR(100) | NULL | District |
| total_rooms | INTEGER | DEFAULT 0 | Total rooms |
| total_beds | INTEGER | DEFAULT 0 | Total beds |
| total_capacity | INTEGER | DEFAULT 0 | Total capacity |
| current_occupancy | INTEGER | DEFAULT 0 | Current occupancy |
| monthly_rent | NUMERIC(10,2) | NULL | Monthly rent |
| contract_start_date | DATE | NULL | Contract start |
| contract_end_date | DATE | NULL | Contract end |
| landlord_name | VARCHAR(200) | NULL | Landlord name |
| landlord_phone | VARCHAR(20) | NULL | Landlord phone |
| supervisor_name | VARCHAR(200) | NULL | Supervisor name |
| supervisor_phone | VARCHAR(20) | NULL | Supervisor phone |
| facilities | TEXT | NULL | Facilities (JSON) |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: rooms

**Purpose:** Individual room management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| building_id | INTEGER | FK buildings.id (CASCADE) | Building |
| room_number | VARCHAR(20) | NOT NULL | Room number |
| floor | INTEGER | NULL | Floor number |
| room_type | VARCHAR(50) | NULL | Room type |
| capacity | INTEGER | NOT NULL | Max occupants |
| current_occupancy | INTEGER | DEFAULT 0 | Current count |
| status | ENUM | DEFAULT 'AVAILABLE' | RoomStatus enum |
| amenities | TEXT | NULL | Amenities (JSON) |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**RoomStatus Enum (lowercase):** `available`, `occupied`, `maintenance`

**Constraints:** UNIQUE (building_id, room_number)

---

### Table: beds

**Purpose:** Individual bed management within rooms

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| room_id | INTEGER | FK rooms.id (CASCADE) | Room |
| bed_number | VARCHAR(20) | NOT NULL | Bed number |
| bed_type | VARCHAR(50) | NULL | Bed type |
| status | ENUM | DEFAULT 'AVAILABLE' | BedStatus enum |
| assigned_courier_id | INTEGER | FK couriers.id | Assigned courier |
| assigned_date | DATE | NULL | Assignment date |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**BedStatus Enum (UPPERCASE):** `AVAILABLE`, `OCCUPIED`, `RESERVED`, `MAINTENANCE`

**Constraints:** UNIQUE (room_id, bed_number)

---

### Table: allocations

**Purpose:** Courier accommodation allocation history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id (CASCADE) | Courier |
| building_id | INTEGER | FK buildings.id | Building |
| room_id | INTEGER | FK rooms.id | Room |
| bed_id | INTEGER | FK beds.id | Bed |
| start_date | DATE | NOT NULL | Allocation start |
| end_date | DATE | NULL | Allocation end |
| allocation_reason | TEXT | NULL | Reason |
| termination_reason | TEXT | NULL | Termination reason |
| monthly_deduction | NUMERIC(10,2) | DEFAULT 0 | Monthly deduction |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

## Support Module

### Table: tickets

**Purpose:** Support ticket management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| ticket_number | VARCHAR(50) | UNIQUE, NOT NULL | Ticket number |
| subject | VARCHAR(255) | NOT NULL | Subject |
| description | TEXT | NOT NULL | Description |
| category | ENUM | NOT NULL | TicketCategory enum |
| priority | ENUM | DEFAULT 'MEDIUM' | TicketPriority enum |
| status | ENUM | DEFAULT 'OPEN' | TicketStatus enum |
| escalation_level | ENUM | DEFAULT 'L1' | EscalationLevel enum |
| created_by | INTEGER | FK users.id | Creator |
| assigned_to | INTEGER | FK users.id | Assignee |
| department | VARCHAR(100) | NULL | Department |
| related_courier_id | INTEGER | FK couriers.id | Related courier |
| related_delivery_id | INTEGER | FK deliveries.id | Related delivery |
| related_vehicle_id | INTEGER | FK vehicles.id | Related vehicle |
| sla_deadline | TIMESTAMP | NULL | SLA deadline |
| sla_status | VARCHAR(50) | NULL | SLA status |
| first_response_at | TIMESTAMP | NULL | First response |
| resolved_at | TIMESTAMP | NULL | Resolution time |
| resolution | TEXT | NULL | Resolution |
| satisfaction_rating | INTEGER | NULL | Rating (1-5) |
| merged_into_id | INTEGER | FK tickets.id | Merged into |
| tags | TEXT | NULL | Tags (JSON) |
| custom_fields | JSONB | NULL | Custom fields |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**TicketCategory Enum (lowercase):** `technical`, `billing`, `delivery`, `courier`, `vehicle`, `hr`, `general`, `complaint`, `feature_request`
**TicketPriority Enum (lowercase):** `low`, `medium`, `high`, `critical`
**TicketStatus Enum (lowercase):** `open`, `in_progress`, `pending`, `on_hold`, `resolved`, `closed`, `cancelled`
**EscalationLevel Enum:** `L1`, `L2`, `L3`, `MANAGEMENT`

---

### Table: ticket_replies

**Purpose:** Ticket conversation threading

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| ticket_id | INTEGER | FK tickets.id (CASCADE) | Parent ticket |
| user_id | INTEGER | FK users.id | Reply author |
| message | TEXT | NOT NULL | Reply message |
| is_internal | BOOLEAN | DEFAULT FALSE | Internal note |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: ticket_attachments

**Purpose:** File attachments for tickets

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| ticket_id | INTEGER | FK tickets.id (CASCADE) | Ticket |
| reply_id | INTEGER | FK ticket_replies.id | Reply (optional) |
| uploaded_by | INTEGER | FK users.id | Uploader |
| filename | VARCHAR(255) | NOT NULL | Original filename |
| file_path | VARCHAR(500) | NOT NULL | Storage path |
| file_type | VARCHAR(100) | NOT NULL | MIME type |
| file_size | BIGINT | NOT NULL | Size (bytes) |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: ticket_templates

**Purpose:** Predefined ticket templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Template name |
| description | VARCHAR(500) | NULL | Description |
| default_subject | VARCHAR(255) | NULL | Default subject |
| default_description | TEXT | NULL | Default description |
| default_category | ENUM | NULL | Default category |
| default_priority | ENUM | DEFAULT 'MEDIUM' | Default priority |
| default_department | VARCHAR(100) | NULL | Default department |
| default_tags | TEXT | NULL | Default tags |
| default_custom_fields | JSONB | NULL | Custom fields |
| sla_hours | INTEGER | NULL | SLA hours |
| is_active | BOOLEAN | DEFAULT TRUE | Active flag |
| is_public | BOOLEAN | DEFAULT TRUE | Public flag |
| created_by | INTEGER | FK users.id | Creator |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: canned_responses

**Purpose:** Pre-written support responses

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| title | VARCHAR(100) | NOT NULL | Response title |
| shortcut | VARCHAR(50) | UNIQUE | Keyboard shortcut |
| content | TEXT | NOT NULL | Response content |
| category | VARCHAR(100) | NOT NULL | Category |
| is_active | BOOLEAN | DEFAULT TRUE | Active flag |
| is_public | BOOLEAN | DEFAULT TRUE | Public flag |
| usage_count | INTEGER | DEFAULT 0 | Usage count |
| created_by | INTEGER | FK users.id | Creator |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: chat_sessions

**Purpose:** Live chat conversations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| session_id | VARCHAR(50) | UNIQUE, NOT NULL | Session ID |
| customer_id | INTEGER | FK users.id (CASCADE) | Customer |
| agent_id | INTEGER | FK users.id | Support agent |
| status | ENUM | DEFAULT 'WAITING' | ChatStatus enum |
| initial_message | VARCHAR(500) | NULL | Initial message |
| started_at | TIMESTAMP | NULL | Chat start |
| ended_at | TIMESTAMP | NULL | Chat end |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**ChatStatus Enum (lowercase):** `waiting`, `active`, `ended`, `transferred`

---

### Table: chat_messages

**Purpose:** Chat message history

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| session_id | INTEGER | FK chat_sessions.id (CASCADE) | Session |
| sender_id | INTEGER | FK users.id | Sender |
| message | TEXT | NOT NULL | Message content |
| is_agent | BOOLEAN | DEFAULT FALSE | Agent message |
| is_system | BOOLEAN | DEFAULT FALSE | System message |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: faqs

**Purpose:** Frequently Asked Questions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| question | VARCHAR(500) | NOT NULL | FAQ question |
| answer | TEXT | NOT NULL | FAQ answer |
| category | VARCHAR(100) | NOT NULL | Category |
| order | INTEGER | DEFAULT 0 | Display order |
| is_active | BOOLEAN | DEFAULT TRUE | Active flag |
| view_count | INTEGER | DEFAULT 0 | View count |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: feedbacks (Support)

**Purpose:** General customer feedback

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| user_id | INTEGER | FK users.id | Submitter |
| subject | VARCHAR(255) | NOT NULL | Subject |
| message | TEXT | NOT NULL | Message |
| category | ENUM | NOT NULL | FeedbackCategory enum |
| rating | INTEGER | NULL | Rating (1-5) |
| status | ENUM | DEFAULT 'NEW' | FeedbackStatus enum |
| response | TEXT | NULL | Response |
| responded_by | INTEGER | FK users.id | Responder |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**FeedbackCategory Enum (lowercase):** `general`, `feature_request`, `bug_report`, `complaint`, `compliment`, `suggestion`
**FeedbackStatus Enum (lowercase):** `new`, `reviewed`, `in_progress`, `completed`, `dismissed`

---

### Table: kb_articles

**Purpose:** Knowledge base articles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| slug | VARCHAR(255) | UNIQUE, NOT NULL | URL slug |
| title | VARCHAR(255) | NOT NULL | Article title |
| content | TEXT | NOT NULL | Content (Markdown) |
| summary | VARCHAR(500) | NULL | Summary |
| category | VARCHAR(100) | NOT NULL | Category |
| tags | TEXT | NULL | Tags (comma-separated) |
| status | ENUM | DEFAULT 'DRAFT' | ArticleStatus enum |
| version | INTEGER | DEFAULT 1 | Version number |
| author_id | INTEGER | FK users.id | Author |
| view_count | INTEGER | DEFAULT 0 | View count |
| helpful_count | INTEGER | DEFAULT 0 | Helpful votes |
| not_helpful_count | INTEGER | DEFAULT 0 | Not helpful votes |
| meta_description | VARCHAR(255) | NULL | SEO description |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**ArticleStatus Enum (lowercase):** `draft`, `published`, `archived`

---

### Table: kb_categories

**Purpose:** Knowledge base category hierarchy

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(100) | NOT NULL | Category name |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | URL slug |
| description | TEXT | NULL | Description |
| parent_id | INTEGER | FK kb_categories.id | Parent category |
| icon | VARCHAR(50) | NULL | Icon name |
| order | INTEGER | DEFAULT 0 | Display order |
| is_active | BOOLEAN | DEFAULT TRUE | Active flag |
| is_public | BOOLEAN | DEFAULT TRUE | Public flag |
| article_count | INTEGER | DEFAULT 0 | Article count |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

## Analytics Module

### Table: dashboards

**Purpose:** Custom user dashboards

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| user_id | INTEGER | FK users.id (CASCADE) | Owner |
| name | VARCHAR(255) | NOT NULL | Dashboard name |
| description | TEXT | NULL | Description |
| widgets | JSONB | NOT NULL | Widget configs |
| layout | JSONB | NULL | Layout config |
| is_default | BOOLEAN | DEFAULT FALSE | Default flag |
| is_shared | BOOLEAN | DEFAULT FALSE | Shared flag |
| refresh_interval_seconds | INTEGER | DEFAULT 300 | Refresh interval |
| filters | JSONB | NULL | Global filters |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: kpis

**Purpose:** Key Performance Indicators

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(255) | NOT NULL | KPI name |
| code | VARCHAR(100) | UNIQUE, NOT NULL | KPI code |
| description | TEXT | NULL | Description |
| category | VARCHAR(100) | NOT NULL | Category |
| current_value | NUMERIC(20,4) | NULL | Current value |
| previous_value | NUMERIC(20,4) | NULL | Previous value |
| target_value | NUMERIC(20,4) | NULL | Target value |
| warning_threshold | NUMERIC(20,4) | NULL | Warning threshold |
| critical_threshold | NUMERIC(20,4) | NULL | Critical threshold |
| trend | ENUM | NULL | KPITrend enum |
| trend_percentage | NUMERIC(10,2) | NULL | Trend % |
| period | ENUM | DEFAULT 'MONTHLY' | KPIPeriod enum |
| period_start | TIMESTAMP | NULL | Period start |
| period_end | TIMESTAMP | NULL | Period end |
| calculation_formula | TEXT | NULL | Formula |
| unit | VARCHAR(50) | NULL | Unit |
| is_active | BOOLEAN | DEFAULT TRUE | Active flag |
| historical_data | JSONB | NULL | History |
| last_calculated_at | TIMESTAMP | NULL | Last calculated |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**KPIPeriod Enum (lowercase):** `daily`, `weekly`, `monthly`, `quarterly`, `yearly`
**KPITrend Enum (lowercase):** `up`, `down`, `stable`

---

### Table: metric_snapshots

**Purpose:** Time-series metric storage

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| metric_name | VARCHAR(100) | NOT NULL | Metric name |
| metric_type | VARCHAR(50) | NOT NULL | Type (counter/gauge/histogram) |
| value | NUMERIC(20,4) | NOT NULL | Value |
| dimensions | JSONB | NULL | Dimensions for filtering |
| timestamp | TIMESTAMP | NOT NULL | Measurement time |
| tags | JSONB | NULL | Additional tags |
| source | VARCHAR(100) | NULL | Source system |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: performance_data

**Purpose:** Courier performance metrics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| courier_id | INTEGER | FK couriers.id (CASCADE) | Courier |
| date | DATE | NOT NULL | Performance date |
| orders_completed | INTEGER | DEFAULT 0 | Completed orders |
| orders_failed | INTEGER | DEFAULT 0 | Failed orders |
| on_time_deliveries | INTEGER | DEFAULT 0 | On-time deliveries |
| late_deliveries | INTEGER | DEFAULT 0 | Late deliveries |
| distance_covered_km | NUMERIC(10,2) | DEFAULT 0 | Distance (km) |
| revenue_generated | NUMERIC(12,2) | DEFAULT 0 | Revenue (SAR) |
| cod_collected | NUMERIC(12,2) | DEFAULT 0 | COD collected |
| average_rating | NUMERIC(3,2) | DEFAULT 0 | Avg rating |
| working_hours | NUMERIC(5,2) | DEFAULT 0 | Working hours |
| efficiency_score | NUMERIC(5,2) | DEFAULT 0 | Efficiency score |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: reports

**Purpose:** Generated reports

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(255) | NOT NULL | Report name |
| description | TEXT | NULL | Description |
| report_type | ENUM | NOT NULL | ReportType enum |
| status | ENUM | DEFAULT 'PENDING' | ReportStatus enum |
| format | ENUM | DEFAULT 'PDF' | ReportFormat enum |
| parameters | JSONB | NULL | Report parameters |
| generated_at | TIMESTAMP | NULL | Generation time |
| scheduled_at | TIMESTAMP | NULL | Schedule time |
| file_path | VARCHAR(500) | NULL | File path |
| file_size_bytes | INTEGER | NULL | File size |
| generated_by_user_id | INTEGER | FK users.id | Generator |
| error_message | TEXT | NULL | Error message |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**ReportType Enum (lowercase):** `courier_performance`, `fleet_utilization`, `delivery_analytics`, `financial_summary`, `hr_attendance`, `maintenance_report`, `cod_reconciliation`, `custom`
**ReportStatus Enum (lowercase):** `pending`, `generating`, `completed`, `failed`, `scheduled`
**ReportFormat Enum (lowercase):** `pdf`, `excel`, `csv`, `json`

---

## Workflow Module

The workflow module provides comprehensive workflow automation with 20+ tables for templates, instances, approvals, automation, history, notifications, and SLA tracking.

### Key Tables

| Table | Purpose |
|-------|---------|
| workflow_templates | Workflow definitions |
| workflow_instances | Active workflow instances |
| approval_chains | Approval chain templates |
| approval_chain_approvers | Approvers in chains |
| approval_requests | Individual approval requests |
| workflow_attachments | File attachments |
| workflow_automations | Automation rules |
| automation_execution_logs | Automation logs |
| workflow_comments | Comments/collaboration |
| workflow_history | Audit trail |
| workflow_step_history | Step execution history |
| workflow_notification_templates | Notification templates |
| workflow_notifications | Notification instances |
| workflow_notification_preferences | User preferences |
| workflow_slas | SLA definitions |
| workflow_sla_instances | SLA tracking |
| sla_events | SLA event log |
| workflow_triggers | Trigger configurations |
| trigger_executions | Trigger execution logs |
| workflow_metrics | Aggregated metrics |
| workflow_step_metrics | Step-level metrics |
| workflow_performance_snapshots | Real-time snapshots |
| workflow_user_metrics | User-specific metrics |

---

## Admin Module

### Table: api_keys

**Purpose:** API key management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(100) | NOT NULL | Key name |
| key_prefix | VARCHAR(10) | NOT NULL | Key prefix (visible) |
| key_hash | VARCHAR(255) | NOT NULL | Key hash (SHA-256) |
| description | TEXT | NULL | Description |
| status | ENUM | DEFAULT 'ACTIVE' | ApiKeyStatus enum |
| scopes | TEXT | NULL | Scopes (JSON) |
| rate_limit_per_minute | INTEGER | DEFAULT 60 | Rate limit/min |
| rate_limit_per_hour | INTEGER | DEFAULT 1000 | Rate limit/hour |
| rate_limit_per_day | INTEGER | DEFAULT 10000 | Rate limit/day |
| ip_whitelist | TEXT | NULL | IP whitelist (JSON) |
| expires_at | TIMESTAMP | NULL | Expiration |
| last_used_at | TIMESTAMP | NULL | Last used |
| last_used_ip | VARCHAR(45) | NULL | Last used IP |
| usage_count | INTEGER | DEFAULT 0 | Usage count |
| created_by | INTEGER | FK users.id | Creator |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

**ApiKeyStatus Enum (UPPERCASE):** `ACTIVE`, `INACTIVE`, `REVOKED`, `EXPIRED`

---

### Table: backups

**Purpose:** Database backup management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(200) | NOT NULL | Backup name |
| description | TEXT | NULL | Description |
| backup_type | VARCHAR(20) | DEFAULT 'full' | Type |
| status | VARCHAR(20) | DEFAULT 'pending' | Status |
| storage_type | VARCHAR(20) | DEFAULT 'local' | Storage type |
| storage_path | VARCHAR(500) | NULL | Storage path |
| size_bytes | BIGINT | NULL | Size (bytes) |
| compressed_size_bytes | BIGINT | NULL | Compressed size |
| is_compressed | BOOLEAN | DEFAULT TRUE | Compressed flag |
| is_encrypted | BOOLEAN | DEFAULT FALSE | Encrypted flag |
| is_verified | BOOLEAN | DEFAULT FALSE | Verified flag |
| checksum | VARCHAR(128) | NULL | SHA-256 checksum |
| started_at | TIMESTAMP | NULL | Start time |
| completed_at | TIMESTAMP | NULL | Completion time |
| expires_at | TIMESTAMP | NULL | Expiration |
| is_pinned | BOOLEAN | DEFAULT FALSE | Pinned flag |
| created_by_id | INTEGER | FK users.id | Creator |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: integrations

**Purpose:** Third-party service integrations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Integration name |
| display_name | VARCHAR(100) | NOT NULL | Display name |
| description | TEXT | NULL | Description |
| integration_type | VARCHAR(50) | NOT NULL | Type |
| status | VARCHAR(20) | DEFAULT 'inactive' | Status |
| is_enabled | BOOLEAN | DEFAULT FALSE | Enabled flag |
| config | JSONB | DEFAULT '{}' | Configuration |
| credentials | JSONB | NULL | Credentials (encrypted) |
| base_url | VARCHAR(500) | NULL | Base URL |
| webhook_url | VARCHAR(500) | NULL | Webhook URL |
| last_health_check | TIMESTAMP | NULL | Last health check |
| error_count | INTEGER | DEFAULT 0 | Error count |
| success_count | INTEGER | DEFAULT 0 | Success count |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: system_settings

**Purpose:** System configuration settings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FK organizations.id | Tenant isolation |
| key | VARCHAR(100) | UNIQUE, NOT NULL | Setting key |
| name | VARCHAR(200) | NOT NULL | Display name |
| description | TEXT | NULL | Description |
| category | VARCHAR(50) | NOT NULL | Category |
| setting_type | VARCHAR(20) | NOT NULL | Type |
| value | TEXT | NULL | Value |
| default_value | TEXT | NULL | Default value |
| json_value | JSONB | NULL | JSON value |
| is_sensitive | BOOLEAN | DEFAULT FALSE | Sensitive flag |
| is_editable | BOOLEAN | DEFAULT TRUE | Editable flag |
| is_public | BOOLEAN | DEFAULT FALSE | Public flag |
| validation_regex | VARCHAR(500) | NULL | Validation regex |
| allowed_values | JSONB | NULL | Allowed values |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

## Integrations Module

### Table: syarah_fuel_transactions

**Purpose:** Syarah fuel card transactions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| transaction_id | VARCHAR(100) | UNIQUE, NOT NULL | Syarah transaction ID |
| card_number | VARCHAR(50) | NOT NULL | Card number |
| driver_id | VARCHAR(100) | NULL | Driver ID |
| vehicle_plate | VARCHAR(20) | NULL | Vehicle plate |
| station_name | VARCHAR(200) | NULL | Station name |
| station_id | VARCHAR(100) | NULL | Station ID |
| fuel_type | VARCHAR(50) | NULL | Fuel type |
| quantity_liters | NUMERIC(10,2) | NULL | Quantity |
| price_per_liter | NUMERIC(8,4) | NULL | Price/liter |
| total_amount | NUMERIC(12,2) | NOT NULL | Total amount |
| transaction_date | TIMESTAMP | NOT NULL | Transaction date |
| odometer_reading | INTEGER | NULL | Odometer |
| raw_data | JSONB | NULL | Raw API data |
| synced_at | TIMESTAMP | NOT NULL | Sync time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: syarah_fuel_statistics

**Purpose:** Aggregated fuel statistics

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| stat_date | DATE | UNIQUE, NOT NULL | Statistics date |
| total_transactions | INTEGER | DEFAULT 0 | Transaction count |
| total_liters | NUMERIC(12,2) | DEFAULT 0 | Total liters |
| total_amount | NUMERIC(14,2) | DEFAULT 0 | Total amount |
| avg_price_per_liter | NUMERIC(8,4) | NULL | Avg price |
| unique_drivers | INTEGER | DEFAULT 0 | Unique drivers |
| unique_vehicles | INTEGER | DEFAULT 0 | Unique vehicles |
| unique_stations | INTEGER | DEFAULT 0 | Unique stations |
| calculated_at | TIMESTAMP | NOT NULL | Calculation time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

### Table: syarah_sync_logs

**Purpose:** Syarah API sync logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| sync_type | VARCHAR(50) | NOT NULL | Sync type |
| status | VARCHAR(20) | NOT NULL | Status |
| started_at | TIMESTAMP | NOT NULL | Start time |
| completed_at | TIMESTAMP | NULL | Completion time |
| records_fetched | INTEGER | DEFAULT 0 | Records fetched |
| records_created | INTEGER | DEFAULT 0 | Records created |
| records_updated | INTEGER | DEFAULT 0 | Records updated |
| records_failed | INTEGER | DEFAULT 0 | Records failed |
| error_message | TEXT | NULL | Error message |
| api_response_time_ms | INTEGER | NULL | Response time |
| raw_response | JSONB | NULL | Raw response |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NULL | Last update |

---

## Enums Reference

### Case Convention

| Module | Case Convention | Example |
|--------|-----------------|---------|
| Fleet (Vehicle, Courier) | UPPERCASE | `ACTIVE`, `MAINTENANCE` |
| HR (Loan, Leave) | lowercase | `active`, `pending` |
| Operations (Dispatch, SLA) | UPPERCASE | `PENDING`, `COMPLETED` |
| Support (Ticket) | lowercase | `open`, `resolved` |
| Workflow | lowercase | `pending`, `approved` |

### Complete Enum List

See individual table definitions above for complete enum values.

---

## Migration History

| Version | Date | Description |
|---------|------|-------------|
| 001 | 2024-01-15 | Initial schema - core tables |
| 002 | 2024-02-01 | Add fleet module |
| 003 | 2024-02-15 | Add HR & finance module |
| 004 | 2024-03-01 | Add operations module |
| 005 | 2024-03-15 | Add accommodation module |
| 006 | 2024-04-01 | Add workflow engine |
| 007 | 2024-04-15 | Add support module |
| 008 | 2024-05-01 | Add analytics module |
| 009 | 2024-05-15 | Add audit logging |
| 010 | 2024-06-01 | Add tenant tables (organizations) |
| 011 | 2024-10-01 | Performance optimizations |
| 012 | 2024-11-01 | Add soft deletes |
| 013-016 | 2025-11 | Various feature additions |
| 017 | 2025-12-03 | Add organization_id to all tables |
| 018 | 2025-12-03 | Enable Row-Level Security (RLS) |
| 019 | 2025-12-05 | Add dispatch_assignments, priority_queue, SLA tables |
| 020 | 2025-12-09 | Add platform integrations, FMS fields |

---

**Document Owner:** Database Team
**Review Cycle:** Monthly
**Last Updated:** December 9, 2025
