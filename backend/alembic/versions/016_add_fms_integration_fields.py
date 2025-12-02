"""Add FMS integration fields to couriers and vehicles

Revision ID: 016
Revises: 015
Create Date: 2024-12-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '016'
down_revision = '015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add FMS fields to couriers table
    op.add_column('couriers', sa.Column('fms_asset_id', sa.Integer(), nullable=True))
    op.add_column('couriers', sa.Column('fms_driver_id', sa.Integer(), nullable=True))
    op.add_column('couriers', sa.Column('fms_last_sync', sa.String(50), nullable=True))
    op.create_index('ix_couriers_fms_asset_id', 'couriers', ['fms_asset_id'], unique=True)

    # Add FMS fields to vehicles table
    op.add_column('vehicles', sa.Column('fms_asset_id', sa.Integer(), nullable=True))
    op.add_column('vehicles', sa.Column('fms_tracking_unit_id', sa.Integer(), nullable=True))
    op.add_column('vehicles', sa.Column('fms_last_sync', sa.String(50), nullable=True))
    op.create_index('ix_vehicles_fms_asset_id', 'vehicles', ['fms_asset_id'], unique=True)


def downgrade() -> None:
    # Remove from vehicles
    op.drop_index('ix_vehicles_fms_asset_id', table_name='vehicles')
    op.drop_column('vehicles', 'fms_last_sync')
    op.drop_column('vehicles', 'fms_tracking_unit_id')
    op.drop_column('vehicles', 'fms_asset_id')

    # Remove from couriers
    op.drop_index('ix_couriers_fms_asset_id', table_name='couriers')
    op.drop_column('couriers', 'fms_last_sync')
    op.drop_column('couriers', 'fms_driver_id')
    op.drop_column('couriers', 'fms_asset_id')
