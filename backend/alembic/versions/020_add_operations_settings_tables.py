"""Add operations settings tables and fix customer_feedbacks

Revision ID: 020
Revises: 019
Create Date: 2025-12-03

This migration:
1. Creates operations_settings, dispatch_rules, sla_thresholds, notification_settings, zone_defaults tables
2. Adds organization_id to customer_feedbacks table (was missed in migration 017)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

# revision identifiers, used by Alembic.
revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None


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

    # Get default organization ID
    result = connection.execute(
        sa.text("SELECT id FROM organizations ORDER BY id LIMIT 1")
    )
    row = result.fetchone()
    default_org_id = row[0] if row else 1

    # 1. Create operations_settings table
    if not table_exists(connection, 'operations_settings'):
        print("Creating operations_settings table...")
        op.create_table(
            'operations_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('organization_id', sa.Integer(), nullable=False),
            sa.Column('setting_key', sa.String(100), nullable=False),
            sa.Column('setting_name', sa.String(200), nullable=False),
            sa.Column('setting_group', sa.String(100), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('value_type', sa.String(20), nullable=False),
            sa.Column('string_value', sa.Text()),
            sa.Column('number_value', sa.Numeric(20, 4)),
            sa.Column('boolean_value', sa.Boolean()),
            sa.Column('json_value', JSON()),
            sa.Column('min_value', sa.Numeric(20, 4)),
            sa.Column('max_value', sa.Numeric(20, 4)),
            sa.Column('allowed_values', sa.Text()),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('is_system', sa.Boolean(), default=False),
            sa.Column('is_readonly', sa.Boolean(), default=False),
            sa.Column('last_modified_by_id', sa.Integer()),
            sa.Column('last_modified_at', sa.DateTime()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['last_modified_by_id'], ['users.id'], ondelete='SET NULL'),
        )
        op.create_index('ix_operations_settings_setting_key', 'operations_settings', ['setting_key'])
        op.create_index('ix_operations_settings_setting_group', 'operations_settings', ['setting_group'])
        op.create_index('ix_operations_settings_organization_id', 'operations_settings', ['organization_id'])

    # 2. Create dispatch_rules table
    if not table_exists(connection, 'dispatch_rules'):
        print("Creating dispatch_rules table...")
        op.create_table(
            'dispatch_rules',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('organization_id', sa.Integer(), nullable=False),
            sa.Column('rule_code', sa.String(50), nullable=False),
            sa.Column('rule_name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('priority', sa.Integer(), default=100),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('conditions', JSON(), nullable=False),
            sa.Column('actions', JSON(), nullable=False),
            sa.Column('algorithm', sa.String(50), default='load_balanced'),
            sa.Column('max_distance_km', sa.Numeric(10, 2), default=10.0),
            sa.Column('max_courier_load', sa.Integer(), default=5),
            sa.Column('min_courier_rating', sa.Numeric(3, 2)),
            sa.Column('zone_ids', sa.Text()),
            sa.Column('applies_to_all_zones', sa.Boolean(), default=True),
            sa.Column('time_start', sa.String(8)),
            sa.Column('time_end', sa.String(8)),
            sa.Column('days_of_week', sa.String(20)),
            sa.Column('times_triggered', sa.Integer(), default=0),
            sa.Column('successful_assignments', sa.Integer(), default=0),
            sa.Column('failed_assignments', sa.Integer(), default=0),
            sa.Column('created_by_id', sa.Integer()),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        )
        op.create_index('ix_dispatch_rules_rule_code', 'dispatch_rules', ['rule_code'])
        op.create_index('ix_dispatch_rules_priority', 'dispatch_rules', ['priority'])
        op.create_index('ix_dispatch_rules_is_active', 'dispatch_rules', ['is_active'])
        op.create_index('ix_dispatch_rules_organization_id', 'dispatch_rules', ['organization_id'])

    # 3. Create sla_thresholds table
    if not table_exists(connection, 'sla_thresholds'):
        print("Creating sla_thresholds table...")
        op.create_table(
            'sla_thresholds',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('organization_id', sa.Integer(), nullable=False),
            sa.Column('threshold_code', sa.String(50), nullable=False),
            sa.Column('threshold_name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('sla_type', sa.String(50), nullable=False),
            sa.Column('service_type', sa.String(50)),
            sa.Column('target_minutes', sa.Integer(), nullable=False),
            sa.Column('warning_minutes', sa.Integer(), nullable=False),
            sa.Column('critical_minutes', sa.Integer(), nullable=False),
            sa.Column('zone_id', sa.Integer()),
            sa.Column('applies_to_all_zones', sa.Boolean(), default=True),
            sa.Column('penalty_amount', sa.Numeric(10, 2), default=0.0),
            sa.Column('escalation_required', sa.Boolean(), default=True),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_sla_thresholds_threshold_code', 'sla_thresholds', ['threshold_code'])
        op.create_index('ix_sla_thresholds_sla_type', 'sla_thresholds', ['sla_type'])
        op.create_index('ix_sla_thresholds_service_type', 'sla_thresholds', ['service_type'])
        op.create_index('ix_sla_thresholds_zone_id', 'sla_thresholds', ['zone_id'])
        op.create_index('ix_sla_thresholds_organization_id', 'sla_thresholds', ['organization_id'])

    # 4. Create notification_settings table
    if not table_exists(connection, 'notification_settings'):
        print("Creating notification_settings table...")
        op.create_table(
            'notification_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('organization_id', sa.Integer(), nullable=False),
            sa.Column('setting_code', sa.String(50), nullable=False),
            sa.Column('setting_name', sa.String(200), nullable=False),
            sa.Column('event_type', sa.String(100), nullable=False),
            sa.Column('notify_email', sa.Boolean(), default=True),
            sa.Column('notify_sms', sa.Boolean(), default=False),
            sa.Column('notify_push', sa.Boolean(), default=True),
            sa.Column('notify_in_app', sa.Boolean(), default=True),
            sa.Column('notify_webhook', sa.Boolean(), default=False),
            sa.Column('notify_roles', sa.Text()),
            sa.Column('notify_user_ids', sa.Text()),
            sa.Column('webhook_url', sa.String(500)),
            sa.Column('cooldown_minutes', sa.Integer(), default=0),
            sa.Column('batch_delay_minutes', sa.Integer(), default=0),
            sa.Column('email_template', sa.String(100)),
            sa.Column('sms_template', sa.String(100)),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_notification_settings_setting_code', 'notification_settings', ['setting_code'])
        op.create_index('ix_notification_settings_event_type', 'notification_settings', ['event_type'])
        op.create_index('ix_notification_settings_organization_id', 'notification_settings', ['organization_id'])

    # 5. Create zone_defaults table
    if not table_exists(connection, 'zone_defaults'):
        print("Creating zone_defaults table...")
        op.create_table(
            'zone_defaults',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('organization_id', sa.Integer(), nullable=False),
            sa.Column('default_code', sa.String(50), nullable=False),
            sa.Column('default_name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text()),
            sa.Column('default_max_couriers', sa.Integer(), default=10),
            sa.Column('default_priority_level', sa.Integer(), default=3),
            sa.Column('default_service_fee', sa.Numeric(10, 2), default=0.0),
            sa.Column('default_peak_multiplier', sa.Numeric(5, 2), default=1.5),
            sa.Column('default_minimum_order', sa.Numeric(10, 2), default=0.0),
            sa.Column('default_delivery_time_minutes', sa.Integer(), default=60),
            sa.Column('default_sla_target_minutes', sa.Integer(), default=45),
            sa.Column('operating_start', sa.String(8), default='08:00:00'),
            sa.Column('operating_end', sa.String(8), default='22:00:00'),
            sa.Column('is_active', sa.Boolean(), default=True),
            sa.Column('is_default', sa.Boolean(), default=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        )
        op.create_index('ix_zone_defaults_default_code', 'zone_defaults', ['default_code'])
        op.create_index('ix_zone_defaults_organization_id', 'zone_defaults', ['organization_id'])

    # 6. Add organization_id to customer_feedbacks if missing
    if table_exists(connection, 'customer_feedbacks'):
        if not column_exists(connection, 'customer_feedbacks', 'organization_id'):
            print("Adding organization_id to customer_feedbacks...")

            # Add column as nullable first
            op.add_column(
                'customer_feedbacks',
                sa.Column('organization_id', sa.Integer(), nullable=True)
            )

            # Update existing rows to use default organization
            connection.execute(
                sa.text("UPDATE customer_feedbacks SET organization_id = :org_id"),
                {"org_id": default_org_id}
            )

            # Make column NOT NULL
            op.alter_column(
                'customer_feedbacks',
                'organization_id',
                nullable=False
            )

            # Add foreign key constraint
            op.create_foreign_key(
                'fk_customer_feedbacks_organization_id',
                'customer_feedbacks',
                'organizations',
                ['organization_id'],
                ['id'],
                ondelete='CASCADE'
            )

            # Create index
            op.create_index(
                'ix_customer_feedbacks_organization_id',
                'customer_feedbacks',
                ['organization_id']
            )

    print("Migration 020 completed successfully!")


def downgrade() -> None:
    connection = op.get_bind()

    # Remove organization_id from customer_feedbacks
    if table_exists(connection, 'customer_feedbacks'):
        if column_exists(connection, 'customer_feedbacks', 'organization_id'):
            try:
                op.drop_index('ix_customer_feedbacks_organization_id', 'customer_feedbacks')
            except Exception:
                pass
            try:
                op.drop_constraint('fk_customer_feedbacks_organization_id', 'customer_feedbacks', type_='foreignkey')
            except Exception:
                pass
            op.drop_column('customer_feedbacks', 'organization_id')

    # Drop tables in reverse order
    for table_name in ['zone_defaults', 'notification_settings', 'sla_thresholds', 'dispatch_rules', 'operations_settings']:
        if table_exists(connection, table_name):
            op.drop_table(table_name)

    print("Migration 020 rollback completed!")
