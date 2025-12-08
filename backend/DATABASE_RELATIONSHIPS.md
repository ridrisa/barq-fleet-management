# BARQ Fleet Management - Database Relationship Diagrams

This document contains visual diagrams of the database relationships using Mermaid syntax.
You can render these in GitHub, Notion, or any Mermaid-compatible viewer.

---

## Core System Architecture

```mermaid
graph TB
    subgraph "Multi-Tenancy"
        ORG[Organizations]
        ORGUSER[OrganizationUsers]
        USER[Users]

        USER --> ORGUSER
        ORG --> ORGUSER
    end

    subgraph "RBAC"
        ROLE[Roles]
        PERM[Permissions]
        USERROLE[UserRoles]
        ROLEPERM[RolePermissions]

        USER --> USERROLE
        ROLE --> USERROLE
        ROLE --> ROLEPERM
        PERM --> ROLEPERM
    end

    subgraph "Audit & Security"
        AUDIT[AuditLogs]
        PWDRESET[PasswordResetTokens]

        USER --> AUDIT
        USER --> PWDRESET
    end

    ORG -.tenant isolation.-> COURIER
    ORG -.tenant isolation.-> VEHICLE

    style ORG fill:#e1f5ff
    style USER fill:#fff4e6
    style ROLE fill:#f3e5f5
```

---

## Fleet Management Domain

```mermaid
graph TB
    subgraph "Core Entities"
        COURIER[Couriers<br/>---<br/>barq_id<br/>employee_id<br/>status]
        VEHICLE[Vehicles<br/>---<br/>plate_number<br/>status<br/>type]
    end

    subgraph "Assignments"
        ASSIGN[CourierVehicleAssignments<br/>---<br/>status<br/>start_date<br/>end_date]

        COURIER -->|many-to-many| ASSIGN
        VEHICLE -->|many-to-many| ASSIGN
    end

    subgraph "Vehicle Operations"
        MAINT[VehicleMaintenance<br/>---<br/>type<br/>status<br/>cost]
        INSPECT[VehicleInspections<br/>---<br/>type<br/>status<br/>score]
        ACCIDENT[AccidentLogs<br/>---<br/>severity<br/>cost<br/>status]
        VLOG[VehicleLogs<br/>---<br/>mileage<br/>distance<br/>fuel]
        FUEL[FuelLogs<br/>---<br/>quantity<br/>cost<br/>date]

        VEHICLE -->|1:many| MAINT
        VEHICLE -->|1:many| INSPECT
        VEHICLE -->|1:many| ACCIDENT
        VEHICLE -->|1:many| VLOG
        VEHICLE -->|1:many| FUEL

        COURIER -.optional.-> ACCIDENT
        COURIER -.optional.-> VLOG
        COURIER -.optional.-> FUEL
    end

    subgraph "Documents"
        DOC[Documents<br/>---<br/>entity_type<br/>entity_id<br/>⚠️ NO FK!]

        DOC -.polymorphic.-> COURIER
        DOC -.polymorphic.-> VEHICLE
    end

    style ASSIGN fill:#fff3e0
    style ACCIDENT fill:#ffebee
    style DOC fill:#ffcdd2
```

### ⚠️ Critical Issues in Fleet Domain

1. **Circular Reference:**
   - `Courier.current_vehicle_id` → `Vehicle`
   - `CourierVehicleAssignment` also tracks this
   - **Two sources of truth!**

2. **Document Model:**
   - Polymorphic reference (entity_type + entity_id)
   - **No foreign key constraint**
   - Can point to non-existent records

3. **Missing ondelete:**
   - `FuelLog.courier_id` - no ondelete specified

---

## HR Management Domain

```mermaid
graph TB
    COURIER[Couriers]

    subgraph "Compensation"
        SALARY[Salaries<br/>---<br/>month/year<br/>⚠️ No unique constraint<br/>⚠️ No ondelete]
        BONUS[Bonuses<br/>---<br/>type<br/>amount<br/>⚠️ No ondelete]
        LOAN[Loans<br/>---<br/>amount<br/>balance<br/>⚠️ No ondelete]
    end

    subgraph "Time & Attendance"
        ATT[Attendance<br/>---<br/>date<br/>status<br/>⚠️ No unique constraint<br/>⚠️ No ondelete]
        LEAVE[Leaves<br/>---<br/>type<br/>status<br/>days<br/>⚠️ No ondelete]
    end

    subgraph "Assets"
        ASSET[Assets<br/>---<br/>type<br/>status<br/>⚠️ No ondelete]
    end

    COURIER -->|1:many| SALARY
    COURIER -->|1:many| BONUS
    COURIER -->|1:many| LOAN
    COURIER -->|1:many| ATT
    COURIER -->|1:many| LEAVE
    COURIER -->|1:many| ASSET

    USER[Users] -.approver.-> LOAN
    USER -.approver.-> LEAVE
    USER -.approver.-> BONUS

    style SALARY fill:#ffcdd2
    style BONUS fill:#ffcdd2
    style LOAN fill:#ffcdd2
    style ATT fill:#ffcdd2
    style LEAVE fill:#ffcdd2
    style ASSET fill:#ffcdd2
```

### ⚠️ Critical Issues in HR Domain

**ALL HR models are missing:**
1. `ondelete` behavior on `courier_id` FK
2. Proper cascade/restrict strategies
3. **Result:** Cannot delete couriers with any HR records

**Missing Unique Constraints:**
- `Salary`: Can have duplicate records for same courier/month
- `Attendance`: Can have duplicate records for same courier/date

---

## Accommodation Domain

```mermaid
graph TB
    COURIER[Couriers<br/>---<br/>❌ accommodation_building_id<br/>❌ accommodation_room_id<br/><i>Orphaned columns!</i>]

    subgraph "Proper Hierarchy"
        BUILD[Buildings<br/>---<br/>name<br/>total_capacity]
        ROOM[Rooms<br/>---<br/>room_number<br/>capacity<br/>⚠️ No ondelete]
        BED[Beds<br/>---<br/>bed_number<br/>status<br/>⚠️ No ondelete]
        ALLOC[Allocations<br/>---<br/>allocation_date<br/>release_date<br/>⚠️ No ondelete]
    end

    BUILD -->|1:many| ROOM
    ROOM -->|1:many| BED
    BED -->|1:1| ALLOC
    COURIER -->|1:many| ALLOC

    COURIER -.broken refs.-> BUILD
    COURIER -.broken refs.-> ROOM

    style COURIER fill:#ffcdd2
    style ROOM fill:#fff9c4
    style BED fill:#fff9c4
    style ALLOC fill:#fff9c4
```

### ⚠️ Critical Issues in Accommodation

1. **Orphaned Columns:**
   - `Courier.accommodation_building_id` - No FK constraint
   - `Courier.accommodation_room_id` - No FK constraint
   - **Should be removed** - use Allocation table

2. **Missing Cascade Chain:**
   - Delete Building → Rooms not cascade deleted
   - Delete Room → Beds not cascade deleted
   - Delete Bed → Allocations not cascade deleted
   - **All need CASCADE ondelete**

---

## Operations Domain

```mermaid
graph TB
    COURIER[Couriers]
    VEHICLE[Vehicles]

    subgraph "Route Planning"
        ZONE[Zones<br/>---<br/>zone_code<br/>boundaries<br/>status]
        ROUTE[Routes<br/>---<br/>route_number<br/>status<br/>date]

        ZONE -->|1:many| ROUTE
        COURIER -.assigned.-> ROUTE
    end

    subgraph "Deliveries"
        DELIV[Deliveries<br/>---<br/>tracking_number<br/>status<br/>⚠️ cod_amount: Integer!<br/>⚠️ No ondelete]
        COD[COD Transactions<br/>---<br/>amount: Numeric(10,2)<br/>status<br/>⚠️ No ondelete]

        COURIER -->|1:many| DELIV
        COURIER -->|1:many| COD
    end

    subgraph "Issues"
        INC[Incidents<br/>---<br/>type<br/>status<br/>⚠️ cost: Integer!<br/>⚠️ No ondelete]

        COURIER -.optional.-> INC
        VEHICLE -.optional.-> INC
    end

    style DELIV fill:#ffcdd2
    style COD fill:#ffcdd2
    style INC fill:#ffcdd2
```

### ⚠️ Critical Issues in Operations

1. **Type Inconsistencies:**
   - `Delivery.cod_amount`: Integer (loses decimals)
   - `COD.amount`: Numeric(10,2) (correct)
   - `Incident.cost`: Integer (should be Numeric)

2. **Missing ondelete:**
   - `Delivery.courier_id` - nullable=False, no ondelete
   - `COD.courier_id` - nullable=False, no ondelete
   - `Incident.courier_id` and `vehicle_id` - no ondelete

---

## Support Domain

```mermaid
graph TB
    USER[Users]
    COURIER[Couriers]

    subgraph "Ticket System"
        TICKET[Tickets<br/>---<br/>ticket_id<br/>status<br/>priority<br/>⚠️ created_by: nullable=False + ondelete=SET NULL]
        REPLY[TicketReplies<br/>---<br/>message<br/>⚠️ is_internal: Integer!<br/>⚠️ user_id: nullable=False + ondelete=SET NULL]
        ATTACH[TicketAttachments<br/>---<br/>filename<br/>file_size<br/>⚠️ uploaded_by: nullable=False + ondelete=SET NULL]
        TEMPLATE[TicketTemplates<br/>---<br/>name<br/>default_category]
    end

    COURIER -.optional.-> TICKET
    USER -->|creator| TICKET
    USER -.assignee.-> TICKET
    USER -.escalator.-> TICKET

    TICKET -->|1:many| REPLY
    TICKET -->|1:many| ATTACH
    TEMPLATE -.used by.-> TICKET

    USER -->|author| REPLY
    REPLY -->|1:many| ATTACH
    USER -->|uploader| ATTACH

    TICKET -.merged into.-> TICKET

    style TICKET fill:#fff9c4
    style REPLY fill:#ffcdd2
    style ATTACH fill:#ffcdd2
```

### ⚠️ Critical Issues in Support

**Conflicting Constraints:**
All have `nullable=False` with `ondelete=SET NULL` - **IMPOSSIBLE!**

1. `Ticket.created_by`:
   - Column is NOT NULL
   - FK has ondelete=SET NULL
   - **Cannot SET NULL on NOT NULL column**

2. `TicketReply.user_id`: Same issue

3. `TicketAttachment.uploaded_by`: Same issue

**Type Issues:**
- `TicketReply.is_internal`: Integer (should be Boolean)

---

## Relationship Summary by Type

### CASCADE Delete (Proper Cleanup)

```mermaid
graph LR
    subgraph "Should CASCADE"
        C1[Courier] -->|CASCADE| L1[Leaves]
        C1 -->|CASCADE| A1[Attendance]
        C1 -->|CASCADE| B1[Bonuses]
        C1 -->|CASCADE| VA[VehicleAssignments]

        V1[Vehicle] -->|CASCADE| M1[Maintenance]
        V1 -->|CASCADE| I1[Inspections]
        V1 -->|CASCADE| AC[AccidentLogs]
        V1 -->|CASCADE| VL[VehicleLogs]
        V1 -->|CASCADE| FL[FuelLogs]

        BUILD[Building] -->|CASCADE| ROOM[Rooms]
        ROOM -->|CASCADE| BED[Beds]
        BED -->|CASCADE| ALLOC[Allocations]
    end

    style C1 fill:#c8e6c9
    style V1 fill:#c8e6c9
    style BUILD fill:#c8e6c9
```

### SET NULL (Preserve Historical Data)

```mermaid
graph LR
    subgraph "Should SET NULL"
        C2[Courier] -.SET NULL.-> D1[Deliveries]
        C2 -.SET NULL.-> COD[COD Transactions]
        C2 -.SET NULL.-> INC[Incidents]
        C2 -.SET NULL.-> FL2[FuelLogs]

        V2[Vehicle] -.SET NULL.-> INC

        U1[User] -.SET NULL.-> AL[AuditLogs]
    end

    style C2 fill:#fff9c4
    style V2 fill:#fff9c4
    style U1 fill:#fff9c4
```

### RESTRICT (Protect Critical Data)

```mermaid
graph LR
    subgraph "Should RESTRICT"
        C3[Courier] -->|RESTRICT| SAL[Salaries]
        C3 -->|RESTRICT| LOAN[Loans]

        U2[User] -->|RESTRICT| TIX[Tickets.created_by]
        U2 -->|RESTRICT| REP[TicketReplies.user_id]
    end

    style C3 fill:#ffebee
    style U2 fill:#ffebee
```

### ⚠️ Missing ondelete (BROKEN)

```mermaid
graph LR
    subgraph "Missing ondelete - WILL FAIL"
        C4[Courier] -.-|❌ NO ONDELETE| SAL2[Salaries]
        C4 -.-|❌ NO ONDELETE| LOAN2[Loans]
        C4 -.-|❌ NO ONDELETE| LEA[Leaves]
        C4 -.-|❌ NO ONDELETE| ATT2[Attendance]
        C4 -.-|❌ NO ONDELETE| ASS[Assets]
        C4 -.-|❌ NO ONDELETE| BON[Bonuses]
        C4 -.-|❌ NO ONDELETE| DEL2[Deliveries]
        C4 -.-|❌ NO ONDELETE| COD2[COD]

        BUILD2[Building] -.-|❌ NO ONDELETE| ROOM2[Rooms]
        ROOM2 -.-|❌ NO ONDELETE| BED2[Beds]
        BED2 -.-|❌ NO ONDELETE| ALL2[Allocations]
    end

    style C4 fill:#f44336
    style BUILD2 fill:#f44336
    style ROOM2 fill:#f44336
```

---

## Multi-Tenant Architecture

```mermaid
graph TB
    subgraph "Organization 1"
        O1[Organization 1]
        C1[Couriers]
        V1[Vehicles]
        D1[Deliveries]
        S1[Salaries]

        O1 -.organization_id.-> C1
        O1 -.organization_id.-> V1
        O1 -.organization_id.-> D1
        O1 -.organization_id.-> S1
    end

    subgraph "Organization 2"
        O2[Organization 2]
        C2[Couriers]
        V2[Vehicles]
        D2[Deliveries]
        S2[Salaries]

        O2 -.organization_id.-> C2
        O2 -.organization_id.-> V2
        O2 -.organization_id.-> D2
        O2 -.organization_id.-> S2
    end

    subgraph "Shared Resources"
        USERS[Users]
        ROLES[Roles]
        PERMS[Permissions]
    end

    O1 --> USERS
    O2 --> USERS

    style O1 fill:#e1f5ff
    style O2 fill:#fff4e6
```

### Multi-Tenant Query Pattern

**Every query must filter by organization_id:**

```sql
-- CORRECT:
SELECT * FROM couriers
WHERE organization_id = :current_org_id
  AND status = 'ACTIVE';

-- WRONG (will see other orgs' data):
SELECT * FROM couriers
WHERE status = 'ACTIVE';
```

**Missing Composite Indexes:**
```sql
-- Needed in ALL tenant-aware tables:
CREATE INDEX ix_couriers_org_created
ON couriers(organization_id, created_at);

CREATE INDEX ix_vehicles_org_created
ON vehicles(organization_id, created_at);

-- etc.
```

---

## Data Flow Diagrams

### Courier Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Onboarding
    Onboarding --> Active: Complete Onboarding
    Active --> OnLeave: Submit Leave
    OnLeave --> Active: Return from Leave
    Active --> Suspended: Violation/Issue
    Suspended --> Active: Resolve Issue
    Active --> Terminated: Resignation/Termination
    Terminated --> [*]

    note right of Onboarding
        Creates:
        - Courier record
        - Documents
        - Initial Assets
    end note

    note right of Active
        Daily:
        - Attendance
        - Deliveries
        - Vehicle Logs

        Monthly:
        - Salary
        - Bonuses
    end note

    note right of Terminated
        ⚠️ CANNOT DELETE if has:
        - Salary records (RESTRICT)
        - Outstanding Loans (RESTRICT)

        ✅ CAN DELETE:
        - Cascades: Leaves, Attendance
        - Sets NULL: Deliveries, COD
    end note
```

### Vehicle Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Active
    Active --> Maintenance: Schedule Service
    Maintenance --> Active: Service Complete
    Active --> Repair: Breakdown/Accident
    Repair --> Active: Repair Complete
    Active --> Inactive: Temporary Stop
    Inactive --> Active: Reactivate
    Active --> Retired: End of Life
    Retired --> [*]

    note right of Active
        Generates:
        - Vehicle Logs
        - Fuel Logs
        - Inspections
    end note

    note right of Repair
        Creates:
        - Accident Log
        - Maintenance Record
    end note

    note right of Retired
        ✅ CAN DELETE:
        - Cascades all logs
        - Sets NULL current assignments
    end note
```

---

## Index Strategy Visualization

### Before Optimization (Slow)

```mermaid
graph LR
    Q1[Query: Get active assignments<br/>for courier] --> SEQ1[Sequential Scan<br/>~500ms]
    Q2[Query: Get courier's<br/>salary for month] --> SEQ2[Sequential Scan<br/>~300ms]
    Q3[Query: Get vehicle<br/>maintenance history] --> SEQ3[Sequential Scan<br/>~400ms]

    style SEQ1 fill:#ffcdd2
    style SEQ2 fill:#ffcdd2
    style SEQ3 fill:#ffcdd2
```

### After Optimization (Fast)

```mermaid
graph LR
    Q1[Query: Get active assignments<br/>for courier] --> IDX1[Index Scan<br/>ix_assignment_courier_status<br/>~5ms ✓]
    Q2[Query: Get courier's<br/>salary for month] --> IDX2[Index Scan<br/>ix_salary_courier_period<br/>~3ms ✓]
    Q3[Query: Get vehicle<br/>maintenance history] --> IDX3[Index Scan<br/>ix_maintenance_vehicle_status<br/>~4ms ✓]

    style IDX1 fill:#c8e6c9
    style IDX2 fill:#c8e6c9
    style IDX3 fill:#c8e6c9
```

---

## Testing Strategy

### Delete Cascade Testing

```mermaid
graph TB
    subgraph "Test: Delete Courier"
        START[Create Test Courier] --> ADD1[Add Leaves]
        ADD1 --> ADD2[Add Attendance]
        ADD2 --> ADD3[Add Vehicle Assignment]
        ADD3 --> ADD4[Add Deliveries]
        ADD4 --> ADD5[Add Salary]
        ADD5 --> DELETE[DELETE Courier]

        DELETE --> CHECK1{Leaves Deleted?}
        CHECK1 -->|YES| CHECK2{Attendance Deleted?}
        CHECK2 -->|YES| CHECK3{Assignments Deleted?}
        CHECK3 -->|YES| CHECK4{Deliveries.courier_id = NULL?}
        CHECK4 -->|YES| CHECK5{Salary Prevents Delete?}
        CHECK5 -->|YES| PASS[✓ Test Pass]
        CHECK5 -->|NO| FAIL[✗ Test Fail]
        CHECK1 -->|NO| FAIL
        CHECK2 -->|NO| FAIL
        CHECK3 -->|NO| FAIL
        CHECK4 -->|NO| FAIL
    end

    style PASS fill:#c8e6c9
    style FAIL fill:#ffcdd2
```

---

## Summary: Relationship Health

| Domain | Total Models | ✅ Good | ⚠️ Issues | 🔴 Critical |
|--------|--------------|---------|-----------|-------------|
| **Core** | 8 | 6 | 1 | 1 |
| **Fleet** | 9 | 3 | 2 | 4 |
| **HR** | 6 | 0 | 0 | 6 |
| **Accommodation** | 4 | 1 | 0 | 3 |
| **Operations** | 6 | 2 | 0 | 4 |
| **Support** | 6 | 2 | 1 | 3 |
| **TOTAL** | 39 | 14 (36%) | 4 (10%) | 21 (54%) |

**Critical Issue Breakdown:**
- Missing `ondelete`: 17 tables (44%)
- Missing FK constraints: 1 table (2%)
- Circular references: 1 pair (3%)
- Type inconsistencies: 3 columns (2%)
- Conflicting constraints: 3 tables (8%)

---

**Report Generated:** 2025-12-07
**Database Architect:** AI Agent
**Rendering:** Compatible with GitHub, Notion, Mermaid Live Editor
