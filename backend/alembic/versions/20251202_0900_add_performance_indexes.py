"""add_performance_indexes

Revision ID: perf_indexes_001
Revises: dbfbd2a3e4e4
Create Date: 2025-12-02 09:00:00.000000

Add performance-critical database indexes for common queries
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'perf_indexes_001'
down_revision = 'dbfbd2a3e4e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add performance indexes for common query patterns
    """

    # ==================== USER INDEXES ====================

    # Index for user lookups by email (login)
    op.create_index(
        'ix_users_email_lower',
        'users',
        [sa.text('LOWER(email)')],
        unique=True,
        postgresql_where=sa.text('is_active = true')
    )

    # Index for active users by organization
    op.create_index(
        'ix_users_org_active',
        'users',
        ['organization_id', 'is_active', 'created_at'],
        postgresql_where=sa.text('is_active = true')
    )

    # Index for user search by name
    op.create_index(
        'ix_users_name_search',
        'users',
        [sa.text('LOWER(first_name)'), sa.text('LOWER(last_name)')],
    )

    # ==================== COURIER INDEXES ====================

    # Index for active couriers by organization
    op.create_index(
        'ix_couriers_org_status',
        'couriers',
        ['organization_id', 'status', 'created_at'],
        postgresql_where=sa.text("status IN ('active', 'on_duty')")
    )

    # Index for courier assignment lookup
    op.create_index(
        'ix_couriers_user_org',
        'couriers',
        ['user_id', 'organization_id'],
    )

    # Index for courier geolocation queries
    op.create_index(
        'ix_couriers_location',
        'couriers',
        ['current_latitude', 'current_longitude'],
        postgresql_where=sa.text("status = 'on_duty'")
    )

    # ==================== VEHICLE INDEXES ====================

    # Index for active vehicles by organization
    op.create_index(
        'ix_vehicles_org_status',
        'vehicles',
        ['organization_id', 'status', 'created_at'],
        postgresql_where=sa.text("status IN ('active', 'in_use')")
    )

    # Index for vehicle assignment
    op.create_index(
        'ix_vehicles_assigned_to',
        'vehicles',
        ['assigned_to', 'status'],
        postgresql_where=sa.text('assigned_to IS NOT NULL')
    )

    # Index for vehicle type filtering
    op.create_index(
        'ix_vehicles_type_org',
        'vehicles',
        ['vehicle_type', 'organization_id'],
    )

    # ==================== DELIVERY INDEXES ====================

    # Index for delivery status tracking
    op.create_index(
        'ix_deliveries_status_date',
        'deliveries',
        ['status', 'created_at'],
        postgresql_where=sa.text("status IN ('pending', 'in_transit', 'delivered')")
    )

    # Index for courier deliveries
    op.create_index(
        'ix_deliveries_courier_status',
        'deliveries',
        ['courier_id', 'status', 'created_at'],
        postgresql_where=sa.text('courier_id IS NOT NULL')
    )

    # Index for delivery SLA monitoring
    op.create_index(
        'ix_deliveries_sla',
        'deliveries',
        ['expected_delivery_at', 'status'],
        postgresql_where=sa.text("status IN ('pending', 'in_transit')")
    )

    # Index for delivery tracking number lookup
    op.create_index(
        'ix_deliveries_tracking_number',
        'deliveries',
        ['tracking_number'],
        unique=True
    )

    # Composite index for organization deliveries by date
    op.create_index(
        'ix_deliveries_org_date',
        'deliveries',
        ['organization_id', 'created_at', 'status'],
    )

    # ==================== ROUTE INDEXES ====================

    # Index for active routes
    op.create_index(
        'ix_routes_status_date',
        'routes',
        ['status', 'scheduled_start', 'organization_id'],
        postgresql_where=sa.text("status IN ('planned', 'in_progress')")
    )

    # Index for courier routes
    op.create_index(
        'ix_routes_courier_status',
        'routes',
        ['courier_id', 'status', 'scheduled_start'],
    )

    # ==================== TICKET INDEXES ====================

    # Index for open tickets
    op.create_index(
        'ix_tickets_status_priority',
        'tickets',
        ['status', 'priority', 'created_at'],
        postgresql_where=sa.text("status IN ('open', 'in_progress')")
    )

    # Index for ticket assignment
    op.create_index(
        'ix_tickets_assigned_status',
        'tickets',
        ['assigned_to', 'status', 'created_at'],
        postgresql_where=sa.text('assigned_to IS NOT NULL')
    )

    # Index for ticket SLA monitoring
    op.create_index(
        'ix_tickets_sla_breach',
        'tickets',
        ['sla_due_at', 'sla_breached', 'status'],
        postgresql_where=sa.text("status IN ('open', 'in_progress')")
    )

    # Index for ticket search by number
    op.create_index(
        'ix_tickets_number',
        'tickets',
        ['number'],
        unique=True
    )

    # Composite index for organization tickets
    op.create_index(
        'ix_tickets_org_date',
        'tickets',
        ['organization_id', 'created_at', 'status'],
    )

    # ==================== WORKFLOW INDEXES ====================

    # Index for active workflow instances
    op.create_index(
        'ix_workflow_instances_status',
        'workflow_instances',
        ['current_state', 'status', 'created_at'],
        postgresql_where=sa.text("status = 'active'")
    )

    # Index for entity workflows
    op.create_index(
        'ix_workflow_instances_entity',
        'workflow_instances',
        ['entity_type', 'entity_id', 'status'],
    )

    # Index for workflow history by instance
    op.create_index(
        'ix_workflow_history_instance',
        'workflow_history',
        ['instance_id', 'created_at'],
    )

    # ==================== ANALYTICS INDEXES ====================

    # Index for metric snapshots by organization and date
    op.create_index(
        'ix_metric_snapshots_org_time',
        'metric_snapshots',
        ['organization_id', 'timestamp'],
    )

    # Index for KPI tracking
    op.create_index(
        'ix_kpis_org_category',
        'kpis',
        ['organization_id', 'category', 'created_at'],
    )

    # Index for dashboard widgets
    op.create_index(
        'ix_dashboard_widgets_dashboard',
        'dashboard_widgets',
        ['dashboard_id', 'position'],
    )

    # ==================== AUDIT INDEXES ====================

    # Index for audit logs by entity
    op.create_index(
        'ix_audit_logs_entity',
        'audit_logs',
        ['entity_type', 'entity_id', 'created_at'],
    )

    # Index for audit logs by user
    op.create_index(
        'ix_audit_logs_user_date',
        'audit_logs',
        ['user_id', 'created_at'],
        postgresql_where=sa.text('user_id IS NOT NULL')
    )

    # Index for audit logs by organization and action
    op.create_index(
        'ix_audit_logs_org_action',
        'audit_logs',
        ['organization_id', 'action', 'created_at'],
    )

    # ==================== ORGANIZATION INDEXES ====================

    # Index for active organizations
    op.create_index(
        'ix_organizations_active',
        'organizations',
        ['is_active', 'created_at'],
        postgresql_where=sa.text('is_active = true')
    )

    # Index for organization search by name
    op.create_index(
        'ix_organizations_name_search',
        'organizations',
        [sa.text('LOWER(name)')],
    )


def downgrade() -> None:
    """
    Remove performance indexes
    """

    # Organization indexes
    op.drop_index('ix_organizations_name_search', table_name='organizations')
    op.drop_index('ix_organizations_active', table_name='organizations')

    # Audit indexes
    op.drop_index('ix_audit_logs_org_action', table_name='audit_logs')
    op.drop_index('ix_audit_logs_user_date', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity', table_name='audit_logs')

    # Analytics indexes
    op.drop_index('ix_dashboard_widgets_dashboard', table_name='dashboard_widgets')
    op.drop_index('ix_kpis_org_category', table_name='kpis')
    op.drop_index('ix_metric_snapshots_org_time', table_name='metric_snapshots')

    # Workflow indexes
    op.drop_index('ix_workflow_history_instance', table_name='workflow_history')
    op.drop_index('ix_workflow_instances_entity', table_name='workflow_instances')
    op.drop_index('ix_workflow_instances_status', table_name='workflow_instances')

    # Ticket indexes
    op.drop_index('ix_tickets_org_date', table_name='tickets')
    op.drop_index('ix_tickets_number', table_name='tickets')
    op.drop_index('ix_tickets_sla_breach', table_name='tickets')
    op.drop_index('ix_tickets_assigned_status', table_name='tickets')
    op.drop_index('ix_tickets_status_priority', table_name='tickets')

    # Route indexes
    op.drop_index('ix_routes_courier_status', table_name='routes')
    op.drop_index('ix_routes_status_date', table_name='routes')

    # Delivery indexes
    op.drop_index('ix_deliveries_org_date', table_name='deliveries')
    op.drop_index('ix_deliveries_tracking_number', table_name='deliveries')
    op.drop_index('ix_deliveries_sla', table_name='deliveries')
    op.drop_index('ix_deliveries_courier_status', table_name='deliveries')
    op.drop_index('ix_deliveries_status_date', table_name='deliveries')

    # Vehicle indexes
    op.drop_index('ix_vehicles_type_org', table_name='vehicles')
    op.drop_index('ix_vehicles_assigned_to', table_name='vehicles')
    op.drop_index('ix_vehicles_org_status', table_name='vehicles')

    # Courier indexes
    op.drop_index('ix_couriers_location', table_name='couriers')
    op.drop_index('ix_couriers_user_org', table_name='couriers')
    op.drop_index('ix_couriers_org_status', table_name='couriers')

    # User indexes
    op.drop_index('ix_users_name_search', table_name='users')
    op.drop_index('ix_users_org_active', table_name='users')
    op.drop_index('ix_users_email_lower', table_name='users')
