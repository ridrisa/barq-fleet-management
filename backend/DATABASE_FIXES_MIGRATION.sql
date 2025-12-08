-- ============================================================================
-- BARQ Fleet Management - Critical Database Fixes
-- ============================================================================
-- Generated: 2025-12-07
-- Priority: CRITICAL - Must be applied before production deployment
-- Estimated Time: 2-3 hours
-- Risk: Medium (backup database before running)
-- ============================================================================

-- IMPORTANT: Test all migrations on staging environment first!
-- Backup database before running:
-- pg_dump -h localhost -U postgres -d barq_fleet > backup_before_migration.sql

BEGIN;

-- ============================================================================
-- PHASE 1: Fix Missing ondelete Behaviors
-- ============================================================================

-- FIX #1: fuel_logs.courier_id
-- Current: No ondelete behavior
-- Fix: SET NULL (preserve fuel log even if courier deleted)
ALTER TABLE fuel_logs
DROP CONSTRAINT IF EXISTS fuel_logs_courier_id_fkey,
ADD CONSTRAINT fuel_logs_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE SET NULL;

-- FIX #2: salaries.courier_id
-- Current: No ondelete behavior
-- Fix: RESTRICT (cannot delete courier with salary records - audit requirement)
ALTER TABLE salaries
DROP CONSTRAINT IF EXISTS salaries_courier_id_fkey,
ADD CONSTRAINT salaries_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE RESTRICT;

-- FIX #3: loans.courier_id
-- Current: No ondelete behavior
-- Fix: RESTRICT (cannot delete courier with outstanding loans)
ALTER TABLE loans
DROP CONSTRAINT IF EXISTS loans_courier_id_fkey,
ADD CONSTRAINT loans_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE RESTRICT;

-- FIX #4: leaves.courier_id
-- Current: No ondelete behavior
-- Fix: CASCADE (delete leave records with courier)
ALTER TABLE leaves
DROP CONSTRAINT IF EXISTS leaves_courier_id_fkey,
ADD CONSTRAINT leaves_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE CASCADE;

-- FIX #5: attendance.courier_id
-- Current: No ondelete behavior
-- Fix: CASCADE (delete attendance records with courier)
ALTER TABLE attendance
DROP CONSTRAINT IF EXISTS attendance_courier_id_fkey,
ADD CONSTRAINT attendance_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE CASCADE;

-- FIX #6: assets.courier_id
-- Current: No ondelete behavior
-- Fix: SET NULL (keep asset history, mark courier as NULL)
-- First, make courier_id nullable
ALTER TABLE assets
ALTER COLUMN courier_id DROP NOT NULL;

ALTER TABLE assets
DROP CONSTRAINT IF EXISTS assets_courier_id_fkey,
ADD CONSTRAINT assets_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE SET NULL;

-- FIX #7: bonuses.courier_id
-- Current: No ondelete behavior
-- Fix: CASCADE (delete bonuses with courier)
ALTER TABLE bonuses
DROP CONSTRAINT IF EXISTS bonuses_courier_id_fkey,
ADD CONSTRAINT bonuses_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE CASCADE;

-- FIX #8: rooms.building_id
-- Current: No ondelete behavior
-- Fix: CASCADE (delete rooms when building deleted)
ALTER TABLE rooms
DROP CONSTRAINT IF EXISTS rooms_building_id_fkey,
ADD CONSTRAINT rooms_building_id_fkey
    FOREIGN KEY (building_id)
    REFERENCES buildings(id)
    ON DELETE CASCADE;

-- FIX #9: beds.room_id
-- Current: No ondelete behavior
-- Fix: CASCADE (delete beds when room deleted)
ALTER TABLE beds
DROP CONSTRAINT IF EXISTS beds_room_id_fkey,
ADD CONSTRAINT beds_room_id_fkey
    FOREIGN KEY (room_id)
    REFERENCES rooms(id)
    ON DELETE CASCADE;

-- FIX #10: allocations.courier_id
-- Current: No ondelete behavior
-- Fix: CASCADE (delete allocation when courier deleted)
ALTER TABLE allocations
DROP CONSTRAINT IF EXISTS allocations_courier_id_fkey,
ADD CONSTRAINT allocations_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE CASCADE;

-- FIX #11: allocations.bed_id
-- Current: No ondelete behavior
-- Fix: CASCADE (delete allocation when bed deleted)
ALTER TABLE allocations
DROP CONSTRAINT IF EXISTS allocations_bed_id_fkey,
ADD CONSTRAINT allocations_bed_id_fkey
    FOREIGN KEY (bed_id)
    REFERENCES beds(id)
    ON DELETE CASCADE;

-- FIX #12: deliveries.courier_id
-- Current: No ondelete, NOT NULL column
-- Fix: SET NULL (preserve delivery records)
-- First, make courier_id nullable
ALTER TABLE deliveries
ALTER COLUMN courier_id DROP NOT NULL;

ALTER TABLE deliveries
DROP CONSTRAINT IF EXISTS deliveries_courier_id_fkey,
ADD CONSTRAINT deliveries_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE SET NULL;

-- FIX #13: cod_transactions.courier_id
-- Current: No ondelete, NOT NULL column
-- Fix: SET NULL (preserve COD records for financial audit)
-- First, make courier_id nullable
ALTER TABLE cod_transactions
ALTER COLUMN courier_id DROP NOT NULL;

ALTER TABLE cod_transactions
DROP CONSTRAINT IF EXISTS cod_transactions_courier_id_fkey,
ADD CONSTRAINT cod_transactions_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE SET NULL;

-- FIX #14: incidents.courier_id
-- Current: No ondelete
-- Fix: SET NULL (preserve incident records)
ALTER TABLE incidents
DROP CONSTRAINT IF EXISTS incidents_courier_id_fkey,
ADD CONSTRAINT incidents_courier_id_fkey
    FOREIGN KEY (courier_id)
    REFERENCES couriers(id)
    ON DELETE SET NULL;

-- FIX #15: incidents.vehicle_id
-- Current: No ondelete
-- Fix: SET NULL (preserve incident records)
ALTER TABLE incidents
DROP CONSTRAINT IF EXISTS incidents_vehicle_id_fkey,
ADD CONSTRAINT incidents_vehicle_id_fkey
    FOREIGN KEY (vehicle_id)
    REFERENCES vehicles(id)
    ON DELETE SET NULL;

-- FIX #16: audit_logs.user_id
-- Current: No ondelete
-- Fix: SET NULL (preserve audit logs even if user deleted)
ALTER TABLE audit_logs
DROP CONSTRAINT IF EXISTS audit_logs_user_id_fkey,
ADD CONSTRAINT audit_logs_user_id_fkey
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE SET NULL;

-- ============================================================================
-- PHASE 2: Fix nullable/ondelete Conflicts
-- ============================================================================

-- FIX #17: tickets.created_by
-- Current: nullable=False with ondelete=SET NULL (conflict!)
-- Fix: Change to RESTRICT (never delete users, maintain audit trail)
ALTER TABLE tickets
DROP CONSTRAINT IF EXISTS tickets_created_by_fkey,
ADD CONSTRAINT tickets_created_by_fkey
    FOREIGN KEY (created_by)
    REFERENCES users(id)
    ON DELETE RESTRICT;

-- FIX #18: ticket_replies.user_id
-- Current: nullable=False with ondelete=SET NULL (conflict!)
-- Fix: Change to RESTRICT
ALTER TABLE ticket_replies
DROP CONSTRAINT IF EXISTS ticket_replies_user_id_fkey,
ADD CONSTRAINT ticket_replies_user_id_fkey
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE RESTRICT;

-- FIX #19: ticket_attachments.uploaded_by
-- Current: nullable=False with ondelete=SET NULL (conflict!)
-- Fix: Change to RESTRICT
ALTER TABLE ticket_attachments
DROP CONSTRAINT IF EXISTS ticket_attachments_uploaded_by_fkey,
ADD CONSTRAINT ticket_attachments_uploaded_by_fkey
    FOREIGN KEY (uploaded_by)
    REFERENCES users(id)
    ON DELETE RESTRICT;

-- ============================================================================
-- PHASE 3: Add Missing Unique Constraints
-- ============================================================================

-- FIX #20: attendance - prevent duplicate records for same courier/date
ALTER TABLE attendance
ADD CONSTRAINT uq_attendance_courier_date
    UNIQUE (courier_id, date);

-- FIX #21: salaries - prevent duplicate records for same courier/period
ALTER TABLE salaries
ADD CONSTRAINT uq_salary_courier_period
    UNIQUE (courier_id, year, month);

-- ============================================================================
-- PHASE 4: Fix Type Inconsistencies
-- ============================================================================

-- FIX #22: deliveries.cod_amount - change from Integer to Numeric
ALTER TABLE deliveries
ALTER COLUMN cod_amount TYPE NUMERIC(10, 2)
USING cod_amount::numeric;

-- Update default value
ALTER TABLE deliveries
ALTER COLUMN cod_amount SET DEFAULT 0.0;

-- FIX #23: incidents.cost - change from Integer to Numeric
ALTER TABLE incidents
ALTER COLUMN cost TYPE NUMERIC(10, 2)
USING cost::numeric;

-- Update default value
ALTER TABLE incidents
ALTER COLUMN cost SET DEFAULT 0.0;

-- FIX #24: ticket_replies.is_internal - change from Integer to Boolean
-- First, convert existing data
UPDATE ticket_replies
SET is_internal = CASE WHEN is_internal::INTEGER != 0 THEN 1 ELSE 0 END;

-- Now change column type
ALTER TABLE ticket_replies
ALTER COLUMN is_internal TYPE BOOLEAN
USING CASE WHEN is_internal::INTEGER != 0 THEN TRUE ELSE FALSE END;

-- Set default
ALTER TABLE ticket_replies
ALTER COLUMN is_internal SET DEFAULT FALSE,
ALTER COLUMN is_internal SET NOT NULL;

-- ============================================================================
-- PHASE 5: Add Critical Indexes for Performance
-- ============================================================================

-- INDEX #1: Composite index for courier assignments by status
CREATE INDEX IF NOT EXISTS ix_assignment_courier_status
ON courier_vehicle_assignments(courier_id, status);

-- INDEX #2: Composite index for vehicle maintenance by status
CREATE INDEX IF NOT EXISTS ix_maintenance_vehicle_status
ON vehicle_maintenance(vehicle_id, status);

-- INDEX #3: Composite index for inspections by vehicle and date
CREATE INDEX IF NOT EXISTS ix_inspection_vehicle_date
ON vehicle_inspections(vehicle_id, inspection_date DESC);

-- INDEX #4: Composite index for accident logs by vehicle and date
CREATE INDEX IF NOT EXISTS ix_accident_vehicle_date
ON accident_logs(vehicle_id, accident_date DESC);

-- INDEX #5: Composite index for salary by courier and period
CREATE INDEX IF NOT EXISTS ix_salary_courier_period
ON salaries(courier_id, year DESC, month DESC);

-- INDEX #6: Composite index for attendance by courier and date
CREATE INDEX IF NOT EXISTS ix_attendance_courier_date
ON attendance(courier_id, date DESC);

-- INDEX #7: Composite index for multi-tenant queries (all tenant tables)
CREATE INDEX IF NOT EXISTS ix_couriers_org_created
ON couriers(organization_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_vehicles_org_created
ON vehicles(organization_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_deliveries_org_created
ON deliveries(organization_id, created_at DESC);

CREATE INDEX IF NOT EXISTS ix_routes_org_date
ON routes(organization_id, route_date DESC);

CREATE INDEX IF NOT EXISTS ix_tickets_org_created
ON tickets(organization_id, created_at DESC);

-- INDEX #8: Index on ticket category for filtering
CREATE INDEX IF NOT EXISTS ix_tickets_category
ON tickets(category);

-- INDEX #9: Index on ticket status for filtering
CREATE INDEX IF NOT EXISTS ix_tickets_status_priority
ON tickets(status, priority);

-- INDEX #10: Index on delivery status for filtering
CREATE INDEX IF NOT EXISTS ix_deliveries_status
ON deliveries(status);

-- INDEX #11: Index on route status for filtering
CREATE INDEX IF NOT EXISTS ix_routes_status
ON routes(status);

-- ============================================================================
-- PHASE 6: Data Cleanup (Remove Orphaned Columns)
-- ============================================================================

-- FIX #25: Remove orphaned accommodation columns from couriers table
-- These are redundant - Allocation table is the source of truth
-- COMMENTED OUT: Only run after verifying no application code uses these columns
-- ALTER TABLE couriers
-- DROP COLUMN IF EXISTS accommodation_building_id,
-- DROP COLUMN IF EXISTS accommodation_room_id;

-- ============================================================================
-- PHASE 7: Add Check Constraints for Data Validation
-- ============================================================================

-- CHECK #1: Salary month must be 1-12
ALTER TABLE salaries
ADD CONSTRAINT check_salary_month_range
    CHECK (month >= 1 AND month <= 12);

-- CHECK #2: Salary year must be reasonable
ALTER TABLE salaries
ADD CONSTRAINT check_salary_year_range
    CHECK (year >= 2000 AND year <= 2100);

-- CHECK #3: Leave dates must be valid (end_date >= start_date)
ALTER TABLE leaves
ADD CONSTRAINT check_leave_date_range
    CHECK (end_date >= start_date);

-- CHECK #4: Loan outstanding balance cannot be negative
ALTER TABLE loans
ADD CONSTRAINT check_loan_balance_positive
    CHECK (outstanding_balance >= 0);

-- CHECK #5: Vehicle year must be reasonable
ALTER TABLE vehicles
ADD CONSTRAINT check_vehicle_year_range
    CHECK (year >= 1950 AND year <= 2100);

-- CHECK #6: Courier age must be reasonable (assuming 18-80)
-- Calculated from date_of_birth
ALTER TABLE couriers
ADD CONSTRAINT check_courier_birth_date
    CHECK (
        date_of_birth IS NULL OR
        (date_of_birth >= (CURRENT_DATE - INTERVAL '80 years') AND
         date_of_birth <= (CURRENT_DATE - INTERVAL '18 years'))
    );

-- ============================================================================
-- PHASE 8: Fix BaseModel updated_at Default
-- ============================================================================

-- Add server_default to updated_at for all tables that inherit from BaseModel
-- This ensures updated_at is set on INSERT, not just UPDATE

-- For each table, run:
ALTER TABLE couriers
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE vehicles
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE organizations
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE users
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE deliveries
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE routes
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE tickets
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE salaries
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE loans
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE leaves
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE attendance
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE buildings
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE rooms
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE beds
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE allocations
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE vehicle_maintenance
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE vehicle_inspections
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE accident_logs
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE vehicle_logs
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE fuel_logs
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE assets
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE bonuses
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE incidents
ALTER COLUMN updated_at SET DEFAULT NOW();

ALTER TABLE cod_transactions
ALTER COLUMN updated_at SET DEFAULT NOW();

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Run these queries to verify the fixes were applied correctly:

-- 1. Verify all foreign keys have ondelete behavior
SELECT
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
    AND ccu.table_schema = tc.table_schema
JOIN information_schema.referential_constraints AS rc
    ON tc.constraint_name = rc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name, kcu.column_name;

-- 2. Verify unique constraints were added
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    string_agg(kcu.column_name, ', ') AS columns
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'UNIQUE'
    AND tc.table_schema = 'public'
    AND tc.table_name IN ('attendance', 'salaries')
GROUP BY tc.table_name, tc.constraint_name, tc.constraint_type
ORDER BY tc.table_name;

-- 3. Verify indexes were created
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND (
        indexname LIKE 'ix_assignment_%'
        OR indexname LIKE 'ix_maintenance_%'
        OR indexname LIKE 'ix_inspection_%'
        OR indexname LIKE 'ix_accident_%'
        OR indexname LIKE 'ix_salary_%'
        OR indexname LIKE 'ix_attendance_%'
        OR indexname LIKE 'ix_%_org_%'
    )
ORDER BY tablename, indexname;

-- 4. Verify column types were changed
SELECT
    table_name,
    column_name,
    data_type,
    numeric_precision,
    numeric_scale
FROM information_schema.columns
WHERE table_schema = 'public'
    AND (
        (table_name = 'deliveries' AND column_name = 'cod_amount') OR
        (table_name = 'incidents' AND column_name = 'cost') OR
        (table_name = 'ticket_replies' AND column_name = 'is_internal')
    )
ORDER BY table_name, column_name;

-- 5. Check for any orphaned records in allocations
SELECT
    'Orphaned courier allocations' AS issue,
    COUNT(*) AS count
FROM allocations a
LEFT JOIN couriers c ON a.courier_id = c.id
WHERE c.id IS NULL

UNION ALL

SELECT
    'Orphaned bed allocations' AS issue,
    COUNT(*) AS count
FROM allocations a
LEFT JOIN beds b ON a.bed_id = b.id
WHERE b.id IS NULL;

-- 6. Check for any duplicate attendance records
SELECT
    courier_id,
    date,
    COUNT(*) AS duplicates
FROM attendance
GROUP BY courier_id, date
HAVING COUNT(*) > 1;

-- 7. Check for any duplicate salary records
SELECT
    courier_id,
    year,
    month,
    COUNT(*) AS duplicates
FROM salaries
GROUP BY courier_id, year, month
HAVING COUNT(*) > 1;

COMMIT;

-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
-- If something goes wrong, restore from backup:
-- psql -h localhost -U postgres -d barq_fleet < backup_before_migration.sql
-- ============================================================================

-- ============================================================================
-- POST-MIGRATION TASKS
-- ============================================================================
-- 1. Update SQLAlchemy models to match database changes
-- 2. Run Alembic to generate migration files for tracking
-- 3. Update application code that uses removed columns
-- 4. Test all CRUD operations, especially deletions
-- 5. Run integration tests
-- 6. Monitor application logs for constraint violations
-- 7. Update API documentation if any changes affect endpoints
-- ============================================================================
