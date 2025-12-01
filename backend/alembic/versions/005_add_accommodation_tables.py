"""Add accommodation tables

Revision ID: 005
Revises: 004
Create Date: 2025-11-06 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Buildings table
    op.create_table(
        'buildings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('total_rooms', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_capacity', sa.Integer(), server_default='0', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_buildings_name', 'buildings', ['name'], unique=True)

    # Create Rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('building_id', sa.Integer(), nullable=False),
        sa.Column('room_number', sa.String(), nullable=False),
        sa.Column('capacity', sa.Integer(), nullable=False),
        sa.Column('occupied', sa.Integer(), server_default='0', nullable=False),
        sa.Column('status', sa.Enum('available', 'occupied', 'maintenance', name='roomstatus'),
                  server_default='available', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('building_id', 'room_number', name='uq_room_building_number')
    )
    op.create_index('ix_rooms_building_id', 'rooms', ['building_id'])
    op.create_index('ix_rooms_status', 'rooms', ['status'])

    # Create Beds table
    op.create_table(
        'beds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_id', sa.Integer(), nullable=False),
        sa.Column('bed_number', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('available', 'occupied', 'reserved', name='bedstatus'),
                  server_default='available', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('room_id', 'bed_number', name='uq_bed_room_number')
    )
    op.create_index('ix_beds_room_id', 'beds', ['room_id'])
    op.create_index('ix_beds_status', 'beds', ['status'])

    # Create Allocations table
    op.create_table(
        'allocations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('bed_id', sa.Integer(), nullable=False),
        sa.Column('allocation_date', sa.Date(), nullable=False),
        sa.Column('release_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bed_id'], ['beds.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_allocations_courier_id', 'allocations', ['courier_id'])
    op.create_index('ix_allocations_bed_id', 'allocations', ['bed_id'])
    op.create_index('ix_allocations_allocation_date', 'allocations', ['allocation_date'])
    op.create_index('ix_allocations_active', 'allocations', ['courier_id', 'release_date'])


def downgrade() -> None:
    # Drop Allocations table
    op.drop_index('ix_allocations_active', table_name='allocations')
    op.drop_index('ix_allocations_allocation_date', table_name='allocations')
    op.drop_index('ix_allocations_bed_id', table_name='allocations')
    op.drop_index('ix_allocations_courier_id', table_name='allocations')
    op.drop_table('allocations')

    # Drop Beds table
    op.drop_index('ix_beds_status', table_name='beds')
    op.drop_index('ix_beds_room_id', table_name='beds')
    op.drop_table('beds')
    op.execute('DROP TYPE IF EXISTS bedstatus')

    # Drop Rooms table
    op.drop_index('ix_rooms_status', table_name='rooms')
    op.drop_index('ix_rooms_building_id', table_name='rooms')
    op.drop_table('rooms')
    op.execute('DROP TYPE IF EXISTS roomstatus')

    # Drop Buildings table
    op.drop_index('ix_buildings_name', table_name='buildings')
    op.drop_table('buildings')
