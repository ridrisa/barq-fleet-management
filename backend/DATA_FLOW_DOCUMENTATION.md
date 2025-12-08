# BARQ Fleet Management System - Data Flow Documentation

## Overview

This document describes the complete data flow architecture for the BARQ Fleet Management System, a multi-tenant SaaS platform for managing delivery fleets, couriers, HR operations, and financial tracking.

---

## 1. Core Entity Relationships

### 1.1 Entity Hierarchy

```
Organization (Tenant Root)
├── Users (System users with roles)
├── Couriers (Fleet delivery personnel)
│   ├── Vehicle Assignments
│   ├── Accommodation Allocations
│   ├── HR Records (Leaves, Loans, Salaries, Attendance, Assets)
│   ├── Operations (Deliveries, COD, Incidents)
│   └── Support Tickets
├── Vehicles (Fleet assets)
│   ├── Fuel Logs
│   ├── Maintenance Records
│   ├── Inspections
│   └── Accident Logs
└── Buildings (Accommodation facilities)
    └── Rooms → Beds → Allocations
```

### 1.2 Primary Key Relationships (187 Total FK Relationships)

| Parent Entity | Referencing Tables | Relationship Count |
|---------------|-------------------|-------------------|
| Couriers | 33 tables | Most referenced entity |
| Vehicles | 12 tables | Fleet core entity |
| Users | 15 tables | Auth/audit trail |
| Organizations | 91 tables | Multi-tenant isolation |

---

## 2. Courier Lifecycle Data Flow

### 2.1 Onboarding Flow

```
[Recruitment] → [Courier Creation] → [Document Upload] → [Training] → [Vehicle Assignment] → [Active Status]
     │                  │                    │                │               │
     v                  v                    v                v               v
  (External)     couriers table       documents table    training_logs   courier_vehicle_assignments
                 status: ONBOARDING   (iqama, passport,  (if tracked)    vehicle_logs
                                       license uploads)
```

**Key Service:** `CourierService.create()` → `CourierService.assign_vehicle()`

### 2.2 Active Courier Daily Operations

```
                         ┌─────────────────────────────────────────┐
                         │           ACTIVE COURIER                │
                         └─────────────────────────────────────────┘
                                          │
         ┌────────────────────────────────┼────────────────────────────────┐
         │                                │                                │
         v                                v                                v
   ┌─────────────┐               ┌─────────────┐                 ┌─────────────┐
   │ ATTENDANCE  │               │ DELIVERIES  │                 │ INCIDENTS   │
   │ punch_in/out│               │ assignments │                 │ reports     │
   └─────────────┘               └─────────────┘                 └─────────────┘
         │                                │                                │
         v                                v                                v
  attendances table              deliveries table                 incidents table
  (daily records)                (package tracking)               (accidents, issues)
         │                                │
         v                                v
  Payroll Engine ←────────────── COD Collection ──────────────→ Finance Reconciliation
```

**Key Services:**
- `AttendanceService.record_punch_in/out()`
- `DeliveryService.update_status()`
- `CODService.mark_as_collected()`

### 2.3 Document Expiry Monitoring

```
Courier Documents (iqama, passport, license)
         │
         v
   ┌─────────────────────────────────────┐
   │     Document Expiry Check           │
   │  (scheduled job or on-demand)       │
   └─────────────────────────────────────┘
         │
         ├── 30 days before expiry → Warning notification
         │
         └── Expired → Status: SUSPENDED, alert generated
```

**Key Service:** `CourierService.get_expiring_documents(days_threshold=30)`

### 2.4 Termination Flow

```
[Resignation/Termination Request]
         │
         v
   ┌─────────────────────────────────────┐
   │     Offboarding Process             │
   └─────────────────────────────────────┘
         │
         ├── EOS Calculation → eos_calculator_service.py
         │   └── Years of service, final settlement
         │
         ├── Outstanding Loan Check → loan_service.py
         │   └── Deduct from final settlement
         │
         ├── Asset Recovery → asset_service.py
         │   └── Return phones, uniforms, bags
         │
         ├── COD Settlement → cod_service.py
         │   └── Collect all pending cash
         │
         └── Update Status → CourierStatus.TERMINATED
             └── Set last_working_day
```

---

## 3. Operations/Delivery Data Flow

### 3.1 Delivery Lifecycle

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                          DELIVERY LIFECYCLE                                   │
└──────────────────────────────────────────────────────────────────────────────┘

  [Order Created]                    Platform Integration (Jahez, Hunger, Mrsool)
        │                                      │
        v                                      v
  ┌─────────────┐                     ┌─────────────────┐
  │  PENDING    │ ←────────────────── │  External API   │
  │  delivery   │                     │  webhook/pull   │
  └─────────────┘                     └─────────────────┘
        │
        v  (Dispatch assigns to courier)
  ┌─────────────┐
  │  ASSIGNED   │  ←── courier_id, vehicle_id assigned
  └─────────────┘
        │
        v  (Courier picks up)
  ┌─────────────┐
  │  PICKED_UP  │  ←── pickup_time recorded
  └─────────────┘
        │
        v  (In transit, GPS tracking via FMS)
  ┌─────────────┐
  │  IN_TRANSIT │  ←── FMS real-time location
  └─────────────┘
        │
        ├────────────────────────────────┐
        v                                v
  ┌─────────────┐                 ┌─────────────┐
  │  DELIVERED  │                 │  FAILED     │
  │             │                 │  (returned) │
  └─────────────┘                 └─────────────┘
        │                                │
        v                                v
  COD Collection                  Incident Report
  (if cash payment)               (failure reason)
```

**Key Service:** `DeliveryService`

### 3.2 COD (Cash on Delivery) Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              COD FLOW                                         │
└──────────────────────────────────────────────────────────────────────────────┘

  [Delivery Completed with COD]
        │
        v
  ┌─────────────┐
  │   PENDING   │  Cash collected by courier, not yet handed over
  └─────────────┘
        │
        v  (Courier hands cash to supervisor)
  ┌─────────────┐
  │  COLLECTED  │  reference_number assigned
  └─────────────┘
        │
        v  (Cash deposited to bank)
  ┌─────────────┐
  │  DEPOSITED  │  deposit_date recorded
  └─────────────┘
        │
        v  (Finance reconciliation complete)
  ┌─────────────┐
  │ RECONCILED  │  Final state
  └─────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │ Key Operations:                                                          │
  │ - get_courier_balance(courier_id) → Total pending + collected amount     │
  │ - settle_courier_cod(courier_id) → Bulk deposit all courier's COD        │
  │ - bulk_deposit([cod_ids]) → Mass deposit operation                       │
  └─────────────────────────────────────────────────────────────────────────┘
```

**Key Service:** `CODService`

---

## 4. Financial Data Flow

### 4.1 Payroll Processing Flow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MONTHLY PAYROLL ENGINE                                │
└──────────────────────────────────────────────────────────────────────────────┘

   ┌─────────────────────┐
   │  PayrollEngineService│
   │  run_monthly_payroll │
   └─────────────────────┘
              │
              v
   ┌─────────────────────────────────────────────────────────────────┐
   │   For each ACTIVE courier in organization                        │
   └─────────────────────────────────────────────────────────────────┘
              │
   ┌──────────┼──────────┬──────────────┬────────────────┐
   v          v          v              v                v
┌──────┐  ┌──────┐  ┌──────────┐  ┌──────────┐   ┌──────────┐
│ Base │  │Attend│  │   Loan   │  │   GOSI   │   │  Bonus   │
│Salary│  │ance  │  │Deduction │  │Deduction │   │Calculate │
└──────┘  └──────┘  └──────────┘  └──────────┘   └──────────┘
   │          │          │              │               │
   │          │          │              │               │
   │   ┌──────┘          │              │               │
   │   │ Days worked vs  │              │               │
   │   │ expected days   │              │               │
   │   │     │           │              │               │
   │   │     v           │              │               │
   │   │ Absence/Late    │              │               │
   │   │ deductions      │              │               │
   │   │                 │              │               │
   v   v                 v              v               v
┌─────────────────────────────────────────────────────────────┐
│                     SALARY CALCULATION                       │
│                                                              │
│  gross_salary = base_salary + allowances + bonus             │
│  total_deductions = absence + late + loans + gosi            │
│  net_salary = gross_salary - total_deductions                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
              │
              v
        salaries table
        (month, year, courier_id, amounts)
              │
              v
     mark_as_paid(salary_id, payment_date)
```

**Key Services:**
- `PayrollEngineService.run_monthly_payroll()`
- `AttendanceService` → Working days, late arrivals
- `LoanService.get_monthly_deduction()` → Active loan installments
- `GOSICalculatorService` → Saudi social insurance

### 4.2 Loan Lifecycle

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              LOAN LIFECYCLE                                   │
└──────────────────────────────────────────────────────────────────────────────┘

  [Courier Request]
        │
        v
  ┌─────────────┐
  │   PENDING   │  loan created, awaiting approval
  └─────────────┘
        │
        v  (Manager approves)
  ┌─────────────┐
  │   ACTIVE    │  outstanding_balance = amount
  └─────────────┘   monthly_deduction set
        │
        │  ─────────────────────────────────────────────┐
        │       Monthly Payroll                         │
        v                                               │
  ┌─────────────────────────────────────────────────┐   │
  │  Monthly Deduction from Salary                   │   │
  │  loan_service.make_payment(loan_id, amount)      │ ←─┘
  │  outstanding_balance -= payment                  │
  └─────────────────────────────────────────────────┘
        │
        │  (When outstanding_balance <= 0)
        v
  ┌─────────────┐
  │  COMPLETED  │  end_date = today
  └─────────────┘

  Alternative path:
        │
        v
  ┌─────────────┐
  │  CANCELLED  │  (if loan withdrawn/rejected)
  └─────────────┘
```

**Key Service:** `LoanService`

### 4.3 Salary-Loan Integration

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     SALARY-LOAN INTEGRATION                                   │
└──────────────────────────────────────────────────────────────────────────────┘

  PayrollEngineService._process_courier_payroll(courier)
                    │
                    v
        loan_service.get_monthly_deduction(courier_id)
                    │
                    ├── Query all ACTIVE loans for courier
                    │
                    └── SUM(monthly_deduction) for all active loans
                                │
                                v
                    salary.loan_deduction = total_loan_deduction
                                │
                                v
                    net_salary -= loan_deduction
```

---

## 5. Integration Points

### 5.1 FMS (Fleet Management System) Integration

**Provider:** Machinestalk GPS Tracking

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         FMS INTEGRATION FLOW                                  │
└──────────────────────────────────────────────────────────────────────────────┘

  External System                           BARQ System
  ─────────────                           ───────────────

  Machinestalk FMS
  ┌─────────────┐
  │ GPS Devices │ ──────────────────┐
  │ on Vehicles │                   │
  └─────────────┘                   │
                                    │
  FMS API                           │
  ┌─────────────┐                   │     ┌──────────────────────┐
  │ /assets     │ ←─────────────────┼───→ │ FMSClient            │
  │ /drivers    │    HTTP REST      │     │ (fms/client.py)      │
  │ /vehicles   │                   │     └──────────────────────┘
  │ /tracking   │                   │              │
  └─────────────┘                   │              v
                                    │     ┌──────────────────────┐
                                    │     │ FMSSyncService       │
                                    └───→ │ (fms/sync.py)        │
                                          └──────────────────────┘
                                                   │
                                    ┌──────────────┴──────────────┐
                                    v                             v
                            ┌─────────────┐              ┌─────────────┐
                            │  couriers   │              │  vehicles   │
                            │ fms_asset_id│              │ fms_asset_id│
                            │ fms_driver_id              │ (future)    │
                            └─────────────┘              └─────────────┘

  Mapping Logic:
  ─────────────
  FMS PlateNumber → Courier.barq_id (via naming convention)
  FMS IDNumber    → Courier.iqama_number
  FMS Asset ID    → Courier.fms_asset_id (stored for tracking)
```

**Key Service:** `FMSSyncService.sync_fms_assets()`

### 5.2 Delivery Platform Integration

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DELIVERY PLATFORM INTEGRATION                              │
└──────────────────────────────────────────────────────────────────────────────┘

  External Platforms                      BARQ Courier Mapping
  ──────────────────                      ────────────────────

  ┌─────────────┐
  │   Jahez     │ ──────────────────────→ courier.jahez_driver_id
  │   (Food)    │
  └─────────────┘

  ┌─────────────┐
  │   Hunger    │ ──────────────────────→ courier.hunger_rider_id
  │   Station   │
  └─────────────┘

  ┌─────────────┐
  │   Mrsool    │ ──────────────────────→ courier.mrsool_courier_id
  │             │
  └─────────────┘

  Data Flow:
  ──────────
  1. Platform sends delivery request (webhook/API)
  2. BARQ matches courier via platform-specific ID
  3. Delivery assigned and tracked in BARQ system
  4. Status updates sync back to platform
```

### 5.3 Notification System

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      NOTIFICATION FLOW                                        │
└──────────────────────────────────────────────────────────────────────────────┘

  Event Triggers                          Notification Services
  ──────────────                          ────────────────────

  Document expiry     ─────────┐
  Loan approved       ─────────┤          ┌──────────────────────┐
  Delivery assigned   ─────────┼────────→ │ Email Service        │
  Salary processed    ─────────┤          │ (SendGrid/SMTP)      │
  Incident reported   ─────────┘          └──────────────────────┘
                                                    │
                                                    v
                                          ┌──────────────────────┐
                                          │ SMS Service          │
                                          │ (Twilio/Local)       │
                                          └──────────────────────┘

  Key Services:
  - email_notification_service.py
  - sms_notification_service.py
```

---

## 6. Multi-Tenant Data Isolation

### 6.1 Tenant Isolation Model

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      MULTI-TENANT ARCHITECTURE                                │
└──────────────────────────────────────────────────────────────────────────────┘

  All 91 tables include organization_id column via TenantMixin

  ┌───────────────────────────────────────────────────────────────────────┐
  │                         Request Flow                                   │
  │                                                                        │
  │  API Request → JWT Token → Extract org_id → Apply to all queries       │
  │                                                                        │
  │  Token payload: { sub: user_id, org_id: 1, org_role: "owner" }        │
  │                                                                        │
  └───────────────────────────────────────────────────────────────────────┘

  Service Layer Pattern:
  ──────────────────────

  class VehicleService:
      def get_active_vehicles(
          self,
          db: Session,
          organization_id: Optional[int] = None,  # ← Tenant filter
      ) -> List[Vehicle]:
          query = db.query(Vehicle).filter(Vehicle.status == VehicleStatus.ACTIVE)

          if organization_id:
              query = query.filter(Vehicle.organization_id == organization_id)

          return query.all()
```

### 6.2 Row-Level Security

```sql
-- All queries automatically filtered by organization_id
-- Set in RLS context at connection level

SET app.current_org_id = '1';

-- RLS policy example (if using PostgreSQL RLS)
CREATE POLICY tenant_isolation ON couriers
    USING (organization_id = current_setting('app.current_org_id')::integer);
```

---

## 7. Analytics & Reporting Data Flow

### 7.1 Dashboard Data Aggregation

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      DASHBOARD DATA FLOW                                      │
└──────────────────────────────────────────────────────────────────────────────┘

  ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
  │   couriers    │      │   vehicles    │      │  deliveries   │
  │   table       │      │   table       │      │   table       │
  └───────────────┘      └───────────────┘      └───────────────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 v
                    ┌───────────────────────────┐
                    │  DashboardPerformanceService │
                    │  (dashboard_performance_service.py) │
                    └───────────────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    v            v            v
              ┌─────────┐  ┌─────────┐  ┌─────────┐
              │ Stats   │  │ Charts  │  │ Alerts  │
              │ Summary │  │ Data    │  │ Feed    │
              └─────────┘  └─────────┘  └─────────┘

  Metrics Calculated:
  ──────────────────
  - Active couriers count
  - Fleet utilization percentage
  - Delivery success rate
  - COD collection status
  - Document expiry alerts
  - Maintenance due alerts
```

### 7.2 HR Analytics

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        HR ANALYTICS FLOW                                      │
└──────────────────────────────────────────────────────────────────────────────┘

  Source Tables              Analytics Service               Output
  ─────────────              ─────────────────               ──────

  attendances    ─────────┐
  leaves         ─────────┤     ┌─────────────────────┐
  salaries       ─────────┼───→ │ HRAnalyticsService  │ ───→ Attendance Rate
  loans          ─────────┤     │                     │ ───→ Leave Patterns
  couriers       ─────────┘     └─────────────────────┘ ───→ Salary Distribution
                                                        ───→ Loan Statistics
```

---

## 8. Workflow Engine Data Flow

### 8.1 Approval Workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOW ENGINE FLOW                                     │
└──────────────────────────────────────────────────────────────────────────────┘

  Trigger Events                Workflow Processing             Output
  ──────────────                ───────────────────             ──────

  Leave Request    ─────────┐
  Loan Request     ─────────┤    ┌────────────────────────┐
  Asset Request    ─────────┼──→ │ WorkflowEngineService  │
  Expense Claim    ─────────┘    └────────────────────────┘
                                           │
                                           v
                           ┌───────────────────────────────┐
                           │     State Machine             │
                           │     PENDING → APPROVED        │
                           │     PENDING → REJECTED        │
                           └───────────────────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    v                      v                      v
             ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
             │ Notifications│      │ Audit Logs  │       │ Status Update│
             │ (email/SMS)  │      │ (history)   │       │ (entity)     │
             └─────────────┘       └─────────────┘       └─────────────┘

  Key Services:
  - workflow_engine_service.py
  - state_machine.py
  - approval_service.py
  - event_trigger_service.py
```

---

## 9. Support Ticket Data Flow

### 9.1 Ticket Lifecycle

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      SUPPORT TICKET FLOW                                      │
└──────────────────────────────────────────────────────────────────────────────┘

  [Courier/User creates ticket]
           │
           v
    ┌─────────────┐
    │    OPEN     │  created_by, category, priority
    └─────────────┘
           │
           v  (Agent picks up)
    ┌─────────────┐
    │ IN_PROGRESS │  assigned_to agent
    └─────────────┘
           │
           ├── Reply added (ticket_replies table)
           │
           ├── Attachment added (ticket_attachments table)
           │
           v  (Issue resolved)
    ┌─────────────┐
    │  RESOLVED   │  resolution notes
    └─────────────┘
           │
           v  (Customer confirms or auto-close after N days)
    ┌─────────────┐
    │   CLOSED    │  closed_at timestamp
    └─────────────┘

  Related Tables:
  ───────────────
  - tickets (main record)
  - ticket_replies (conversation thread)
  - ticket_attachments (files)
  - canned_responses (templates)
  - kb_articles (knowledge base)
```

---

## 10. Legacy/Orphaned Tables

The following tables exist in the database but have no corresponding SQLAlchemy models:

| Table Name | Status | Recommendation |
|------------|--------|----------------|
| assignments | Orphaned | Migrate data to courier_vehicle_assignments, then DROP |
| driver_orders | Orphaned | Migrate to deliveries if needed, then DROP |
| orders | Orphaned | Migrate to deliveries if needed, then DROP |
| sub_projects | Orphaned | Review usage, likely DROP |
| tasks | Orphaned | Review if needed for workflow, otherwise DROP |
| vehicle_data | Orphaned | Migrate to vehicles table, then DROP |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Database Tables | 92 |
| SQLAlchemy Models | 82 |
| API Endpoints | 737 |
| Service Files | 68 |
| FK Relationships | 187+ |
| Modules | 10 |

---

## Document History

- **Created:** 2025-12-07
- **Author:** System Analysis
- **Version:** 1.0
