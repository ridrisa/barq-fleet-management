"""Add Operations tables

Revision ID: 006
Revises: 005
Create Date: 2025-11-06 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Deliveries table
    op.create_table(
        'deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tracking_number', sa.String(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('pickup_address', sa.Text(), nullable=False),
        sa.Column('delivery_address', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'in_transit', 'delivered', 'failed', 'returned', name='deliverystatus'),
                  server_default='pending', nullable=False),
        sa.Column('pickup_time', sa.DateTime(), nullable=True),
        sa.Column('delivery_time', sa.DateTime(), nullable=True),
        sa.Column('cod_amount', sa.Integer(), server_default='0', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tracking_number', name='uq_delivery_tracking_number')
    )
    op.create_index('ix_deliveries_courier_id', 'deliveries', ['courier_id'])
    op.create_index('ix_deliveries_status', 'deliveries', ['status'])
    op.create_index('ix_deliveries_tracking_number', 'deliveries', ['tracking_number'])
    op.create_index('ix_deliveries_created_at', 'deliveries', ['created_at'])

    # Create Routes table
    op.create_table(
        'routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('route_name', sa.String(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('waypoints', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_distance', sa.Integer(), nullable=True),
        sa.Column('estimated_time', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_routes_courier_id', 'routes', ['courier_id'])
    op.create_index('ix_routes_date', 'routes', ['date'])
    op.create_index('ix_routes_courier_date', 'routes', ['courier_id', 'date'])

    # Create COD Transactions table
    op.create_table(
        'cod_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('collection_date', sa.Date(), nullable=False),
        sa.Column('deposit_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'collected', 'deposited', 'reconciled', name='codstatus'),
                  server_default='pending', nullable=False),
        sa.Column('reference_number', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_cod_transactions_courier_id', 'cod_transactions', ['courier_id'])
    op.create_index('ix_cod_transactions_status', 'cod_transactions', ['status'])
    op.create_index('ix_cod_transactions_collection_date', 'cod_transactions', ['collection_date'])

    # Create Incidents table
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_type', sa.Enum('accident', 'theft', 'damage', 'violation', 'other', name='incidenttype'), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=True),
        sa.Column('vehicle_id', sa.Integer(), nullable=True),
        sa.Column('incident_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.Enum('reported', 'investigating', 'resolved', 'closed', name='incidentstatus'),
                  server_default='reported', nullable=False),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('cost', sa.Integer(), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_incidents_courier_id', 'incidents', ['courier_id'])
    op.create_index('ix_incidents_vehicle_id', 'incidents', ['vehicle_id'])
    op.create_index('ix_incidents_status', 'incidents', ['status'])
    op.create_index('ix_incidents_incident_type', 'incidents', ['incident_type'])
    op.create_index('ix_incidents_incident_date', 'incidents', ['incident_date'])


def downgrade() -> None:
    # Drop Incidents table
    op.drop_index('ix_incidents_incident_date', table_name='incidents')
    op.drop_index('ix_incidents_incident_type', table_name='incidents')
    op.drop_index('ix_incidents_status', table_name='incidents')
    op.drop_index('ix_incidents_vehicle_id', table_name='incidents')
    op.drop_index('ix_incidents_courier_id', table_name='incidents')
    op.drop_table('incidents')
    op.execute('DROP TYPE IF EXISTS incidentstatus')
    op.execute('DROP TYPE IF EXISTS incidenttype')

    # Drop COD Transactions table
    op.drop_index('ix_cod_transactions_collection_date', table_name='cod_transactions')
    op.drop_index('ix_cod_transactions_status', table_name='cod_transactions')
    op.drop_index('ix_cod_transactions_courier_id', table_name='cod_transactions')
    op.drop_table('cod_transactions')
    op.execute('DROP TYPE IF EXISTS codstatus')

    # Drop Routes table
    op.drop_index('ix_routes_courier_date', table_name='routes')
    op.drop_index('ix_routes_date', table_name='routes')
    op.drop_index('ix_routes_courier_id', table_name='routes')
    op.drop_table('routes')

    # Drop Deliveries table
    op.drop_index('ix_deliveries_created_at', table_name='deliveries')
    op.drop_index('ix_deliveries_tracking_number', table_name='deliveries')
    op.drop_index('ix_deliveries_status', table_name='deliveries')
    op.drop_index('ix_deliveries_courier_id', table_name='deliveries')
    op.drop_table('deliveries')
    op.execute('DROP TYPE IF EXISTS deliverystatus')
