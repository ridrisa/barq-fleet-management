"""Add password reset tokens table

Revision ID: 019
Revises: 018
Create Date: 2025-12-03

This migration creates the password_reset_tokens table for secure password recovery.

Security features:
- Stores only SHA-256 hashes of tokens (never raw tokens)
- Single-use tokens with 'used' flag
- Automatic expiration tracking
- IP address and user agent for audit trail
- Indexed for performance on token lookups

The raw token is sent to users via email; only the hash is stored in the database.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '019'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column(
            'user_id',
            sa.Integer(),
            sa.ForeignKey('users.id', ondelete='CASCADE'),
            nullable=False
        ),
        sa.Column(
            'token_hash',
            sa.String(256),
            nullable=False,
            unique=True,
            comment='SHA-256 hash of the reset token'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            'expires_at',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='Token expiration timestamp'
        ),
        sa.Column(
            'used',
            sa.Boolean(),
            default=False,
            nullable=False,
            comment='Whether the token has been used'
        ),
        sa.Column(
            'used_at',
            sa.DateTime(timezone=True),
            nullable=True,
            comment='Timestamp when token was used'
        ),
        sa.Column(
            'ip_address',
            sa.String(45),
            nullable=True,
            comment='IP address of requester (IPv6 compatible)'
        ),
        sa.Column(
            'user_agent',
            sa.String(500),
            nullable=True,
            comment='User agent of requester'
        ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for performance
    op.create_index(
        'ix_password_reset_tokens_id',
        'password_reset_tokens',
        ['id']
    )
    op.create_index(
        'ix_password_reset_tokens_user_id',
        'password_reset_tokens',
        ['user_id']
    )
    op.create_index(
        'ix_password_reset_tokens_token_hash',
        'password_reset_tokens',
        ['token_hash'],
        unique=True
    )
    op.create_index(
        'ix_password_reset_tokens_user_id_used',
        'password_reset_tokens',
        ['user_id', 'used']
    )
    op.create_index(
        'ix_password_reset_tokens_expires_at',
        'password_reset_tokens',
        ['expires_at']
    )

    print("Created password_reset_tokens table with indexes")


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_password_reset_tokens_expires_at', 'password_reset_tokens')
    op.drop_index('ix_password_reset_tokens_user_id_used', 'password_reset_tokens')
    op.drop_index('ix_password_reset_tokens_token_hash', 'password_reset_tokens')
    op.drop_index('ix_password_reset_tokens_user_id', 'password_reset_tokens')
    op.drop_index('ix_password_reset_tokens_id', 'password_reset_tokens')

    # Drop table
    op.drop_table('password_reset_tokens')

    print("Dropped password_reset_tokens table")
