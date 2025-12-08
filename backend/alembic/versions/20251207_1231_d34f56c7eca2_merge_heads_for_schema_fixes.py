"""merge_heads_for_schema_fixes

Revision ID: d34f56c7eca2
Revises: 20250106_001, perf_001
Create Date: 2025-12-07 12:31:57.826269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd34f56c7eca2'
down_revision = ('20250106_001', 'perf_001')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
