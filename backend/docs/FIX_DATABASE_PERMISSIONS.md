# Fixing Database Permissions for BARQ Fleet Production

## Problem Description

The Cloud SQL database returns the following error when accessing the `couriers` table:

```
permission denied for table couriers
```

## Root Cause Analysis

After reviewing the codebase, the issue is caused by the interaction of several factors:

### 1. Row-Level Security (RLS) is Enabled

Migration `018_enable_row_level_security.py` enables RLS on all tenant tables including `couriers`:

```python
# RLS is enabled AND forced for all tables
connection.execute(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
connection.execute(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY")
```

When `FORCE ROW LEVEL SECURITY` is set, even the table owner must satisfy the RLS policies.

### 2. RLS Policies Require Session Variables

The RLS policies expect session variables to be set:

```sql
CREATE POLICY tenant_isolation_couriers ON couriers
FOR ALL
USING (
    organization_id = COALESCE(
        NULLIF(current_setting('app.current_org_id', true), '')::integer,
        organization_id
    )
)
```

When `app.current_org_id` is not set, the policy evaluates to `organization_id = organization_id`, which should work, but the `superuser_bypass` policy requires `app.is_superuser = 'true'`.

### 3. Database Connection Details

From `cloudbuild.yaml`:
- **User**: `postgres`
- **Database**: `barq_fleet`
- **Cloud SQL Instance**: `barqdps:me-central1:barq-postgres-staging`

The `postgres` user is a superuser, but PostgreSQL superuser status is not being checked in the RLS policies.

## Solution

### Quick Fix (Apply via Cloud Build)

Run the pre-built Cloud Build configuration:

```bash
cd /Users/ramiz_new/Desktop/Projects/barq-fleet-clean
gcloud builds submit --config=cloudbuild.fix-permissions.yaml --project=barqdps .
```

This will:
1. Connect to Cloud SQL using the proxy
2. Grant all necessary privileges to the postgres user
3. Add bypass policies for database superusers
4. Verify the fix works

### Manual Fix (Via Cloud SQL Console)

If you prefer to run commands manually:

#### Step 1: Connect to Cloud SQL

1. Go to Google Cloud Console > SQL > barq-postgres-staging
2. Click "Connect using Cloud Shell" or use Cloud SQL Proxy locally
3. Connect with: `psql -U postgres -d barq_fleet`

#### Step 2: Run the Permission Fix Script

```sql
-- Grant all privileges
GRANT USAGE ON SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Add bypass policy for the couriers table
CREATE POLICY db_superuser_bypass_couriers ON couriers
FOR ALL
USING (
    (SELECT usesuper FROM pg_user WHERE usename = current_user)
    OR COALESCE(current_setting('app.is_superuser', true), 'false')::boolean = true
    OR NULLIF(current_setting('app.current_org_id', true), '') IS NULL
)
WITH CHECK (
    (SELECT usesuper FROM pg_user WHERE usename = current_user)
    OR COALESCE(current_setting('app.is_superuser', true), 'false')::boolean = true
    OR NULLIF(current_setting('app.current_org_id', true), '') IS NULL
);
```

#### Step 3: Verify the Fix

```sql
-- This should return a count now
SELECT COUNT(*) FROM couriers;

-- Check policies
SELECT policyname, cmd FROM pg_policies WHERE tablename = 'couriers';
```

### Alternative: Disable RLS (Development Only)

For development/testing, you can temporarily disable RLS:

```sql
ALTER TABLE couriers DISABLE ROW LEVEL SECURITY;
ALTER TABLE couriers NO FORCE ROW LEVEL SECURITY;
```

**WARNING**: Do not do this in production as it removes tenant isolation.

## Files Created

1. **SQL Script**: `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/scripts/fix_database_permissions.sql`
   - Complete SQL script with all fixes
   - Includes verification queries
   - Can be run manually via psql

2. **Cloud Build Config**: `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/cloudbuild.fix-permissions.yaml`
   - Automated fix via Cloud Build
   - Handles Cloud SQL proxy setup
   - Includes verification steps

## Verification Commands

After applying the fix, verify with these commands:

### Test via psql

```sql
-- Should return row count
SELECT COUNT(*) FROM couriers;

-- Should show bypass policy
SELECT policyname FROM pg_policies WHERE tablename = 'couriers';

-- Test with explicit context
SET app.current_org_id = '1';
SELECT * FROM couriers LIMIT 5;
RESET app.current_org_id;
```

### Test via API

```bash
# Test the GraphQL endpoint
curl -X POST https://sync-api-869422381378.me-central1.run.app/api/v1/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{"query": "{ couriers(limit: 5) { id name status } }"}'
```

## Prevention

To prevent this issue in future deployments:

1. **Update Migration 018**: Add database superuser bypass to the RLS policies
2. **Add to CI/CD Pipeline**: Include permission verification in the deployment smoke tests
3. **Document RLS Requirements**: Ensure developers understand the session variable requirements

## Related Files

- `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/alembic/versions/018_enable_row_level_security.py` - RLS migration
- `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/backend/app/core/database.py` - Database configuration
- `/Users/ramiz_new/Desktop/Projects/barq-fleet-clean/cloudbuild.yaml` - Production deployment config

## Support

If the issue persists after applying these fixes:

1. Check Cloud SQL logs for detailed error messages
2. Verify the correct database instance is being connected
3. Check if there are any pending migrations: `alembic current`
4. Review the application logs in Cloud Run for connection details
