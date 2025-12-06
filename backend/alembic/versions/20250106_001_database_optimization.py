"""Database Optimization - Indexes, Constraints, and Performance

Revision ID: 20250106_001
Revises: <previous_revision>
Create Date: 2025-01-06 10:00:00.000000

This migration adds comprehensive database optimizations:
1. Missing indexes on foreign keys
2. Composite indexes for common query patterns
3. Partial indexes for filtered queries
4. Index on timestamp columns for time-series queries
5. Missing indexes on status and frequently queried columns

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250106_001'
down_revision = '021'  # Points to the latest migration
branch_labels = None
depends_on = None


def upgrade():
    """Add performance optimization indexes"""

    # =================================================================
    # FLEET MODULE - Courier Indexes
    # =================================================================
    print("Adding indexes for couriers table...")

    # Composite index for multi-tenant queries with status filter
    op.create_index(
        'idx_couriers_org_status',
        'couriers',
        ['organization_id', 'status'],
        unique=False
    )

    # Composite index for city-based queries
    op.create_index(
        'idx_couriers_org_city_status',
        'couriers',
        ['organization_id', 'city', 'status'],
        unique=False
    )

    # Partial index for active couriers (most common query)
    op.execute("""
        CREATE INDEX idx_couriers_active
        ON couriers (organization_id, joining_date DESC)
        WHERE status = 'ACTIVE'
    """)

    # Partial index for couriers without vehicles
    op.execute("""
        CREATE INDEX idx_couriers_no_vehicle
        ON couriers (organization_id, id)
        WHERE current_vehicle_id IS NULL AND status = 'ACTIVE'
    """)

    # Index for document expiry checks
    op.create_index(
        'idx_couriers_iqama_expiry',
        'couriers',
        ['iqama_expiry_date'],
        unique=False,
        postgresql_where=sa.text("iqama_expiry_date IS NOT NULL")
    )

    op.create_index(
        'idx_couriers_license_expiry',
        'couriers',
        ['license_expiry_date'],
        unique=False,
        postgresql_where=sa.text("license_expiry_date IS NOT NULL")
    )

    # Index for FMS integration lookups
    op.create_index(
        'idx_couriers_fms_asset',
        'couriers',
        ['fms_asset_id'],
        unique=False,
        postgresql_where=sa.text("fms_asset_id IS NOT NULL")
    )

    # Index on created_at for time-series queries
    op.create_index(
        'idx_couriers_created_at',
        'couriers',
        ['created_at'],
        unique=False
    )

    # =================================================================
    # FLEET MODULE - Vehicle Indexes
    # =================================================================
    print("Adding indexes for vehicles table...")

    # Composite index for multi-tenant queries with status
    op.create_index(
        'idx_vehicles_org_status',
        'vehicles',
        ['organization_id', 'status'],
        unique=False
    )

    # Composite index for type-based queries
    op.create_index(
        'idx_vehicles_org_type_status',
        'vehicles',
        ['organization_id', 'vehicle_type', 'status'],
        unique=False
    )

    # Partial index for active vehicles
    op.execute("""
        CREATE INDEX idx_vehicles_active
        ON vehicles (organization_id, vehicle_type)
        WHERE status = 'ACTIVE'
    """)

    # Index for service due dates
    op.create_index(
        'idx_vehicles_next_service',
        'vehicles',
        ['next_service_due_date'],
        unique=False,
        postgresql_where=sa.text("next_service_due_date IS NOT NULL AND status = 'ACTIVE'")
    )

    # Index for insurance expiry
    op.create_index(
        'idx_vehicles_insurance_expiry',
        'vehicles',
        ['insurance_expiry_date'],
        unique=False,
        postgresql_where=sa.text("insurance_expiry_date IS NOT NULL")
    )

    # Index on city assignment
    op.create_index(
        'idx_vehicles_city',
        'vehicles',
        ['assigned_to_city', 'status'],
        unique=False,
        postgresql_where=sa.text("assigned_to_city IS NOT NULL")
    )

    # =================================================================
    # FLEET MODULE - Assignment Indexes
    # =================================================================
    print("Adding indexes for courier_vehicle_assignments table...")

    # Composite index for finding active assignments
    op.create_index(
        'idx_assignments_org_status',
        'courier_vehicle_assignments',
        ['organization_id', 'status'],
        unique=False
    )

    # Composite index for courier's assignments
    op.create_index(
        'idx_assignments_courier_dates',
        'courier_vehicle_assignments',
        ['courier_id', 'start_date', 'end_date'],
        unique=False
    )

    # Composite index for vehicle's assignments
    op.create_index(
        'idx_assignments_vehicle_dates',
        'courier_vehicle_assignments',
        ['vehicle_id', 'start_date', 'end_date'],
        unique=False
    )

    # Partial index for active assignments only
    op.execute("""
        CREATE INDEX idx_assignments_active
        ON courier_vehicle_assignments (courier_id, vehicle_id, start_date)
        WHERE status = 'active' AND end_date IS NULL
    """)

    # =================================================================
    # OPERATIONS MODULE - Delivery Indexes
    # =================================================================
    print("Adding indexes for deliveries table...")

    # Composite index for courier's deliveries
    op.create_index(
        'idx_deliveries_courier_status',
        'deliveries',
        ['courier_id', 'status', 'created_at'],
        unique=False
    )

    # Composite index for organization queries
    op.create_index(
        'idx_deliveries_org_status',
        'deliveries',
        ['organization_id', 'status', 'created_at'],
        unique=False
    )

    # Partial index for pending deliveries (most queried)
    op.execute("""
        CREATE INDEX idx_deliveries_pending
        ON deliveries (organization_id, courier_id, created_at DESC)
        WHERE status = 'pending'
    """)

    # Partial index for COD deliveries
    op.execute("""
        CREATE INDEX idx_deliveries_cod
        ON deliveries (courier_id, status, cod_amount)
        WHERE cod_amount > 0
    """)

    # Index on tracking number (should already exist, but ensure it's there)
    op.create_index(
        'idx_deliveries_tracking',
        'deliveries',
        ['tracking_number'],
        unique=True,
        postgresql_ops={'tracking_number': 'text_pattern_ops'}
    )

    # Index for time-based queries
    op.create_index(
        'idx_deliveries_pickup_time',
        'deliveries',
        ['pickup_time'],
        unique=False,
        postgresql_where=sa.text("pickup_time IS NOT NULL")
    )

    op.create_index(
        'idx_deliveries_delivery_time',
        'deliveries',
        ['delivery_time'],
        unique=False,
        postgresql_where=sa.text("delivery_time IS NOT NULL")
    )

    # =================================================================
    # OPERATIONS MODULE - COD Indexes
    # =================================================================
    print("Adding indexes for cod_transactions table...")

    # Composite index for courier's COD transactions
    op.create_index(
        'idx_cod_courier_status',
        'cod_transactions',
        ['courier_id', 'status', 'collection_date'],
        unique=False
    )

    # Composite index for organization queries
    op.create_index(
        'idx_cod_org_status',
        'cod_transactions',
        ['organization_id', 'status', 'collection_date'],
        unique=False
    )

    # Partial index for pending collections
    op.execute("""
        CREATE INDEX idx_cod_pending
        ON cod_transactions (courier_id, collection_date DESC)
        WHERE status = 'pending'
    """)

    # Index on collection date for date-range queries
    op.create_index(
        'idx_cod_collection_date',
        'cod_transactions',
        ['collection_date', 'status'],
        unique=False
    )

    # =================================================================
    # HR MODULE - Salary Indexes
    # =================================================================
    print("Adding indexes for salaries table...")

    # Composite index for courier's salary history
    op.create_index(
        'idx_salaries_courier_period',
        'salaries',
        ['courier_id', 'year', 'month'],
        unique=False
    )

    # Composite index for organization payroll queries
    op.create_index(
        'idx_salaries_org_period',
        'salaries',
        ['organization_id', 'year', 'month'],
        unique=False
    )

    # Index on payment date
    op.create_index(
        'idx_salaries_payment_date',
        'salaries',
        ['payment_date'],
        unique=False,
        postgresql_where=sa.text("payment_date IS NOT NULL")
    )

    # Unique constraint for one salary per courier per month
    op.create_index(
        'idx_salaries_unique_month',
        'salaries',
        ['courier_id', 'year', 'month'],
        unique=True
    )

    # =================================================================
    # HR MODULE - Attendance Indexes
    # =================================================================
    print("Adding indexes for attendance table...")

    # Composite index for courier's attendance
    op.create_index(
        'idx_attendance_courier_date',
        'attendance',
        ['courier_id', 'date'],
        unique=False
    )

    # Composite index for organization attendance reports
    op.create_index(
        'idx_attendance_org_date',
        'attendance',
        ['organization_id', 'date', 'status'],
        unique=False
    )

    # Index on date for month-based queries (BRIN for large tables)
    op.execute("""
        CREATE INDEX idx_attendance_date_brin
        ON attendance USING BRIN (date, created_at)
    """)

    # Partial index for absent records
    op.execute("""
        CREATE INDEX idx_attendance_absent
        ON attendance (courier_id, date)
        WHERE status = 'absent'
    """)

    # =================================================================
    # SUPPORT MODULE - Ticket Indexes
    # =================================================================
    print("Adding indexes for tickets table (if exists)...")

    # Check if tickets table exists before adding indexes
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'tickets' in inspector.get_table_names():
        # Composite index for organization tickets
        op.create_index(
            'idx_tickets_org_status',
            'tickets',
            ['organization_id', 'status', 'created_at'],
            unique=False
        )

        # Index on assigned user
        op.create_index(
            'idx_tickets_assigned',
            'tickets',
            ['assigned_to', 'status'],
            unique=False,
            postgresql_where=sa.text("assigned_to IS NOT NULL")
        )

        # Partial index for open tickets
        op.execute("""
            CREATE INDEX idx_tickets_open
            ON tickets (organization_id, priority, created_at DESC)
            WHERE status IN ('open', 'in_progress')
        """)

    # =================================================================
    # AUDIT & GENERAL INDEXES
    # =================================================================
    print("Adding audit and timestamp indexes...")

    # Add created_at and updated_at indexes to frequently queried tables
    tables_for_timestamp_indexes = [
        'vehicle_logs',
        'fuel_logs',
        'maintenance_records',
        'inspections',
        'accident_logs',
        'leaves',
        'loans',
        'bonuses',
        'workflow_instances',
        'audit_logs'
    ]

    for table in tables_for_timestamp_indexes:
        if table in inspector.get_table_names():
            try:
                op.create_index(
                    f'idx_{table}_created_at',
                    table,
                    ['created_at'],
                    unique=False
                )
                print(f"Added created_at index to {table}")
            except Exception as e:
                print(f"Skipping {table}: {str(e)}")

    print("Database optimization indexes added successfully!")


def downgrade():
    """Remove optimization indexes"""

    # Remove all indexes created in upgrade (in reverse order)

    # Timestamp indexes
    tables_for_timestamp_indexes = [
        'audit_logs',
        'workflow_instances',
        'bonuses',
        'loans',
        'leaves',
        'accident_logs',
        'inspections',
        'maintenance_records',
        'fuel_logs',
        'vehicle_logs'
    ]

    conn = op.get_bind()
    inspector = sa.inspect(conn)

    for table in tables_for_timestamp_indexes:
        if table in inspector.get_table_names():
            try:
                op.drop_index(f'idx_{table}_created_at', table_name=table)
            except:
                pass

    # Support module
    if 'tickets' in inspector.get_table_names():
        op.execute("DROP INDEX IF EXISTS idx_tickets_open")
        op.drop_index('idx_tickets_assigned', table_name='tickets')
        op.drop_index('idx_tickets_org_status', table_name='tickets')

    # HR - Attendance
    op.execute("DROP INDEX IF EXISTS idx_attendance_absent")
    op.execute("DROP INDEX IF EXISTS idx_attendance_date_brin")
    op.drop_index('idx_attendance_org_date', table_name='attendance')
    op.drop_index('idx_attendance_courier_date', table_name='attendance')

    # HR - Salary
    op.drop_index('idx_salaries_unique_month', table_name='salaries')
    op.drop_index('idx_salaries_payment_date', table_name='salaries')
    op.drop_index('idx_salaries_org_period', table_name='salaries')
    op.drop_index('idx_salaries_courier_period', table_name='salaries')

    # Operations - COD
    op.drop_index('idx_cod_collection_date', table_name='cod_transactions')
    op.execute("DROP INDEX IF EXISTS idx_cod_pending")
    op.drop_index('idx_cod_org_status', table_name='cod_transactions')
    op.drop_index('idx_cod_courier_status', table_name='cod_transactions')

    # Operations - Delivery
    op.drop_index('idx_deliveries_delivery_time', table_name='deliveries')
    op.drop_index('idx_deliveries_pickup_time', table_name='deliveries')
    op.drop_index('idx_deliveries_tracking', table_name='deliveries')
    op.execute("DROP INDEX IF EXISTS idx_deliveries_cod")
    op.execute("DROP INDEX IF EXISTS idx_deliveries_pending")
    op.drop_index('idx_deliveries_org_status', table_name='deliveries')
    op.drop_index('idx_deliveries_courier_status', table_name='deliveries')

    # Fleet - Assignments
    op.execute("DROP INDEX IF EXISTS idx_assignments_active")
    op.drop_index('idx_assignments_vehicle_dates', table_name='courier_vehicle_assignments')
    op.drop_index('idx_assignments_courier_dates', table_name='courier_vehicle_assignments')
    op.drop_index('idx_assignments_org_status', table_name='courier_vehicle_assignments')

    # Fleet - Vehicles
    op.drop_index('idx_vehicles_city', table_name='vehicles')
    op.drop_index('idx_vehicles_insurance_expiry', table_name='vehicles')
    op.drop_index('idx_vehicles_next_service', table_name='vehicles')
    op.execute("DROP INDEX IF EXISTS idx_vehicles_active")
    op.drop_index('idx_vehicles_org_type_status', table_name='vehicles')
    op.drop_index('idx_vehicles_org_status', table_name='vehicles')

    # Fleet - Couriers
    op.drop_index('idx_couriers_created_at', table_name='couriers')
    op.drop_index('idx_couriers_fms_asset', table_name='couriers')
    op.drop_index('idx_couriers_license_expiry', table_name='couriers')
    op.drop_index('idx_couriers_iqama_expiry', table_name='couriers')
    op.execute("DROP INDEX IF EXISTS idx_couriers_no_vehicle")
    op.execute("DROP INDEX IF EXISTS idx_couriers_active")
    op.drop_index('idx_couriers_org_city_status', table_name='couriers')
    op.drop_index('idx_couriers_org_status', table_name='couriers')

    print("Database optimization indexes removed successfully!")
