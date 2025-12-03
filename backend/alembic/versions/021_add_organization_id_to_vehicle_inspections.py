"""Add organization_id to vehicle_inspections table

Revision ID: 021
Revises: 020
Create Date: 2025-01-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '021'
down_revision: Union[str, None] = '020'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Get default organization ID
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT id FROM organizations LIMIT 1"))
    row = result.fetchone()
    default_org_id = row[0] if row else 1

    # Add organization_id column to vehicle_inspections
    op.add_column(
        'vehicle_inspections',
        sa.Column('organization_id', sa.Integer(), nullable=True)
    )

    # Update existing rows with default organization
    op.execute(f"UPDATE vehicle_inspections SET organization_id = {default_org_id}")

    # Make column NOT NULL and add foreign key
    op.alter_column('vehicle_inspections', 'organization_id', nullable=False)
    op.create_foreign_key(
        'fk_vehicle_inspections_organization',
        'vehicle_inspections', 'organizations',
        ['organization_id'], ['id'],
        ondelete='CASCADE'
    )

    # Create index for performance
    op.create_index(
        'ix_vehicle_inspections_organization_id',
        'vehicle_inspections',
        ['organization_id']
    )


def downgrade() -> None:
    op.drop_index('ix_vehicle_inspections_organization_id', table_name='vehicle_inspections')
    op.drop_constraint('fk_vehicle_inspections_organization', 'vehicle_inspections', type_='foreignkey')
    op.drop_column('vehicle_inspections', 'organization_id')
