"""Add multi-tenancy organization_id to all tables

Revision ID: 017
Revises: perf_indexes_001
Create Date: 2025-12-03

This migration adds organization_id to all tenant-aware tables for multi-tenancy support.
It performs the following steps:
1. Creates a default organization if none exists
2. Adds organization_id column (nullable initially) to all tables
3. Updates existing rows to use the default organization
4. Makes organization_id NOT NULL
5. Adds foreign key constraints with CASCADE delete
6. Creates indexes for query performance
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '017'
down_revision = 'perf_indexes_001'
branch_labels = None
depends_on = None

# All tables that need organization_id for multi-tenancy
TENANT_TABLES = [
    # Fleet tables
    'couriers',
    'vehicles',
    'courier_vehicle_assignments',
    'accident_logs',
    'fuel_logs',
    'vehicle_logs',
    'vehicle_maintenance',
    'inspections',
    'documents',

    # HR tables
    'attendance',
    'leaves',
    'loans',
    'salaries',
    'assets',
    'bonuses',

    # Operations tables
    'deliveries',
    'cods',
    'dispatch_assignments',
    'operations_documents',
    'customer_feedback',
    'feedback_templates',
    'handovers',
    'incidents',
    'priority_queue_entries',
    'quality_metrics',
    'quality_inspections',
    'routes',
    'operations_settings',
    'dispatch_rules',
    'sla_thresholds',
    'notification_settings',
    'zone_defaults',
    'sla_definitions',
    'sla_tracking',
    'zones',

    # Accommodation tables
    'buildings',
    'rooms',
    'beds',
    'allocations',

    # Analytics tables
    'dashboards',
    'kpis',
    'metric_snapshots',
    'performance_data',
    'reports',

    # Admin tables
    'api_keys',
    'backups',
    'integrations',
    'system_settings',

    # Support tables
    'tickets',
    'ticket_replies',
    'ticket_attachments',
    'ticket_templates',
    'chat_sessions',
    'chat_messages',
    'canned_responses',
    'faqs',
    'support_feedback',
    'kb_articles',
    'kb_categories',

    # Workflow tables
    'workflow_templates',
    'workflow_instances',
    'workflow_history',
    'workflow_step_history',
    'workflow_comments',
    'workflow_attachments',
    'workflow_automations',
    'automation_execution_logs',
    'workflow_notification_templates',
    'workflow_notifications',
    'notification_preferences',
    'workflow_slas',
    'workflow_sla_instances',
    'sla_events',
    'workflow_triggers',
    'trigger_executions',
    'workflow_metrics',
    'workflow_step_metrics',
    'workflow_performance_snapshots',
    'workflow_user_metrics',
    'approval_chains',
    'approval_chain_approvers',
    'approval_requests',
]


def table_exists(connection, table_name):
    """Check if a table exists in the database"""
    result = connection.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = :table_name)"
        ),
        {"table_name": table_name}
    )
    return result.scalar()


def column_exists(connection, table_name, column_name):
    """Check if a column exists in a table"""
    result = connection.execute(
        sa.text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name = :table_name AND column_name = :column_name
            )
            """
        ),
        {"table_name": table_name, "column_name": column_name}
    )
    return result.scalar()


def upgrade() -> None:
    connection = op.get_bind()

    # Step 1: Ensure default organization exists
    result = connection.execute(
        sa.text("SELECT id FROM organizations ORDER BY id LIMIT 1")
    )
    row = result.fetchone()

    if row is None:
        # Create default organization
        connection.execute(
            sa.text(
                """
                INSERT INTO organizations (name, slug, is_active, subscription_plan, subscription_status,
                                          max_users, max_couriers, max_vehicles, created_at)
                VALUES ('Default Organization', 'default', true, 'ENTERPRISE', 'ACTIVE',
                        1000, 10000, 10000, NOW())
                RETURNING id
                """
            )
        )
        result = connection.execute(
            sa.text("SELECT id FROM organizations ORDER BY id LIMIT 1")
        )
        row = result.fetchone()

    default_org_id = row[0]
    print(f"Using organization ID {default_org_id} as default")

    # Step 2: Add organization_id column to each table (nullable first)
    for table_name in TENANT_TABLES:
        if not table_exists(connection, table_name):
            print(f"Table {table_name} does not exist, skipping...")
            continue

        if column_exists(connection, table_name, 'organization_id'):
            print(f"Table {table_name} already has organization_id, skipping...")
            continue

        print(f"Adding organization_id to {table_name}...")

        # Add column as nullable
        op.add_column(
            table_name,
            sa.Column('organization_id', sa.Integer(), nullable=True)
        )

        # Update existing rows to use default organization
        connection.execute(
            sa.text(f"UPDATE {table_name} SET organization_id = :org_id"),
            {"org_id": default_org_id}
        )

        # Make column NOT NULL
        op.alter_column(
            table_name,
            'organization_id',
            nullable=False
        )

        # Add foreign key constraint
        op.create_foreign_key(
            f'fk_{table_name}_organization_id',
            table_name,
            'organizations',
            ['organization_id'],
            ['id'],
            ondelete='CASCADE'
        )

        # Create index for performance
        op.create_index(
            f'ix_{table_name}_organization_id',
            table_name,
            ['organization_id']
        )

    print("Multi-tenancy migration completed successfully!")


def downgrade() -> None:
    connection = op.get_bind()

    # Remove organization_id from all tables in reverse order
    for table_name in reversed(TENANT_TABLES):
        if not table_exists(connection, table_name):
            continue

        if not column_exists(connection, table_name, 'organization_id'):
            continue

        print(f"Removing organization_id from {table_name}...")

        # Drop index (ignore if doesn't exist)
        try:
            op.drop_index(f'ix_{table_name}_organization_id', table_name)
        except Exception:
            pass

        # Drop foreign key (ignore if doesn't exist)
        try:
            op.drop_constraint(f'fk_{table_name}_organization_id', table_name, type_='foreignkey')
        except Exception:
            pass

        # Drop column
        op.drop_column(table_name, 'organization_id')

    print("Multi-tenancy migration rollback completed!")
