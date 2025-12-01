"""Add Google OAuth fields to users table

Revision ID: 003
Revises: 002
Create Date: 2025-11-06 15:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make hashed_password nullable for Google OAuth users
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.VARCHAR(),
                    nullable=True)

    # Add Google OAuth fields
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('picture', sa.String(), nullable=True))

    # Create indexes
    op.create_index(op.f('ix_users_google_id'), 'users', ['google_id'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_users_google_id'), table_name='users')

    # Drop Google OAuth fields
    op.drop_column('users', 'picture')
    op.drop_column('users', 'google_id')

    # Make hashed_password not nullable again
    op.alter_column('users', 'hashed_password',
                    existing_type=sa.VARCHAR(),
                    nullable=False)
