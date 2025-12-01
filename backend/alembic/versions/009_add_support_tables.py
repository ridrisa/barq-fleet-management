"""Add Support tables

Revision ID: 009
Revises: 008
Create Date: 2025-11-06 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing enum types if they exist (from failed migration attempts)
    op.execute('DROP TYPE IF EXISTS ticketcategory CASCADE')
    op.execute('DROP TYPE IF EXISTS ticketpriority CASCADE')
    op.execute('DROP TYPE IF EXISTS ticketstatus CASCADE')

    # Define enum types (SQLAlchemy will auto-create them when creating the table)
    ticket_category_enum = postgresql.ENUM(
        'hr', 'vehicle', 'accommodation', 'finance', 'operations', 'it', 'other',
        name='ticketcategory',
        create_type=True
    )

    ticket_priority_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'urgent',
        name='ticketpriority',
        create_type=True
    )

    ticket_status_enum = postgresql.ENUM(
        'open', 'in_progress', 'pending', 'resolved', 'closed',
        name='ticketstatus',
        create_type=True
    )

    # Create Tickets table
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticket_id', sa.String(50), nullable=False, unique=True,
                  comment='Unique ticket identifier (e.g., TKT-20250106-001)'),
        sa.Column('courier_id', sa.Integer(), nullable=True,
                  comment='Related courier (nullable for non-courier issues)'),
        sa.Column('created_by', sa.Integer(), nullable=False,
                  comment='User who created the ticket'),
        sa.Column('assigned_to', sa.Integer(), nullable=True,
                  comment='User assigned to handle the ticket'),
        sa.Column('category', ticket_category_enum, nullable=False,
                  comment='Ticket category for routing'),
        sa.Column('priority', ticket_priority_enum, server_default='medium', nullable=False,
                  comment='Ticket priority level'),
        sa.Column('status', ticket_status_enum, server_default='open', nullable=False,
                  comment='Current ticket status'),
        sa.Column('subject', sa.String(255), nullable=False,
                  comment='Ticket subject/title'),
        sa.Column('description', sa.Text(), nullable=False,
                  comment='Detailed description of the issue'),
        sa.Column('resolution', sa.Text(), nullable=True,
                  comment='Resolution details when ticket is resolved'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True,
                  comment='When ticket was resolved'),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True,
                  comment='When ticket was closed'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),

        # Foreign keys
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),

        # Primary key
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for optimized queries
    op.create_index('ix_tickets_ticket_id', 'tickets', ['ticket_id'], unique=True)
    op.create_index('ix_tickets_courier_id', 'tickets', ['courier_id'])
    op.create_index('ix_tickets_created_by', 'tickets', ['created_by'])
    op.create_index('ix_tickets_assigned_to', 'tickets', ['assigned_to'])
    op.create_index('ix_tickets_category', 'tickets', ['category'])
    op.create_index('ix_tickets_priority', 'tickets', ['priority'])
    op.create_index('ix_tickets_status', 'tickets', ['status'])
    op.create_index('ix_tickets_created_at', 'tickets', ['created_at'])

    # Composite indexes for common queries
    op.create_index('ix_tickets_status_priority', 'tickets', ['status', 'priority'])
    op.create_index('ix_tickets_category_status', 'tickets', ['category', 'status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_tickets_category_status', table_name='tickets')
    op.drop_index('ix_tickets_status_priority', table_name='tickets')
    op.drop_index('ix_tickets_created_at', table_name='tickets')
    op.drop_index('ix_tickets_status', table_name='tickets')
    op.drop_index('ix_tickets_priority', table_name='tickets')
    op.drop_index('ix_tickets_category', table_name='tickets')
    op.drop_index('ix_tickets_assigned_to', table_name='tickets')
    op.drop_index('ix_tickets_created_by', table_name='tickets')
    op.drop_index('ix_tickets_courier_id', table_name='tickets')
    op.drop_index('ix_tickets_ticket_id', table_name='tickets')

    # Drop table
    op.drop_table('tickets')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS ticketstatus')
    op.execute('DROP TYPE IF EXISTS ticketpriority')
    op.execute('DROP TYPE IF EXISTS ticketcategory')
