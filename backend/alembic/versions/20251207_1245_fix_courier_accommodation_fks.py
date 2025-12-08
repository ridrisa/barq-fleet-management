"""Add foreign key constraints for courier accommodation columns

Revision ID: fix_courier_accom_fks
Revises: fix_fk_ondelete
Create Date: 2025-12-07

This migration adds FK constraints for the courier accommodation columns
that were previously missing constraints.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_courier_accom_fks'
down_revision = 'fix_fk_ondelete'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add FK constraints for courier accommodation columns"""

    print("Adding FK constraint for accommodation_building_id...")
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_name = 'couriers_accommodation_building_id_fkey'
            ) THEN
                ALTER TABLE couriers
                ADD CONSTRAINT couriers_accommodation_building_id_fkey
                FOREIGN KEY (accommodation_building_id) REFERENCES buildings(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)

    print("Adding FK constraint for accommodation_room_id...")
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints
                WHERE constraint_name = 'couriers_accommodation_room_id_fkey'
            ) THEN
                ALTER TABLE couriers
                ADD CONSTRAINT couriers_accommodation_room_id_fkey
                FOREIGN KEY (accommodation_room_id) REFERENCES rooms(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """)

    print("Courier accommodation FK constraints added successfully!")


def downgrade() -> None:
    """Remove FK constraints for courier accommodation columns"""
    op.execute("ALTER TABLE couriers DROP CONSTRAINT IF EXISTS couriers_accommodation_building_id_fkey;")
    op.execute("ALTER TABLE couriers DROP CONSTRAINT IF EXISTS couriers_accommodation_room_id_fkey;")
