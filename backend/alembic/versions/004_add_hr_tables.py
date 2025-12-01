"""Add HR tables

Revision ID: 004
Revises: 003
Create Date: 2025-11-06 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create Leave table
    op.create_table(
        'leaves',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('leave_type', sa.Enum('annual', 'sick', 'emergency', 'unpaid', name='leavetype'), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('days', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'cancelled', name='leavestatus'),
                  server_default='pending', nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leaves_courier_id', 'leaves', ['courier_id'])
    op.create_index('ix_leaves_status', 'leaves', ['status'])
    op.create_index('ix_leaves_start_date', 'leaves', ['start_date'])

    # Create Attendance table
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('check_in', sa.Time(), nullable=True),
        sa.Column('check_out', sa.Time(), nullable=True),
        sa.Column('status', sa.Enum('present', 'absent', 'late', 'half_day', 'on_leave', name='attendancestatus'), nullable=False),
        sa.Column('hours_worked', sa.Integer(), server_default='0', nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('courier_id', 'date', name='uq_attendance_courier_date')
    )
    op.create_index('ix_attendance_courier_id', 'attendance', ['courier_id'])
    op.create_index('ix_attendance_date', 'attendance', ['date'])
    op.create_index('ix_attendance_status', 'attendance', ['status'])

    # Create Loans table
    op.create_table(
        'loans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('outstanding_balance', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('monthly_deduction', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('active', 'completed', 'cancelled', name='loanstatus'),
                  server_default='active', nullable=False),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_loans_courier_id', 'loans', ['courier_id'])
    op.create_index('ix_loans_status', 'loans', ['status'])

    # Create Salaries table
    op.create_table(
        'salaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('base_salary', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('allowances', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('deductions', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('loan_deduction', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('gosi_employee', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('gross_salary', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('net_salary', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('courier_id', 'month', 'year', name='uq_salary_courier_month_year')
    )
    op.create_index('ix_salaries_courier_id', 'salaries', ['courier_id'])
    op.create_index('ix_salaries_month_year', 'salaries', ['month', 'year'])

    # Create Assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_type', sa.Enum('uniform', 'mobile_device', 'equipment', 'tools', name='assettype'), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('return_date', sa.Date(), nullable=True),
        sa.Column('condition', sa.String(), server_default='good', nullable=False),
        sa.Column('status', sa.Enum('assigned', 'returned', 'damaged', 'lost', name='assetstatus'),
                  server_default='assigned', nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_assets_courier_id', 'assets', ['courier_id'])
    op.create_index('ix_assets_status', 'assets', ['status'])
    op.create_index('ix_assets_asset_type', 'assets', ['asset_type'])


def downgrade() -> None:
    # Drop Assets table
    op.drop_index('ix_assets_asset_type', table_name='assets')
    op.drop_index('ix_assets_status', table_name='assets')
    op.drop_index('ix_assets_courier_id', table_name='assets')
    op.drop_table('assets')
    op.execute('DROP TYPE IF EXISTS assetstatus')
    op.execute('DROP TYPE IF EXISTS assettype')

    # Drop Salaries table
    op.drop_index('ix_salaries_month_year', table_name='salaries')
    op.drop_index('ix_salaries_courier_id', table_name='salaries')
    op.drop_table('salaries')

    # Drop Loans table
    op.drop_index('ix_loans_status', table_name='loans')
    op.drop_index('ix_loans_courier_id', table_name='loans')
    op.drop_table('loans')
    op.execute('DROP TYPE IF EXISTS loanstatus')

    # Drop Attendance table
    op.drop_index('ix_attendance_status', table_name='attendance')
    op.drop_index('ix_attendance_date', table_name='attendance')
    op.drop_index('ix_attendance_courier_id', table_name='attendance')
    op.drop_table('attendance')
    op.execute('DROP TYPE IF EXISTS attendancestatus')

    # Drop Leave table
    op.drop_index('ix_leaves_start_date', table_name='leaves')
    op.drop_index('ix_leaves_status', table_name='leaves')
    op.drop_index('ix_leaves_courier_id', table_name='leaves')
    op.drop_table('leaves')
    op.execute('DROP TYPE IF EXISTS leavestatus')
    op.execute('DROP TYPE IF EXISTS leavetype')
