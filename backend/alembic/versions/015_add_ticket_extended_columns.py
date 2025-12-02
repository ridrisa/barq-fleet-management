"""Add extended ticket columns

Revision ID: 015
Revises: 014
Create Date: 2025-12-02 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '015'
down_revision: Union[str, None] = '014'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create escalation level enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE escalationlevel AS ENUM (
                'none', 'level_1', 'level_2', 'level_3', 'management'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Add SLA tracking columns
    op.add_column('tickets', sa.Column('sla_due_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('first_response_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('sla_breached', sa.Boolean(), server_default='false', nullable=False))

    # Add escalation columns
    op.add_column('tickets', sa.Column('escalation_level',
                                        postgresql.ENUM('none', 'level_1', 'level_2', 'level_3', 'management',
                                                        name='escalationlevel', create_type=False),
                                        server_default='none', nullable=False))
    op.add_column('tickets', sa.Column('escalated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('tickets', sa.Column('escalated_by', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('escalation_reason', sa.Text(), nullable=True))

    # Add merge support columns
    op.add_column('tickets', sa.Column('merged_into_id', sa.Integer(), nullable=True))
    op.add_column('tickets', sa.Column('is_merged', sa.Boolean(), server_default='false', nullable=False))

    # Add template reference
    op.add_column('tickets', sa.Column('template_id', sa.Integer(), nullable=True))

    # Add tags and custom fields
    op.add_column('tickets', sa.Column('tags', sa.Text(), nullable=True))
    op.add_column('tickets', sa.Column('custom_fields', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Add contact information
    op.add_column('tickets', sa.Column('contact_email', sa.String(255), nullable=True))
    op.add_column('tickets', sa.Column('contact_phone', sa.String(50), nullable=True))

    # Add department routing
    op.add_column('tickets', sa.Column('department', sa.String(100), nullable=True))

    # Add foreign key constraints
    op.create_foreign_key('fk_tickets_escalated_by', 'tickets', 'users',
                          ['escalated_by'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_tickets_merged_into', 'tickets', 'tickets',
                          ['merged_into_id'], ['id'], ondelete='SET NULL')

    # Create ticket_templates table if it doesn't exist (for template_id FK)
    # First check if it exists
    op.execute("""
        CREATE TABLE IF NOT EXISTS ticket_templates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category ticketcategory NOT NULL,
            priority ticketpriority DEFAULT 'medium',
            subject_template VARCHAR(255),
            body_template TEXT,
            tags TEXT,
            auto_assign_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
            sla_hours INTEGER DEFAULT 24,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMP WITH TIME ZONE
        )
    """)

    op.create_foreign_key('fk_tickets_template', 'tickets', 'ticket_templates',
                          ['template_id'], ['id'], ondelete='SET NULL')

    # Create indexes
    op.create_index('ix_tickets_sla_due_at', 'tickets', ['sla_due_at'])
    op.create_index('ix_tickets_sla_breached', 'tickets', ['sla_breached'])
    op.create_index('ix_tickets_escalation_level', 'tickets', ['escalation_level'])
    op.create_index('ix_tickets_merged_into_id', 'tickets', ['merged_into_id'])
    op.create_index('ix_tickets_is_merged', 'tickets', ['is_merged'])
    op.create_index('ix_tickets_department', 'tickets', ['department'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_tickets_department', table_name='tickets')
    op.drop_index('ix_tickets_is_merged', table_name='tickets')
    op.drop_index('ix_tickets_merged_into_id', table_name='tickets')
    op.drop_index('ix_tickets_escalation_level', table_name='tickets')
    op.drop_index('ix_tickets_sla_breached', table_name='tickets')
    op.drop_index('ix_tickets_sla_due_at', table_name='tickets')

    # Drop foreign keys
    op.drop_constraint('fk_tickets_template', 'tickets', type_='foreignkey')
    op.drop_constraint('fk_tickets_merged_into', 'tickets', type_='foreignkey')
    op.drop_constraint('fk_tickets_escalated_by', 'tickets', type_='foreignkey')

    # Drop columns
    op.drop_column('tickets', 'department')
    op.drop_column('tickets', 'contact_phone')
    op.drop_column('tickets', 'contact_email')
    op.drop_column('tickets', 'custom_fields')
    op.drop_column('tickets', 'tags')
    op.drop_column('tickets', 'template_id')
    op.drop_column('tickets', 'is_merged')
    op.drop_column('tickets', 'merged_into_id')
    op.drop_column('tickets', 'escalation_reason')
    op.drop_column('tickets', 'escalated_by')
    op.drop_column('tickets', 'escalated_at')
    op.drop_column('tickets', 'escalation_level')
    op.drop_column('tickets', 'sla_breached')
    op.drop_column('tickets', 'first_response_at')
    op.drop_column('tickets', 'sla_due_at')

    # Drop enum
    op.execute('DROP TYPE IF EXISTS escalationlevel')
