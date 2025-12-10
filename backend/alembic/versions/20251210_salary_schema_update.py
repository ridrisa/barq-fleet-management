"""Add missing salary columns and payroll tables

Revision ID: salary_schema_update
Revises: fix_courier_accom_fks
Create Date: 2025-12-10

Based on salary.txt specification for category-based payroll calculation.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'salary_schema_update'
down_revision = 'fix_courier_accom_fks'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ===========================================
    # 1. Add missing columns to salaries table
    # ===========================================

    # Category-based payroll fields
    op.add_column('salaries', sa.Column('category', sa.String(50), nullable=True,
                  comment='Payroll category: Motorcycle, Food Trial, Food In-House New/Old, Ecommerce WH, Ecommerce'))

    # Period dates (25th to 24th calculation period)
    op.add_column('salaries', sa.Column('period_start', sa.Date(), nullable=True,
                  comment='Calculation period start date'))
    op.add_column('salaries', sa.Column('period_end', sa.Date(), nullable=True,
                  comment='Calculation period end date'))

    # Performance metrics (from BigQuery)
    op.add_column('salaries', sa.Column('total_orders', sa.Integer(), nullable=True, server_default='0',
                  comment='Total orders in period'))
    op.add_column('salaries', sa.Column('total_revenue', sa.Numeric(12, 2), nullable=True, server_default='0',
                  comment='Total revenue in period'))
    op.add_column('salaries', sa.Column('gas_usage', sa.Numeric(10, 2), nullable=True, server_default='0',
                  comment='Actual gas usage (without VAT)'))

    # Target and calculation
    op.add_column('salaries', sa.Column('target', sa.Numeric(10, 2), nullable=True, server_default='0',
                  comment='Final calculated target'))
    op.add_column('salaries', sa.Column('daily_target', sa.Numeric(10, 2), nullable=True, server_default='0',
                  comment='Daily target from config'))
    op.add_column('salaries', sa.Column('days_since_joining', sa.Integer(), nullable=True, server_default='0',
                  comment='Days since joining as of period end'))

    # Salary components (category-based)
    op.add_column('salaries', sa.Column('bonus_amount', sa.Numeric(10, 2), nullable=True, server_default='0',
                  comment='Performance bonus (can be negative = penalty)'))

    # Gas/Fuel components
    op.add_column('salaries', sa.Column('gas_deserved', sa.Numeric(10, 2), nullable=True, server_default='0',
                  comment='Calculated gas allowance'))
    op.add_column('salaries', sa.Column('gas_difference', sa.Numeric(10, 2), nullable=True, server_default='0',
                  comment='gas_deserved - gas_usage'))

    # Payment tracking
    op.add_column('salaries', sa.Column('is_paid', sa.Integer(), nullable=True, server_default='0',
                  comment='Payment status: 0=unpaid, 1=paid'))

    # Audit fields
    op.add_column('salaries', sa.Column('calculation_details', sa.Text(), nullable=True,
                  comment='JSON with detailed calculation breakdown'))
    op.add_column('salaries', sa.Column('generated_date', sa.Date(), nullable=True,
                  comment='When salary was calculated'))

    # ===========================================
    # 2. Create payroll_parameters table
    # ===========================================
    op.create_table(
        'payroll_parameters',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('basic_salary_rate', sa.Numeric(12, 6), nullable=False, server_default='0'),
        sa.Column('bonus_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('penalty_rate', sa.Numeric(10, 2), nullable=True, server_default='10'),
        sa.Column('gas_rate', sa.Numeric(10, 6), nullable=True),
        sa.Column('gas_cap', sa.Numeric(10, 2), nullable=True),
        sa.Column('revenue_coefficient', sa.Numeric(12, 10), nullable=True),
        sa.Column('daily_order_divisor', sa.Numeric(10, 6), nullable=True),
        sa.Column('tier_threshold', sa.Integer(), nullable=True),
        sa.Column('tier_1_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('tier_2_rate', sa.Numeric(10, 2), nullable=True),
        sa.Column('bonus_revenue_threshold', sa.Numeric(10, 2), nullable=True),
        sa.Column('bonus_rate_below_threshold', sa.Numeric(10, 4), nullable=True),
        sa.Column('bonus_rate_above_threshold', sa.Numeric(10, 4), nullable=True),
        sa.Column('fuel_revenue_coefficient', sa.Numeric(10, 6), nullable=True),
        sa.Column('fuel_target_coefficient', sa.Numeric(10, 6), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('category', 'organization_id', name='uq_payroll_params_category')
    )
    op.create_index('ix_payroll_parameters_id', 'payroll_parameters', ['id'])
    op.create_index('ix_payroll_parameters_organization_id', 'payroll_parameters', ['organization_id'])
    op.create_index('ix_payroll_parameters_category', 'payroll_parameters', ['category'])

    # ===========================================
    # 3. Create courier_targets table
    # ===========================================
    op.create_table(
        'courier_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('daily_target', sa.Numeric(10, 2), nullable=False, server_default='0'),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('courier_id', 'month', 'year', 'organization_id', name='uq_courier_target_period')
    )
    op.create_index('ix_courier_targets_id', 'courier_targets', ['id'])
    op.create_index('ix_courier_targets_courier_id', 'courier_targets', ['courier_id'])
    op.create_index('ix_courier_targets_organization_id', 'courier_targets', ['organization_id'])
    op.create_index('ix_courier_targets_period', 'courier_targets', ['year', 'month'])

    # ===========================================
    # 4. Insert default payroll parameters
    # ===========================================
    # Note: These will be inserted for organization_id=1 (default org)
    # In production, each organization should configure their own parameters

    op.execute("""
        INSERT INTO payroll_parameters (category, basic_salary_rate, bonus_rate, penalty_rate, gas_rate, gas_cap, daily_order_divisor, organization_id)
        VALUES
            ('Motorcycle', 53.33333, 6, 10, 0.65, 261, 13.333, 1),
            ('Food Trial', 66.66666667, 7, 10, 2.11, 826, 13, 1),
            ('Food In-House New', 66.66666667, 7, 10, 1.739, 826, 15.83333333, 1),
            ('Food In-House Old', 66.66666667, NULL, 10, 2.065, 826, 15.83333333, 1),
            ('Ecommerce WH', 66.666667, 8, 10, 15.03, 452, 16.6666667, 1),
            ('Ecommerce', 66.66666667, NULL, NULL, NULL, 452, 221, 1)
        ON CONFLICT DO NOTHING
    """)

    # Update Food In-House Old with tier rates
    op.execute("""
        UPDATE payroll_parameters
        SET tier_threshold = 199, tier_1_rate = 6, tier_2_rate = 9
        WHERE category = 'Food In-House Old'
    """)

    # Update Ecommerce with special rates
    op.execute("""
        UPDATE payroll_parameters
        SET revenue_coefficient = 0.3016591252,
            bonus_revenue_threshold = 4000,
            bonus_rate_below_threshold = 0.55,
            bonus_rate_above_threshold = 0.5,
            fuel_revenue_coefficient = 0.068,
            fuel_target_coefficient = 15.06
        WHERE category = 'Ecommerce'
    """)


def downgrade() -> None:
    # Drop tables
    op.drop_table('courier_targets')
    op.drop_table('payroll_parameters')

    # Drop columns from salaries
    op.drop_column('salaries', 'generated_date')
    op.drop_column('salaries', 'calculation_details')
    op.drop_column('salaries', 'is_paid')
    op.drop_column('salaries', 'gas_difference')
    op.drop_column('salaries', 'gas_deserved')
    op.drop_column('salaries', 'bonus_amount')
    op.drop_column('salaries', 'days_since_joining')
    op.drop_column('salaries', 'daily_target')
    op.drop_column('salaries', 'target')
    op.drop_column('salaries', 'gas_usage')
    op.drop_column('salaries', 'total_revenue')
    op.drop_column('salaries', 'total_orders')
    op.drop_column('salaries', 'period_end')
    op.drop_column('salaries', 'period_start')
    op.drop_column('salaries', 'category')
