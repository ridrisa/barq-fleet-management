
"""Add Analytics tables

Revision ID: 008
Revises: 007
Create Date: 2025-11-06 16:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PerformanceData table
    op.create_table(
        'performance_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),

        # Order Metrics
        sa.Column('orders_completed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('orders_failed', sa.Integer(), server_default='0', nullable=False),
        sa.Column('on_time_deliveries', sa.Integer(), server_default='0', nullable=False),
        sa.Column('late_deliveries', sa.Integer(), server_default='0', nullable=False),

        # Distance & Revenue
        sa.Column('distance_covered_km', sa.Numeric(precision=10, scale=2), server_default='0.0', nullable=False),
        sa.Column('revenue_generated', sa.Numeric(precision=12, scale=2), server_default='0.0', nullable=False),
        sa.Column('cod_collected', sa.Numeric(precision=12, scale=2), server_default='0.0', nullable=False),

        # Quality Metrics
        sa.Column('average_rating', sa.Numeric(precision=3, scale=2), server_default='0.0', nullable=False),

        # Time Metrics
        sa.Column('working_hours', sa.Numeric(precision=5, scale=2), server_default='0.0', nullable=False),

        # Performance Score
        sa.Column('efficiency_score', sa.Numeric(precision=5, scale=2), server_default='0.0', nullable=False),

        # Additional
        sa.Column('notes', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        # Constraints
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('courier_id', 'date', name='uq_performance_courier_date')
    )

    # Create indexes for performance_data
    op.create_index('ix_performance_data_courier_id', 'performance_data', ['courier_id'])
    op.create_index('ix_performance_data_date', 'performance_data', ['date'])
    op.create_index('ix_performance_data_efficiency_score', 'performance_data', ['efficiency_score'])
    op.create_index('ix_performance_data_orders_completed', 'performance_data', ['orders_completed'])
    op.create_index('ix_performance_data_revenue_generated', 'performance_data', ['revenue_generated'])

    # Composite index for date range queries
    op.create_index(
        'ix_performance_data_courier_date_range',
        'performance_data',
        ['courier_id', 'date']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_performance_data_courier_date_range', table_name='performance_data')
    op.drop_index('ix_performance_data_revenue_generated', table_name='performance_data')
    op.drop_index('ix_performance_data_orders_completed', table_name='performance_data')
    op.drop_index('ix_performance_data_efficiency_score', table_name='performance_data')
    op.drop_index('ix_performance_data_date', table_name='performance_data')
    op.drop_index('ix_performance_data_courier_id', table_name='performance_data')

    # Drop table
    op.drop_table('performance_data')
