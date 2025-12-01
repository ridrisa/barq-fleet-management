"""Add Tenant tables

Revision ID: 010
Revises: 009
Create Date: 2025-11-06 16:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = '010'
down_revision = '009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column(
            'subscription_plan',
            sa.Enum('FREE', 'BASIC', 'PROFESSIONAL', 'ENTERPRISE', name='subscriptionplan'),
            nullable=False,
            server_default='FREE'
        ),
        sa.Column(
            'subscription_status',
            sa.Enum('TRIAL', 'ACTIVE', 'SUSPENDED', 'CANCELLED', name='subscriptionstatus'),
            nullable=False,
            server_default='TRIAL'
        ),
        sa.Column('max_users', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('max_couriers', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('max_vehicles', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('settings', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for organizations
    op.create_index('ix_organizations_id', 'organizations', ['id'])
    op.create_index('ix_organizations_name', 'organizations', ['name'], unique=True)
    op.create_index('ix_organizations_slug', 'organizations', ['slug'], unique=True)
    op.create_index('ix_organizations_is_active', 'organizations', ['is_active'])
    op.create_index('ix_organizations_subscription_plan', 'organizations', ['subscription_plan'])
    op.create_index('ix_organizations_subscription_status', 'organizations', ['subscription_status'])

    # Create organization_users table
    op.create_table(
        'organization_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column(
            'role',
            sa.Enum('OWNER', 'ADMIN', 'MANAGER', 'VIEWER', name='organizationrole'),
            nullable=False,
            server_default='VIEWER'
        ),
        sa.Column('permissions', JSON, nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'user_id', name='uq_organization_user')
    )

    # Create indexes for organization_users
    op.create_index('ix_organization_users_id', 'organization_users', ['id'])
    op.create_index('ix_organization_users_organization_id', 'organization_users', ['organization_id'])
    op.create_index('ix_organization_users_user_id', 'organization_users', ['user_id'])
    op.create_index('ix_organization_users_role', 'organization_users', ['role'])
    op.create_index('ix_organization_users_is_active', 'organization_users', ['is_active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_organization_users_is_active', 'organization_users')
    op.drop_index('ix_organization_users_role', 'organization_users')
    op.drop_index('ix_organization_users_user_id', 'organization_users')
    op.drop_index('ix_organization_users_organization_id', 'organization_users')
    op.drop_index('ix_organization_users_id', 'organization_users')

    op.drop_index('ix_organizations_subscription_status', 'organizations')
    op.drop_index('ix_organizations_subscription_plan', 'organizations')
    op.drop_index('ix_organizations_is_active', 'organizations')
    op.drop_index('ix_organizations_slug', 'organizations')
    op.drop_index('ix_organizations_name', 'organizations')
    op.drop_index('ix_organizations_id', 'organizations')

    # Drop tables
    op.drop_table('organization_users')
    op.drop_table('organizations')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS organizationrole')
    op.execute('DROP TYPE IF EXISTS subscriptionstatus')
    op.execute('DROP TYPE IF EXISTS subscriptionplan')
