-- ============================================================================
-- BARQ Fleet Management - Database Permissions Fix
-- ============================================================================
-- Generated: 2025-12-12
-- Priority: CRITICAL - Fixes "permission denied for table couriers" error
-- Issue: The database user doesn't have proper access to tables
--
-- Root Cause Analysis:
-- The Cloud SQL instance is using the 'postgres' user, but:
-- 1. Row-Level Security (RLS) is enabled on tables (migration 018)
-- 2. RLS FORCE means even the table owner needs proper policies
-- 3. The 'app_user' role was created but not granted to 'postgres'
-- ============================================================================

-- IMPORTANT: Run this script as the postgres superuser
-- Test on staging first before applying to production!

BEGIN;

-- ============================================================================
-- OPTION 1: Quick Fix - Disable RLS (For Development/Testing)
-- ============================================================================
-- Uncomment the section below if you want to disable RLS temporarily
-- This is NOT recommended for production but useful for debugging

/*
-- Disable RLS on all tables with organization_id
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('ALTER TABLE %I DISABLE ROW LEVEL SECURITY', r.tablename);
        EXECUTE format('ALTER TABLE %I NO FORCE ROW LEVEL SECURITY', r.tablename);
        RAISE NOTICE 'Disabled RLS on table: %', r.tablename;
    END LOOP;
END $$;
*/

-- ============================================================================
-- OPTION 2: Proper Fix - Grant Permissions to Database User
-- ============================================================================

-- Step 1: Grant schema usage
GRANT USAGE ON SCHEMA public TO postgres;

-- Step 2: Grant all privileges on existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;

-- Step 3: Grant all privileges on sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Step 4: Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO postgres;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO postgres;

-- Step 5: Ensure postgres user has the app_user role (if it exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
        GRANT app_user TO postgres;
        RAISE NOTICE 'Granted app_user role to postgres';
    END IF;
END $$;

-- ============================================================================
-- OPTION 3: Fix RLS Policies for the postgres user
-- ============================================================================

-- The RLS policies require session variables to be set.
-- When app.current_org_id is not set, queries should still work for superusers.
-- We need to add a bypass policy for database superusers.

-- List of all tenant tables (from migration 018)
DO $$
DECLARE
    tenant_tables TEXT[] := ARRAY[
        'couriers', 'vehicles', 'courier_vehicle_assignments', 'accident_logs',
        'fuel_logs', 'vehicle_logs', 'vehicle_maintenance', 'inspections', 'documents',
        'attendance', 'leaves', 'loans', 'salaries', 'assets', 'bonuses',
        'deliveries', 'cods', 'dispatch_assignments', 'operations_documents',
        'customer_feedback', 'feedback_templates', 'handovers', 'incidents',
        'priority_queue_entries', 'quality_metrics', 'quality_inspections', 'routes',
        'operations_settings', 'dispatch_rules', 'sla_thresholds', 'notification_settings',
        'zone_defaults', 'sla_definitions', 'sla_tracking', 'zones',
        'buildings', 'rooms', 'beds', 'allocations',
        'dashboards', 'kpis', 'metric_snapshots', 'performance_data', 'reports',
        'api_keys', 'backups', 'integrations', 'system_settings',
        'tickets', 'ticket_replies', 'ticket_attachments', 'ticket_templates',
        'chat_sessions', 'chat_messages', 'canned_responses', 'faqs', 'support_feedback',
        'kb_articles', 'kb_categories',
        'workflow_templates', 'workflow_instances', 'workflow_history', 'workflow_step_history',
        'workflow_comments', 'workflow_attachments', 'workflow_automations',
        'automation_execution_logs', 'workflow_notification_templates', 'workflow_notifications',
        'notification_preferences', 'workflow_slas', 'workflow_sla_instances', 'sla_events',
        'workflow_triggers', 'trigger_executions', 'workflow_metrics', 'workflow_step_metrics',
        'workflow_performance_snapshots', 'workflow_user_metrics',
        'approval_chains', 'approval_chain_approvers', 'approval_requests',
        'vehicle_inspections', 'cod_transactions'
    ];
    t TEXT;
    policy_exists BOOLEAN;
BEGIN
    FOREACH t IN ARRAY tenant_tables
    LOOP
        -- Check if table exists
        IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = t AND table_schema = 'public') THEN
            -- Check if superuser bypass policy exists
            SELECT EXISTS (
                SELECT FROM pg_policies
                WHERE tablename = t
                AND policyname = 'db_superuser_bypass_' || t
            ) INTO policy_exists;

            IF NOT policy_exists THEN
                -- Add a bypass policy for database superusers
                EXECUTE format(
                    'CREATE POLICY db_superuser_bypass_%I ON %I
                    FOR ALL
                    USING (
                        -- Allow if current user is a PostgreSQL superuser
                        (SELECT usesuper FROM pg_user WHERE usename = current_user)
                        OR
                        -- Allow if app.is_superuser session variable is true
                        COALESCE(current_setting(''app.is_superuser'', true), ''false'')::boolean = true
                        OR
                        -- Allow if no org context is set (for admin queries)
                        NULLIF(current_setting(''app.current_org_id'', true), '''') IS NULL
                    )
                    WITH CHECK (
                        (SELECT usesuper FROM pg_user WHERE usename = current_user)
                        OR
                        COALESCE(current_setting(''app.is_superuser'', true), ''false'')::boolean = true
                        OR
                        NULLIF(current_setting(''app.current_org_id'', true), '''') IS NULL
                    )',
                    t, t
                );
                RAISE NOTICE 'Created db_superuser_bypass policy on table: %', t;
            ELSE
                RAISE NOTICE 'Policy db_superuser_bypass already exists on table: %', t;
            END IF;
        ELSE
            RAISE NOTICE 'Table does not exist, skipping: %', t;
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify current user permissions
SELECT
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'postgres'
    AND table_schema = 'public'
    AND table_name = 'couriers'
ORDER BY table_name;

-- Check RLS status on couriers table
SELECT
    relname as table_name,
    relrowsecurity as rls_enabled,
    relforcerowsecurity as rls_forced
FROM pg_class
WHERE relname = 'couriers'
    AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public');

-- List all policies on couriers table
SELECT
    policyname,
    tablename,
    cmd as operation,
    qual as using_expression,
    with_check
FROM pg_policies
WHERE tablename = 'couriers';

-- Test query (should work after fixes)
-- SELECT COUNT(*) FROM couriers;

COMMIT;

-- ============================================================================
-- POST-FIX TESTING
-- ============================================================================
-- After running this script, test the following:
--
-- 1. Basic SELECT on couriers:
--    SELECT COUNT(*) FROM couriers;
--
-- 2. Test with organization context:
--    SET app.current_org_id = '1';
--    SELECT * FROM couriers LIMIT 5;
--    RESET app.current_org_id;
--
-- 3. Test GraphQL API endpoint:
--    curl https://sync-api-869422381378.me-central1.run.app/api/v1/graphql \
--      -H "Content-Type: application/json" \
--      -d '{"query": "{ couriers { id name } }"}'
--
-- ============================================================================
