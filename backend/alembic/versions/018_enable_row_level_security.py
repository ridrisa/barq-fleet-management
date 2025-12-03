"""Enable Row-Level Security (RLS) for multi-tenant isolation

Revision ID: 018
Revises: 017
Create Date: 2025-12-03

This migration enables PostgreSQL Row-Level Security (RLS) on all tenant-aware tables.
RLS provides database-level tenant isolation that cannot be bypassed even by application bugs.

Security model:
- Regular users can only access rows where organization_id matches their session context
- Superusers/admins can bypass RLS when needed (via app.is_superuser setting)
- The application sets session variables (app.current_org_id) to control access

Usage in application:
    SET app.current_org_id = '123';
    SET app.is_superuser = 'false';
    -- All queries now automatically filtered by organization_id = 123
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '018'
down_revision = '017'
branch_labels = None
depends_on = None

# All tables with RLS policies
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


def upgrade() -> None:
    connection = op.get_bind()

    # Create application role if it doesn't exist (for RLS policies)
    connection.execute(
        sa.text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
                    CREATE ROLE app_user;
                END IF;
            END
            $$;
            """
        )
    )

    # Enable RLS and create policies for each table
    for table_name in TENANT_TABLES:
        if not table_exists(connection, table_name):
            print(f"Table {table_name} does not exist, skipping RLS...")
            continue

        print(f"Enabling RLS on {table_name}...")

        # Enable Row Level Security
        connection.execute(
            sa.text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
        )

        # Force RLS for table owner too (important for security)
        connection.execute(
            sa.text(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY")
        )

        # Drop existing policies if they exist
        connection.execute(
            sa.text(f"DROP POLICY IF EXISTS tenant_isolation_{table_name} ON {table_name}")
        )
        connection.execute(
            sa.text(f"DROP POLICY IF EXISTS superuser_bypass_{table_name} ON {table_name}")
        )

        # Create tenant isolation policy
        # This policy checks if organization_id matches the session variable
        connection.execute(
            sa.text(
                f"""
                CREATE POLICY tenant_isolation_{table_name} ON {table_name}
                FOR ALL
                USING (
                    organization_id = COALESCE(
                        NULLIF(current_setting('app.current_org_id', true), '')::integer,
                        organization_id
                    )
                )
                WITH CHECK (
                    organization_id = COALESCE(
                        NULLIF(current_setting('app.current_org_id', true), '')::integer,
                        organization_id
                    )
                )
                """
            )
        )

        # Create superuser bypass policy
        # Superusers can access all organizations when app.is_superuser is set
        connection.execute(
            sa.text(
                f"""
                CREATE POLICY superuser_bypass_{table_name} ON {table_name}
                FOR ALL
                USING (
                    COALESCE(current_setting('app.is_superuser', true), 'false')::boolean = true
                )
                WITH CHECK (
                    COALESCE(current_setting('app.is_superuser', true), 'false')::boolean = true
                )
                """
            )
        )

    print("Row-Level Security enabled on all tables!")


def downgrade() -> None:
    connection = op.get_bind()

    # Disable RLS and drop policies for each table
    for table_name in reversed(TENANT_TABLES):
        if not table_exists(connection, table_name):
            continue

        print(f"Disabling RLS on {table_name}...")

        # Drop policies
        connection.execute(
            sa.text(f"DROP POLICY IF EXISTS tenant_isolation_{table_name} ON {table_name}")
        )
        connection.execute(
            sa.text(f"DROP POLICY IF EXISTS superuser_bypass_{table_name} ON {table_name}")
        )

        # Disable RLS
        connection.execute(
            sa.text(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY")
        )
        connection.execute(
            sa.text(f"ALTER TABLE {table_name} NO FORCE ROW LEVEL SECURITY")
        )

    print("Row-Level Security disabled on all tables!")
