# BARQ Fleet Management - Database Schema Documentation

**Version:** 1.1.0
**Database:** PostgreSQL 16
**Last Updated:** December 3, 2025

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
11. [Indexes](#indexes)
12. [Constraints](#constraints)
13. [Migration History](#migration-history)

---

## Overview

### Database Information

- **Name:** barq_fleet
- **Engine:** PostgreSQL 16
- **Character Set:** UTF-8
- **Collation:** en_US.UTF-8
- **Total Tables:** 69+
- **Total Migrations:** 18

### Design Principles

1. **Normalization:** 3NF (Third Normal Form)
2. **Primary Keys:** UUID v4 for all entities
3. **Timestamps:** All tables have created_at, updated_at
4. **Soft Deletes:** deleted_at column for important entities
5. **Audit Trail:** audit_logs table for critical operations
6. **Foreign Keys:** Enforce referential integrity
7. **Indexes:** Strategic indexing for performance

---

## Schema Diagram

### Entity Relationship Overview

```
┌─────────────────────┐
│    organizations    │
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│users │  │ roles│
└──┬───┘  └──┬───┘
   │         │
   └────┬────┘
        │
    ┌───▼────────┐
    │            │
┌───▼───┐    ┌──▼─────┐
│couriers│   │vehicles│
└───┬───┘    └──┬─────┘
    │           │
    └─────┬─────┘
          │
┌─────────▼───────────────────┐
│courier_vehicle_assignments  │
└─────────┬───────────────────┘
          │
    ┌─────┴─────┐
    │           │
┌───▼──────┐ ┌─▼────────┐
│attendance│ │deliveries│
└──────────┘ └──────────┘
```

---

## Core Module

### Table: users

**Purpose:** System users (admins, managers, etc.)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization association |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt password |
| full_name | VARCHAR(255) | NOT NULL | Full name |
| role_id | UUID | FOREIGN KEY | User role |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| last_login | TIMESTAMP | NULL | Last login time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Indexes:**
- `idx_users_email` (email)
- `idx_users_organization` (organization_id)
- `idx_users_role` (role_id)

**Sample Query:**
```sql
-- Get active users with their roles
SELECT u.id, u.email, u.full_name, r.name as role
FROM users u
JOIN roles r ON u.role_id = r.id
WHERE u.is_active = true AND u.deleted_at IS NULL;
```

---

### Table: roles

**Purpose:** User roles and permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization association |
| name | VARCHAR(50) | NOT NULL | Role name |
| description | TEXT | NULL | Role description |
| permissions | JSONB | NOT NULL | Permission array |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_roles_name` (name)
- `idx_roles_organization` (organization_id)

**Sample Data:**
```sql
INSERT INTO roles (name, permissions) VALUES
('admin', '["*"]'),
('manager', '["couriers.read", "couriers.write", "vehicles.read"]'),
('hr_manager', '["hr.*", "payroll.*"]'),
('operations', '["deliveries.*", "incidents.*"]');
```

---

### Table: organizations

**Purpose:** Multi-tenancy support (tenant isolation)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| name | VARCHAR(255) | NOT NULL | Organization name |
| slug | VARCHAR(100) | UNIQUE | URL-safe identifier |
| settings | JSONB | NULL | Organization settings |
| subscription_plan | VARCHAR(20) | DEFAULT 'FREE' | FREE/BASIC/PROFESSIONAL/ENTERPRISE |
| subscription_status | VARCHAR(20) | DEFAULT 'TRIAL' | TRIAL/ACTIVE/SUSPENDED/CANCELLED |
| trial_ends_at | TIMESTAMP | NULL | Trial expiration |
| max_users | INTEGER | DEFAULT 5 | Max users allowed |
| max_couriers | INTEGER | DEFAULT 50 | Max couriers allowed |
| max_vehicles | INTEGER | DEFAULT 25 | Max vehicles allowed |
| is_active | BOOLEAN | DEFAULT TRUE | Status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

### Table: organization_users

**Purpose:** Organization membership and roles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| user_id | INTEGER | FOREIGN KEY | User |
| role | VARCHAR(20) | NOT NULL | OWNER/ADMIN/MANAGER/VIEWER |
| is_active | BOOLEAN | DEFAULT TRUE | Membership status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_org_users_org` (organization_id)
- `idx_org_users_user` (user_id)
- UNIQUE (organization_id, user_id)

---

### Table: audit_logs

**Purpose:** Audit trail for critical operations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| user_id | UUID | FOREIGN KEY | User who performed action |
| action | VARCHAR(50) | NOT NULL | Action type |
| entity_type | VARCHAR(50) | NOT NULL | Entity (e.g., 'courier') |
| entity_id | UUID | NOT NULL | Entity ID |
| changes | JSONB | NULL | Before/after values |
| ip_address | VARCHAR(45) | NULL | Client IP |
| user_agent | TEXT | NULL | Client user agent |
| created_at | TIMESTAMP | NOT NULL | Action timestamp |

**Indexes:**
- `idx_audit_logs_user` (user_id)
- `idx_audit_logs_entity` (entity_type, entity_id)
- `idx_audit_logs_created` (created_at)

---

## Fleet Module

### Table: couriers

**Purpose:** Courier workforce management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| name | VARCHAR(255) | NOT NULL | Full name |
| email | VARCHAR(255) | UNIQUE | Email address |
| phone | VARCHAR(20) | NOT NULL | Phone number |
| national_id | VARCHAR(20) | UNIQUE, NOT NULL | National ID |
| date_of_birth | DATE | NULL | Date of birth |
| nationality | VARCHAR(50) | NULL | Nationality |
| license_number | VARCHAR(50) | NULL | Driving license |
| license_expiry | DATE | NULL | License expiry |
| iban | VARCHAR(34) | NULL | Bank IBAN |
| bank_name | VARCHAR(100) | NULL | Bank name |
| emergency_contact_name | VARCHAR(255) | NULL | Emergency contact |
| emergency_contact_phone | VARCHAR(20) | NULL | Emergency phone |
| emergency_contact_relationship | VARCHAR(50) | NULL | Relationship |
| status | VARCHAR(20) | NOT NULL | active/inactive/suspended |
| hire_date | DATE | NOT NULL | Hire date |
| termination_date | DATE | NULL | Termination date |
| basic_salary | DECIMAL(10,2) | DEFAULT 0 | Monthly salary |
| allowances | DECIMAL(10,2) | DEFAULT 0 | Monthly allowances |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Indexes:**
- `idx_couriers_email` (email)
- `idx_couriers_national_id` (national_id)
- `idx_couriers_phone` (phone)
- `idx_couriers_status` (status)
- `idx_couriers_organization` (organization_id)

**Sample Query:**
```sql
-- Get active couriers with current vehicle assignment
SELECT
    c.id,
    c.name,
    c.phone,
    c.status,
    v.plate_number,
    v.model
FROM couriers c
LEFT JOIN courier_vehicles cv ON c.id = cv.courier_id AND cv.end_date IS NULL
LEFT JOIN vehicles v ON cv.vehicle_id = v.id
WHERE c.status = 'active' AND c.deleted_at IS NULL;
```

---

### Table: vehicles

**Purpose:** Fleet vehicle inventory

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| plate_number | VARCHAR(20) | UNIQUE, NOT NULL | License plate |
| model | VARCHAR(100) | NOT NULL | Vehicle model |
| type | VARCHAR(20) | NOT NULL | motorcycle/car/van |
| year | INTEGER | NULL | Manufacture year |
| color | VARCHAR(50) | NULL | Vehicle color |
| vin | VARCHAR(17) | UNIQUE | VIN number |
| purchase_date | DATE | NULL | Purchase date |
| purchase_price | DECIMAL(10,2) | NULL | Purchase price |
| status | VARCHAR(20) | NOT NULL | available/assigned/maintenance/retired |
| mileage | INTEGER | DEFAULT 0 | Current mileage |
| last_maintenance_date | DATE | NULL | Last maintenance |
| next_maintenance_due | DATE | NULL | Next maintenance |
| insurance_company | VARCHAR(100) | NULL | Insurance provider |
| insurance_policy_number | VARCHAR(50) | NULL | Policy number |
| insurance_expiry | DATE | NULL | Insurance expiry |
| registration_expiry | DATE | NULL | Registration expiry |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |
| deleted_at | TIMESTAMP | NULL | Soft delete |

**Indexes:**
- `idx_vehicles_plate` (plate_number)
- `idx_vehicles_status` (status)
- `idx_vehicles_type` (type)
- `idx_vehicles_organization` (organization_id)

---

### Table: courier_vehicle_assignments

**Purpose:** Courier-vehicle assignment junction table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Courier |
| vehicle_id | UUID | FOREIGN KEY | Vehicle |
| start_date | DATE | NOT NULL | Assignment start |
| end_date | DATE | NULL | Assignment end |
| notes | TEXT | NULL | Assignment notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_courier_vehicles_courier` (courier_id)
- `idx_courier_vehicles_vehicle` (vehicle_id)
- `idx_courier_vehicles_dates` (start_date, end_date)

**Constraints:**
```sql
-- Ensure no overlapping assignments for same vehicle
CREATE UNIQUE INDEX idx_vehicle_active_assignment
ON courier_vehicles (vehicle_id)
WHERE end_date IS NULL;

-- Ensure no overlapping assignments for same courier
CREATE UNIQUE INDEX idx_courier_active_assignment
ON courier_vehicles (courier_id)
WHERE end_date IS NULL;
```

---

### Table: vehicle_logs

**Purpose:** Vehicle maintenance and incident logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| vehicle_id | UUID | FOREIGN KEY | Vehicle |
| log_type | VARCHAR(20) | NOT NULL | maintenance/repair/accident/inspection |
| date | DATE | NOT NULL | Log date |
| description | TEXT | NOT NULL | Description |
| cost | DECIMAL(10,2) | DEFAULT 0 | Cost |
| mileage_at_service | INTEGER | NULL | Mileage |
| performed_by | VARCHAR(255) | NULL | Service provider |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_vehicle_logs_vehicle` (vehicle_id)
- `idx_vehicle_logs_date` (date)
- `idx_vehicle_logs_type` (log_type)

---

## HR & Finance Module

### Table: attendance

**Purpose:** Daily courier attendance tracking

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Courier |
| date | DATE | NOT NULL | Attendance date |
| check_in | TIME | NULL | Check-in time |
| check_out | TIME | NULL | Check-out time |
| status | VARCHAR(20) | NOT NULL | present/absent/late/leave/holiday |
| hours_worked | DECIMAL(4,2) | DEFAULT 0 | Total hours |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_attendance_courier_date` (courier_id, date) UNIQUE
- `idx_attendance_date` (date)
- `idx_attendance_status` (status)

**Sample Query:**
```sql
-- Monthly attendance summary
SELECT
    c.name,
    COUNT(*) FILTER (WHERE a.status = 'present') as present_days,
    COUNT(*) FILTER (WHERE a.status = 'absent') as absent_days,
    SUM(a.hours_worked) as total_hours
FROM couriers c
LEFT JOIN attendance a ON c.id = a.courier_id
    AND a.date >= '2025-11-01'
    AND a.date <= '2025-11-30'
WHERE c.status = 'active'
GROUP BY c.id, c.name;
```

---

### Table: salaries

**Purpose:** Monthly salary/payroll records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Courier |
| month | INTEGER | NOT NULL | Month (1-12) |
| year | INTEGER | NOT NULL | Year |
| basic_salary | DECIMAL(10,2) | NOT NULL | Base salary |
| allowances | DECIMAL(10,2) | DEFAULT 0 | Allowances |
| bonuses | DECIMAL(10,2) | DEFAULT 0 | Bonuses |
| overtime_pay | DECIMAL(10,2) | DEFAULT 0 | Overtime |
| deductions | DECIMAL(10,2) | DEFAULT 0 | Deductions |
| loan_deduction | DECIMAL(10,2) | DEFAULT 0 | Loan installment |
| gross_salary | DECIMAL(10,2) | NOT NULL | Gross amount |
| net_salary | DECIMAL(10,2) | NOT NULL | Net amount |
| status | VARCHAR(20) | NOT NULL | pending/approved/paid |
| payment_date | DATE | NULL | Payment date |
| payment_method | VARCHAR(50) | NULL | bank_transfer/cash |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_payroll_courier_period` (courier_id, month, year) UNIQUE
- `idx_payroll_status` (status)
- `idx_payroll_period` (month, year)

---

### Table: loans

**Purpose:** Courier loan management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Courier |
| amount | DECIMAL(10,2) | NOT NULL | Loan amount |
| installments | INTEGER | NOT NULL | Number of installments |
| installment_amount | DECIMAL(10,2) | NOT NULL | Monthly installment |
| remaining_amount | DECIMAL(10,2) | NOT NULL | Remaining balance |
| reason | TEXT | NULL | Loan reason |
| status | VARCHAR(20) | NOT NULL | pending/approved/rejected/active/completed |
| request_date | DATE | NOT NULL | Request date |
| approval_date | DATE | NULL | Approval date |
| approved_by | UUID | FOREIGN KEY | Approver user ID |
| disbursement_date | DATE | NULL | Disbursement date |
| completion_date | DATE | NULL | Completion date |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_loans_courier` (courier_id)
- `idx_loans_status` (status)

---

### Table: leaves

**Purpose:** Leave request management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Courier |
| leave_type | VARCHAR(20) | NOT NULL | annual/sick/emergency/unpaid |
| start_date | DATE | NOT NULL | Leave start |
| end_date | DATE | NOT NULL | Leave end |
| days | INTEGER | NOT NULL | Total days |
| reason | TEXT | NULL | Leave reason |
| status | VARCHAR(20) | NOT NULL | pending/approved/rejected |
| requested_date | DATE | NOT NULL | Request date |
| approved_by | UUID | FOREIGN KEY | Approver |
| approval_date | DATE | NULL | Approval date |
| rejection_reason | TEXT | NULL | Rejection reason |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_leave_requests_courier` (courier_id)
- `idx_leave_requests_dates` (start_date, end_date)
- `idx_leave_requests_status` (status)

---

### Table: assets

**Purpose:** Company asset assignment to couriers

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Courier (nullable) |
| asset_type | VARCHAR(50) | NOT NULL | phone/tablet/uniform/bag |
| asset_name | VARCHAR(255) | NOT NULL | Asset name |
| serial_number | VARCHAR(100) | UNIQUE | Serial/IMEI |
| purchase_date | DATE | NULL | Purchase date |
| purchase_price | DECIMAL(10,2) | NULL | Purchase price |
| assigned_date | DATE | NULL | Assignment date |
| return_date | DATE | NULL | Return date |
| status | VARCHAR(20) | NOT NULL | available/assigned/damaged/retired |
| condition | VARCHAR(20) | NULL | excellent/good/fair/poor |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

---

## Operations Module

### Table: deliveries

**Purpose:** Delivery task management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Assigned courier |
| order_number | VARCHAR(50) | UNIQUE | Order reference |
| customer_name | VARCHAR(255) | NOT NULL | Customer name |
| customer_phone | VARCHAR(20) | NOT NULL | Customer phone |
| pickup_address | TEXT | NOT NULL | Pickup location |
| delivery_address | TEXT | NOT NULL | Delivery location |
| status | VARCHAR(20) | NOT NULL | pending/assigned/in_progress/completed/failed |
| scheduled_time | TIMESTAMP | NULL | Scheduled time |
| pickup_time | TIMESTAMP | NULL | Actual pickup |
| delivery_time | TIMESTAMP | NULL | Actual delivery |
| cod_amount | DECIMAL(10,2) | DEFAULT 0 | Cash on delivery |
| delivery_fee | DECIMAL(10,2) | DEFAULT 0 | Delivery fee |
| notes | TEXT | NULL | Notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Indexes:**
- `idx_deliveries_courier` (courier_id)
- `idx_deliveries_status` (status)
- `idx_deliveries_order` (order_number)
- `idx_deliveries_date` (scheduled_time)

---

### Table: incidents

**Purpose:** Incident and accident reporting

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| courier_id | UUID | FOREIGN KEY | Involved courier |
| vehicle_id | UUID | FOREIGN KEY | Involved vehicle |
| incident_type | VARCHAR(20) | NOT NULL | accident/theft/damage/other |
| incident_date | DATE | NOT NULL | Incident date |
| incident_time | TIME | NULL | Incident time |
| location | TEXT | NULL | Incident location |
| description | TEXT | NOT NULL | Description |
| severity | VARCHAR(20) | NOT NULL | low/medium/high/critical |
| status | VARCHAR(20) | NOT NULL | reported/investigating/resolved/closed |
| police_report_number | VARCHAR(50) | NULL | Police report |
| insurance_claim_number | VARCHAR(50) | NULL | Insurance claim |
| estimated_cost | DECIMAL(10,2) | NULL | Estimated cost |
| actual_cost | DECIMAL(10,2) | NULL | Actual cost |
| resolution_date | DATE | NULL | Resolution date |
| resolution_notes | TEXT | NULL | Resolution notes |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

---

## Accommodation Module

### Table: buildings

**Purpose:** Property/building management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| name | VARCHAR(255) | NOT NULL | Building name |
| address | TEXT | NOT NULL | Full address |
| city | VARCHAR(100) | NOT NULL | City |
| total_rooms | INTEGER | NOT NULL | Total rooms |
| rent_amount | DECIMAL(10,2) | NULL | Monthly rent |
| contract_start | DATE | NULL | Contract start |
| contract_end | DATE | NULL | Contract end |
| landlord_name | VARCHAR(255) | NULL | Landlord name |
| landlord_phone | VARCHAR(20) | NULL | Landlord phone |
| status | VARCHAR(20) | NOT NULL | active/inactive |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

---

### Table: rooms

**Purpose:** Individual room management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| building_id | UUID | FOREIGN KEY | Building |
| room_number | VARCHAR(20) | NOT NULL | Room number |
| capacity | INTEGER | NOT NULL | Max occupants |
| current_occupants | INTEGER | DEFAULT 0 | Current count |
| status | VARCHAR(20) | NOT NULL | available/occupied/maintenance |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

**Constraints:**
```sql
-- Ensure unique room numbers per building
CREATE UNIQUE INDEX idx_room_number_building
ON rooms (building_id, room_number);
```

---

### Table: room_assignments

**Purpose:** Courier room assignment

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| room_id | UUID | FOREIGN KEY | Room |
| courier_id | UUID | FOREIGN KEY | Courier |
| start_date | DATE | NOT NULL | Assignment start |
| end_date | DATE | NULL | Assignment end |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

---

## Workflow Module

### Table: workflow_templates

**Purpose:** Workflow templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| name | VARCHAR(255) | NOT NULL | Workflow name |
| workflow_type | VARCHAR(50) | NOT NULL | leave_request/loan_request/etc |
| steps | JSONB | NOT NULL | Workflow steps |
| is_active | BOOLEAN | DEFAULT TRUE | Active status |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

---

### Table: workflow_instances

**Purpose:** Active workflow instances

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| workflow_definition_id | UUID | FOREIGN KEY | Definition |
| entity_type | VARCHAR(50) | NOT NULL | Entity type |
| entity_id | UUID | NOT NULL | Entity ID |
| status | VARCHAR(20) | NOT NULL | pending/approved/rejected |
| current_step | INTEGER | DEFAULT 0 | Current step |
| initiated_by | UUID | FOREIGN KEY | Initiator |
| initiated_at | TIMESTAMP | NOT NULL | Start time |
| completed_at | TIMESTAMP | NULL | Completion time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

---

### Table: workflow_approvals

**Purpose:** Workflow approval steps

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| workflow_instance_id | UUID | FOREIGN KEY | Instance |
| step_number | INTEGER | NOT NULL | Step number |
| approver_id | UUID | FOREIGN KEY | Approver |
| status | VARCHAR(20) | NOT NULL | pending/approved/rejected |
| comments | TEXT | NULL | Comments |
| approved_at | TIMESTAMP | NULL | Approval time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

---

## Support Module

### Table: tickets

**Purpose:** Support ticket management

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| organization_id | INTEGER | FOREIGN KEY | Organization |
| ticket_number | VARCHAR(20) | UNIQUE | Ticket number |
| created_by | UUID | FOREIGN KEY | Creator |
| assigned_to | UUID | FOREIGN KEY | Assignee |
| category | VARCHAR(50) | NOT NULL | vehicle/delivery/hr/technical |
| priority | VARCHAR(20) | NOT NULL | low/medium/high/critical |
| status | VARCHAR(20) | NOT NULL | open/in_progress/resolved/closed |
| subject | VARCHAR(255) | NOT NULL | Subject |
| description | TEXT | NOT NULL | Description |
| resolution | TEXT | NULL | Resolution |
| resolved_at | TIMESTAMP | NULL | Resolution time |
| created_at | TIMESTAMP | NOT NULL | Creation time |
| updated_at | TIMESTAMP | NOT NULL | Last update |

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

---

## Sample Queries

### Complex Joins

```sql
-- Get courier with vehicle, attendance, and payroll
SELECT
    c.name,
    c.phone,
    c.status,
    v.plate_number,
    v.model,
    COUNT(a.id) as attendance_days,
    SUM(p.net_salary) as total_earned
FROM couriers c
LEFT JOIN courier_vehicles cv ON c.id = cv.courier_id AND cv.end_date IS NULL
LEFT JOIN vehicles v ON cv.vehicle_id = v.id
LEFT JOIN attendance a ON c.id = a.courier_id AND a.date >= '2025-11-01'
LEFT JOIN payroll p ON c.id = p.courier_id AND p.year = 2025
WHERE c.status = 'active'
GROUP BY c.id, c.name, c.phone, c.status, v.plate_number, v.model;
```

---

**Document Owner:** Database Team
**Review Cycle:** Monthly
**Last Updated:** December 3, 2025
