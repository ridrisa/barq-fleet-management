# Row-Level Security (RLS) Policy Optimization Guide

## Overview

This document provides optimized RLS policies for the BARQ Fleet Management system, ensuring both security and performance.

## Key Principles

1. **Index RLS Filter Columns**: Ensure `organization_id` is indexed on ALL tenant tables
2. **Minimize Policy Complexity**: Keep RLS policies simple for better performance
3. **Use Session Variables**: Leverage PostgreSQL session variables for context
4. **Test Performance**: Always EXPLAIN ANALYZE queries with RLS enabled
5. **Consistent Implementation**: Apply same pattern across all tenant tables

## Session Context Setup

```sql
-- Set in application code for each request
SET app.current_org_id = '123';
SET app.current_user_id = '456';
SET app.is_superuser = 'false';
```

## Core RLS Policies

### 1. Couriers Table

```sql
-- Enable RLS
ALTER TABLE couriers ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS couriers_tenant_isolation ON couriers;
DROP POLICY IF EXISTS couriers_superuser_access ON couriers;

-- Policy 1: Tenant isolation for regular users
CREATE POLICY couriers_tenant_isolation ON couriers
  FOR ALL
  TO authenticated_users
  USING (
    organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER)
  );

-- Policy 2: Superuser access (bypass tenant filter)
CREATE POLICY couriers_superuser_access ON couriers
  FOR ALL
  TO authenticated_users
  USING (
    current_setting('app.is_superuser', true) = 'true'
  );

-- Index for performance (should already exist from TenantMixin)
CREATE INDEX IF NOT EXISTS idx_couriers_org_id ON couriers(organization_id);

-- Verify index usage with EXPLAIN
EXPLAIN ANALYZE
SELECT * FROM couriers
WHERE organization_id = 1;
```

### 2. Vehicles Table

```sql
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS vehicles_tenant_isolation ON vehicles;
DROP POLICY IF EXISTS vehicles_superuser_access ON vehicles;

CREATE POLICY vehicles_tenant_isolation ON vehicles
  FOR ALL
  TO authenticated_users
  USING (
    organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER)
  );

CREATE POLICY vehicles_superuser_access ON vehicles
  FOR ALL
  TO authenticated_users
  USING (
    current_setting('app.is_superuser', true) = 'true'
  );

CREATE INDEX IF NOT EXISTS idx_vehicles_org_id ON vehicles(organization_id);
```

### 3. Deliveries Table

```sql
ALTER TABLE deliveries ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS deliveries_tenant_isolation ON deliveries;
DROP POLICY IF EXISTS deliveries_superuser_access ON deliveries;

CREATE POLICY deliveries_tenant_isolation ON deliveries
  FOR ALL
  TO authenticated_users
  USING (
    organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER)
  );

CREATE POLICY deliveries_superuser_access ON deliveries
  FOR ALL
  TO authenticated_users
  USING (
    current_setting('app.is_superuser', true) = 'true'
  );

CREATE INDEX IF NOT EXISTS idx_deliveries_org_id ON deliveries(organization_id);
```

### 4. Courier Vehicle Assignments

```sql
ALTER TABLE courier_vehicle_assignments ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS assignments_tenant_isolation ON courier_vehicle_assignments;
DROP POLICY IF EXISTS assignments_superuser_access ON courier_vehicle_assignments;

CREATE POLICY assignments_tenant_isolation ON courier_vehicle_assignments
  FOR ALL
  TO authenticated_users
  USING (
    organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER)
  );

CREATE POLICY assignments_superuser_access ON courier_vehicle_assignments
  FOR ALL
  TO authenticated_users
  USING (
    current_setting('app.is_superuser', true) = 'true'
  );

CREATE INDEX IF NOT EXISTS idx_assignments_org_id ON courier_vehicle_assignments(organization_id);
```

### 5. HR Tables (Salaries, Attendance, Leaves, Loans)

```sql
-- Salaries
ALTER TABLE salaries ENABLE ROW LEVEL SECURITY;
CREATE POLICY salaries_tenant_isolation ON salaries
  FOR ALL TO authenticated_users
  USING (organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER));
CREATE POLICY salaries_superuser_access ON salaries
  FOR ALL TO authenticated_users
  USING (current_setting('app.is_superuser', true) = 'true');
CREATE INDEX IF NOT EXISTS idx_salaries_org_id ON salaries(organization_id);

-- Attendance
ALTER TABLE attendance ENABLE ROW LEVEL SECURITY;
CREATE POLICY attendance_tenant_isolation ON attendance
  FOR ALL TO authenticated_users
  USING (organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER));
CREATE POLICY attendance_superuser_access ON attendance
  FOR ALL TO authenticated_users
  USING (current_setting('app.is_superuser', true) = 'true');
CREATE INDEX IF NOT EXISTS idx_attendance_org_id ON attendance(organization_id);

-- Leaves
ALTER TABLE leaves ENABLE ROW LEVEL SECURITY;
CREATE POLICY leaves_tenant_isolation ON leaves
  FOR ALL TO authenticated_users
  USING (organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER));
CREATE POLICY leaves_superuser_access ON leaves
  FOR ALL TO authenticated_users
  USING (current_setting('app.is_superuser', true) = 'true');
CREATE INDEX IF NOT EXISTS idx_leaves_org_id ON leaves(organization_id);

-- Loans
ALTER TABLE loans ENABLE ROW LEVEL SECURITY;
CREATE POLICY loans_tenant_isolation ON loans
  FOR ALL TO authenticated_users
  USING (organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER));
CREATE POLICY loans_superuser_access ON loans
  FOR ALL TO authenticated_users
  USING (current_setting('app.is_superuser', true) = 'true');
CREATE INDEX IF NOT EXISTS idx_loans_org_id ON loans(organization_id);
```

### 6. COD Transactions

```sql
ALTER TABLE cod_transactions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS cod_tenant_isolation ON cod_transactions;
DROP POLICY IF EXISTS cod_superuser_access ON cod_transactions;

CREATE POLICY cod_tenant_isolation ON cod_transactions
  FOR ALL
  TO authenticated_users
  USING (
    organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER)
  );

CREATE POLICY cod_superuser_access ON cod_transactions
  FOR ALL
  TO authenticated_users
  USING (
    current_setting('app.is_superuser', true) = 'true'
  );

CREATE INDEX IF NOT EXISTS idx_cod_org_id ON cod_transactions(organization_id);
```

## Performance Testing

### Test RLS Policy Performance

```sql
-- Set session context
SET app.current_org_id = '1';
SET app.is_superuser = 'false';

-- Test query with EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT c.*, v.plate_number
FROM couriers c
LEFT JOIN vehicles v ON c.current_vehicle_id = v.id
WHERE c.status = 'ACTIVE'
LIMIT 100;

-- Look for:
-- 1. "Index Scan" or "Bitmap Index Scan" on organization_id
-- 2. Low "actual time" values
-- 3. No "Seq Scan" on large tables
```

### Expected Output (Good Performance)

```
Index Scan using idx_couriers_org_status on couriers c  (cost=0.42..123.45 rows=50 width=500) (actual time=0.032..0.156 rows=50 loops=1)
  Index Cond: ((organization_id = 1) AND (status = 'ACTIVE'::courier_status))
```

### Bad Performance Indicator

```
Seq Scan on couriers c  (cost=0.00..10000.00 rows=5000 width=500) (actual time=50.234..150.456 rows=50 loops=1)
  Filter: (organization_id = 1)
  Rows Removed by Filter: 49950
```

## Application Integration

### FastAPI Dependency

```python
# In app/core/dependencies.py

from sqlalchemy import text
from sqlalchemy.orm import Session

def get_tenant_db(
    organization_id: int,
    is_superuser: bool = False
) -> Generator[Session, None, None]:
    """
    Get database session with RLS context
    """
    db = db_manager.create_session()
    try:
        # CRITICAL: Use parameterized queries to prevent SQL injection
        db.execute(
            text("SET app.current_org_id = :org_id"),
            {"org_id": str(int(organization_id))}
        )
        db.execute(
            text("SET app.is_superuser = :is_super"),
            {"is_super": str(is_superuser).lower()}
        )
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        # Reset context to prevent leaking to connection pool
        try:
            db.execute(text("RESET app.current_org_id"))
            db.execute(text("RESET app.is_superuser"))
        except:
            pass
        db.close()
```

### Usage in Endpoints

```python
@router.get("/couriers")
async def get_couriers(
    db: Session = Depends(get_tenant_db),
    current_user: User = Depends(get_current_user)
):
    # RLS automatically filters by organization_id
    couriers = db.query(Courier).filter(Courier.status == 'ACTIVE').all()
    return couriers
```

## Monitoring & Maintenance

### 1. Check RLS is Enabled

```sql
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN (
        'couriers', 'vehicles', 'deliveries',
        'courier_vehicle_assignments', 'salaries',
        'attendance', 'leaves', 'loans', 'cod_transactions'
    )
ORDER BY tablename;
```

### 2. List All RLS Policies

```sql
SELECT
    schemaname,
    tablename,
    policyname,
    roles,
    cmd,
    qual  -- USING clause
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

### 3. Verify Index Usage

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND indexname LIKE '%org_id%'
ORDER BY tablename;
```

## Common Pitfalls

### ❌ Don't Do This

```sql
-- BAD: Complex subqueries in RLS policies
CREATE POLICY bad_policy ON couriers
  USING (
    organization_id IN (
      SELECT org_id FROM user_organizations WHERE user_id = current_user_id()
    )
  );

-- PROBLEM: Subquery runs for EVERY row check - very slow!
```

### ✅ Do This Instead

```sql
-- GOOD: Simple comparison with session variable
CREATE POLICY good_policy ON couriers
  USING (
    organization_id = CAST(current_setting('app.current_org_id', true) AS INTEGER)
  );

-- BENEFIT: Direct index lookup - very fast!
```

### ❌ Don't Do This

```python
# BAD: String interpolation (SQL injection risk)
db.execute(f"SET app.current_org_id = '{org_id}'")
```

### ✅ Do This Instead

```python
# GOOD: Parameterized query
db.execute(
    text("SET app.current_org_id = :org_id"),
    {"org_id": str(int(org_id))}
)
```

## Performance Benchmarks

Expected query performance with RLS:

| Operation | Without RLS | With RLS (Optimized) | Overhead |
|-----------|-------------|----------------------|----------|
| Single courier lookup | 0.5ms | 0.6ms | +20% |
| List 100 couriers | 5ms | 6ms | +20% |
| Dashboard stats | 50ms | 55ms | +10% |
| Bulk insert (100 records) | 200ms | 210ms | +5% |

**Target**: RLS overhead should be < 25% for most queries.

## Troubleshooting

### Query is slow despite RLS

1. Check if index exists: `\d+ table_name`
2. Verify index is used: `EXPLAIN ANALYZE query`
3. Update table statistics: `ANALYZE table_name;`
4. Consider partial indexes for filtered queries

### RLS not filtering correctly

1. Verify session variable is set: `SHOW app.current_org_id;`
2. Check policy is enabled: `SELECT * FROM pg_policies WHERE tablename = 'your_table';`
3. Verify user role has policy applied
4. Test with `SET app.current_org_id = 'X'; SELECT * FROM table;`

## Automation Script

```bash
#!/bin/bash
# apply_rls_policies.sh

psql -U postgres -d barq_fleet << EOF
-- Enable RLS and create policies for all tenant tables
\i sql/rls_policies/01_couriers.sql
\i sql/rls_policies/02_vehicles.sql
\i sql/rls_policies/03_deliveries.sql
\i sql/rls_policies/04_assignments.sql
\i sql/rls_policies/05_hr_tables.sql
\i sql/rls_policies/06_cod.sql

-- Verify
\i sql/rls_policies/verify.sql
EOF
```

## Next Steps

1. Apply RLS policies using the migration
2. Test with EXPLAIN ANALYZE
3. Monitor query performance in production
4. Adjust indexes based on actual query patterns
5. Document any custom RLS policies for specific use cases
