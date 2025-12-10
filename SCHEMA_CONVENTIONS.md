# Database Schema Conventions

## Schema Roles

### `public` - Canonical Operational Model
- **Purpose**: Source of truth for all domain entities
- **RLS**: Enabled and enforced for multi-tenancy
- **Tables**: couriers, vehicles, orders, salaries, organizations, users, etc.
- **Enums**: All shared enums defined here (courierstatus, vehiclestatus, etc.)

### `barq` - Overlay / Infrastructure Layer
- **Purpose**: Admin workflows, auditing, CDC, HR processes
- **RLS**: Not directly applied (access via joins to public tables)
- **Tables**:
  - `audit_logs` - Change tracking
  - `cdc_queue` - Change data capture outbox
  - `couriers` / `vehicles` - Legacy overlay (FK to public)
  - `leave_requests` / `leave_approvals` - HR workflows
  - `workflow_instances` - Workflow engine state
  - `vehicle_assignments` - Assignment tracking

## Key Constraints

### Identity Mapping (barq → public)
```
barq.couriers.barq_id        → public.couriers.barq_id
barq.vehicles.plate_number   → public.vehicles.plate_number
```

### Shared Enums
All status/type columns use `public.*` enums:
- `courierstatus`, `sponsorshipstatus`
- `vehiclestatus`, `vehicletype`

## Rules
1. **Never treat `barq` as source of truth** - it's an overlay
2. **New domain entities go in `public`** with RLS
3. **Infrastructure/audit/workflow goes in `barq`**
4. **Always use shared enums** - no varchar status fields
