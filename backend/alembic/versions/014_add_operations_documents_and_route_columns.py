"""Add operations documents table and route columns

Revision ID: 014
Revises: 013
Create Date: 2025-12-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '014'
down_revision: Union[str, None] = 'perf_indexes_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create document category enum
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE documentcategory AS ENUM (
                'Procedures', 'Policies', 'Training', 'Reports',
                'Templates', 'Guidelines', 'Other'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create operations_documents table
    op.create_table(
        'operations_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('doc_number', sa.String(50), unique=True, index=True),
        sa.Column('doc_name', sa.String(255), nullable=False),
        sa.Column('category', postgresql.ENUM('Procedures', 'Policies', 'Training', 'Reports',
                                               'Templates', 'Guidelines', 'Other',
                                               name='documentcategory', create_type=False),
                  server_default='Other', nullable=False),
        sa.Column('file_name', sa.String(255)),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('file_type', sa.String(50)),
        sa.Column('file_size', sa.Integer(), server_default='0'),
        sa.Column('version', sa.String(20), server_default='1.0'),
        sa.Column('description', sa.Text()),
        sa.Column('is_public', sa.String(10), server_default='false'),
        sa.Column('department', sa.String(100)),
        sa.Column('uploaded_by', sa.String(200)),
        sa.Column('uploader_email', sa.String(200)),
        sa.Column('uploaded_by_id', sa.Integer(), nullable=True),
        sa.Column('view_count', sa.Integer(), server_default='0'),
        sa.Column('download_count', sa.Integer(), server_default='0'),
        sa.Column('tags', sa.String(500)),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime()),
        sa.ForeignKeyConstraint(['uploaded_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_operations_documents_category', 'operations_documents', ['category'])
    op.create_index('ix_operations_documents_created_at', 'operations_documents', ['created_at'])

    # Create route status enum if not exists
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE routestatus AS ENUM (
                'planned', 'assigned', 'in_progress', 'completed', 'cancelled'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Add missing columns to routes table
    op.add_column('routes', sa.Column('route_number', sa.String(50)))
    op.add_column('routes', sa.Column('status', postgresql.ENUM('planned', 'assigned', 'in_progress',
                                                                  'completed', 'cancelled',
                                                                  name='routestatus', create_type=False),
                                       server_default='planned'))
    op.add_column('routes', sa.Column('zone_id', sa.Integer()))
    op.add_column('routes', sa.Column('scheduled_start_time', sa.DateTime()))
    op.add_column('routes', sa.Column('scheduled_end_time', sa.DateTime()))
    op.add_column('routes', sa.Column('actual_start_time', sa.DateTime()))
    op.add_column('routes', sa.Column('actual_end_time', sa.DateTime()))
    op.add_column('routes', sa.Column('start_location', sa.String(500)))
    op.add_column('routes', sa.Column('start_latitude', sa.Numeric(10, 8)))
    op.add_column('routes', sa.Column('start_longitude', sa.Numeric(11, 8)))
    op.add_column('routes', sa.Column('end_location', sa.String(500)))
    op.add_column('routes', sa.Column('end_latitude', sa.Numeric(10, 8)))
    op.add_column('routes', sa.Column('end_longitude', sa.Numeric(11, 8)))
    op.add_column('routes', sa.Column('total_stops', sa.Integer(), server_default='0'))
    op.add_column('routes', sa.Column('actual_distance_km', sa.Numeric(10, 2)))
    op.add_column('routes', sa.Column('actual_duration_minutes', sa.Integer()))
    op.add_column('routes', sa.Column('is_optimized', sa.Boolean(), server_default='false'))
    op.add_column('routes', sa.Column('optimization_algorithm', sa.String(50)))
    op.add_column('routes', sa.Column('optimization_score', sa.Numeric(5, 2)))
    op.add_column('routes', sa.Column('total_deliveries', sa.Integer(), server_default='0'))
    op.add_column('routes', sa.Column('completed_deliveries', sa.Integer(), server_default='0'))
    op.add_column('routes', sa.Column('failed_deliveries', sa.Integer(), server_default='0'))
    op.add_column('routes', sa.Column('avg_time_per_stop_minutes', sa.Numeric(10, 2)))
    op.add_column('routes', sa.Column('distance_variance_km', sa.Numeric(10, 2)))
    op.add_column('routes', sa.Column('time_variance_minutes', sa.Integer()))
    op.add_column('routes', sa.Column('special_instructions', sa.Text()))
    op.add_column('routes', sa.Column('internal_notes', sa.Text()))
    op.add_column('routes', sa.Column('created_by_id', sa.Integer()))
    op.add_column('routes', sa.Column('assigned_by_id', sa.Integer()))
    op.add_column('routes', sa.Column('assigned_at', sa.DateTime()))

    # Add foreign key constraints
    op.create_foreign_key('fk_routes_zone_id', 'routes', 'zones', ['zone_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_routes_created_by', 'routes', 'users', ['created_by_id'], ['id'], ondelete='SET NULL')
    op.create_foreign_key('fk_routes_assigned_by', 'routes', 'users', ['assigned_by_id'], ['id'], ondelete='SET NULL')

    # Create indexes and constraints
    op.create_index('ix_routes_route_number', 'routes', ['route_number'], unique=True)
    op.create_index('ix_routes_status', 'routes', ['status'])
    op.create_index('ix_routes_zone_id', 'routes', ['zone_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_routes_zone_id', table_name='routes')
    op.drop_index('ix_routes_status', table_name='routes')
    op.drop_index('ix_routes_route_number', table_name='routes')

    # Drop foreign keys
    op.drop_constraint('fk_routes_assigned_by', 'routes', type_='foreignkey')
    op.drop_constraint('fk_routes_created_by', 'routes', type_='foreignkey')
    op.drop_constraint('fk_routes_zone_id', 'routes', type_='foreignkey')

    # Drop routes columns
    op.drop_column('routes', 'assigned_at')
    op.drop_column('routes', 'assigned_by_id')
    op.drop_column('routes', 'created_by_id')
    op.drop_column('routes', 'internal_notes')
    op.drop_column('routes', 'special_instructions')
    op.drop_column('routes', 'time_variance_minutes')
    op.drop_column('routes', 'distance_variance_km')
    op.drop_column('routes', 'avg_time_per_stop_minutes')
    op.drop_column('routes', 'failed_deliveries')
    op.drop_column('routes', 'completed_deliveries')
    op.drop_column('routes', 'total_deliveries')
    op.drop_column('routes', 'optimization_score')
    op.drop_column('routes', 'optimization_algorithm')
    op.drop_column('routes', 'is_optimized')
    op.drop_column('routes', 'actual_duration_minutes')
    op.drop_column('routes', 'actual_distance_km')
    op.drop_column('routes', 'total_stops')
    op.drop_column('routes', 'end_longitude')
    op.drop_column('routes', 'end_latitude')
    op.drop_column('routes', 'end_location')
    op.drop_column('routes', 'start_longitude')
    op.drop_column('routes', 'start_latitude')
    op.drop_column('routes', 'start_location')
    op.drop_column('routes', 'actual_end_time')
    op.drop_column('routes', 'actual_start_time')
    op.drop_column('routes', 'scheduled_end_time')
    op.drop_column('routes', 'scheduled_start_time')
    op.drop_column('routes', 'zone_id')
    op.drop_column('routes', 'status')
    op.drop_column('routes', 'route_number')

    # Drop operations_documents table
    op.drop_index('ix_operations_documents_created_at', table_name='operations_documents')
    op.drop_index('ix_operations_documents_category', table_name='operations_documents')
    op.drop_table('operations_documents')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS documentcategory')
    op.execute('DROP TYPE IF EXISTS routestatus')
