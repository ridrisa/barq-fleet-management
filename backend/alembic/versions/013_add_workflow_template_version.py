"""Add workflow template version column

Revision ID: 013
Revises: 012
Create Date: 2025-12-01 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '013'
down_revision: Union[str, None] = '012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add version column to workflow_templates
    op.add_column('workflow_templates', sa.Column('version', sa.Integer(), server_default='1', nullable=True))

    # Add parent_template_id column for versioning/cloning
    op.add_column('workflow_templates', sa.Column('parent_template_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('workflow_templates', 'parent_template_id')
    op.drop_column('workflow_templates', 'version')
