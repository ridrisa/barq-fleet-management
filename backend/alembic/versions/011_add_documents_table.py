"""Add documents table

Revision ID: 011
Revises: 010
Create Date: 2025-11-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types if they don't exist
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE documententity AS ENUM ('COURIER', 'VEHICLE');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    op.execute("""
        DO $$ BEGIN
            CREATE TYPE documenttype AS ENUM (
                'DRIVER_LICENSE', 'VEHICLE_REGISTRATION', 'INSURANCE',
                'MULKIYA', 'IQAMA', 'PASSPORT', 'CONTRACT', 'OTHER'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create documents table
    op.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            entity_type documententity NOT NULL,
            entity_id INTEGER NOT NULL,
            document_type documenttype NOT NULL,
            document_number VARCHAR(100),
            document_name VARCHAR(200) NOT NULL,
            file_url VARCHAR(500) NOT NULL,
            file_type VARCHAR(50),
            file_size INTEGER,
            issue_date DATE,
            expiry_date DATE,
            issuing_authority VARCHAR(200),
            notes VARCHAR(500),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE
        );
    """)

    # Create indexes
    op.execute("CREATE INDEX IF NOT EXISTS ix_documents_id ON documents (id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_documents_entity_type ON documents (entity_type);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_documents_entity_id ON documents (entity_id);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_documents_document_type ON documents (document_type);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_documents_entity_type_entity_id ON documents (entity_type, entity_id);")


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_documents_entity_type_entity_id', table_name='documents')
    op.drop_index('ix_documents_document_type', table_name='documents')
    op.drop_index('ix_documents_entity_id', table_name='documents')
    op.drop_index('ix_documents_entity_type', table_name='documents')
    op.drop_index('ix_documents_id', table_name='documents')

    # Drop table
    op.drop_table('documents')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS documenttype')
    op.execute('DROP TYPE IF EXISTS documententity')
