"""Add Workflow tables

Revision ID: 007
Revises: 006
Create Date: 2025-11-06 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create WorkflowTemplate table
    op.create_table(
        'workflow_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('steps', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_templates_name', 'workflow_templates', ['name'])
    op.create_index('ix_workflow_templates_is_active', 'workflow_templates', ['is_active'])
    op.create_index('ix_workflow_templates_category', 'workflow_templates', ['category'])

    # Create WorkflowInstance table
    op.create_table(
        'workflow_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('initiated_by', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum(
            'DRAFT', 'IN_PROGRESS', 'PENDING_APPROVAL', 'APPROVED',
            'REJECTED', 'COMPLETED', 'CANCELLED',
            name='workflowstatus'
        ), server_default='DRAFT', nullable=False),
        sa.Column('current_step', sa.Integer(), server_default='0', nullable=False),
        sa.Column('data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('started_at', sa.Date(), nullable=True),
        sa.Column('completed_at', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['workflow_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['initiated_by'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_instances_template_id', 'workflow_instances', ['template_id'])
    op.create_index('ix_workflow_instances_initiated_by', 'workflow_instances', ['initiated_by'])
    op.create_index('ix_workflow_instances_status', 'workflow_instances', ['status'])
    op.create_index('ix_workflow_instances_created_at', 'workflow_instances', ['created_at'])


def downgrade() -> None:
    # Drop WorkflowInstance table
    op.drop_index('ix_workflow_instances_created_at', table_name='workflow_instances')
    op.drop_index('ix_workflow_instances_status', table_name='workflow_instances')
    op.drop_index('ix_workflow_instances_initiated_by', table_name='workflow_instances')
    op.drop_index('ix_workflow_instances_template_id', table_name='workflow_instances')
    op.drop_table('workflow_instances')
    op.execute('DROP TYPE IF EXISTS workflowstatus')

    # Drop WorkflowTemplate table
    op.drop_index('ix_workflow_templates_category', table_name='workflow_templates')
    op.drop_index('ix_workflow_templates_is_active', table_name='workflow_templates')
    op.drop_index('ix_workflow_templates_name', table_name='workflow_templates')
    op.drop_table('workflow_templates')
