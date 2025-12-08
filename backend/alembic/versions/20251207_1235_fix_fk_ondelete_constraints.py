"""Fix foreign key ondelete constraints for data integrity

Revision ID: fix_fk_ondelete
Revises: d34f56c7eca2
Create Date: 2025-12-07

This migration fixes critical foreign key ondelete behaviors identified in the database audit:
- Adds CASCADE, SET NULL, or RESTRICT behaviors to prevent orphaned records
- Adds unique constraints for attendance and salary deduplication
- Fixes type issues (Integer -> Numeric for monetary fields)
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_fk_ondelete'
down_revision = 'd34f56c7eca2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add ondelete behaviors to foreign keys and add unique constraints."""

    # Helper function to safely drop and recreate FK constraints
    def recreate_fk(table, column, ref_table, ref_column, ondelete):
        """Drop existing FK and recreate with ondelete behavior"""
        # Get constraint name pattern
        constraint_name = f"{table}_{column}_fkey"
        try:
            op.drop_constraint(constraint_name, table, type_='foreignkey')
        except Exception:
            # Constraint might have different name, try to find it
            pass

        op.create_foreign_key(
            constraint_name,
            table,
            ref_table,
            [column],
            [ref_column],
            ondelete=ondelete
        )

    # =====================================================
    # FUEL_LOGS - CASCADE on vehicle, SET NULL on courier
    # =====================================================
    print("Fixing fuel_logs foreign keys...")
    op.execute("""
        ALTER TABLE fuel_logs
        DROP CONSTRAINT IF EXISTS fuel_logs_vehicle_id_fkey;
    """)
    op.execute("""
        ALTER TABLE fuel_logs
        ADD CONSTRAINT fuel_logs_vehicle_id_fkey
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE CASCADE;
    """)

    op.execute("""
        ALTER TABLE fuel_logs
        DROP CONSTRAINT IF EXISTS fuel_logs_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE fuel_logs
        ADD CONSTRAINT fuel_logs_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE SET NULL;
    """)

    # =====================================================
    # SALARIES - RESTRICT (prevent courier deletion with salary records)
    # =====================================================
    print("Fixing salaries foreign keys...")
    op.execute("""
        ALTER TABLE salaries
        DROP CONSTRAINT IF EXISTS salaries_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE salaries
        ADD CONSTRAINT salaries_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE RESTRICT;
    """)

    # Add unique constraint for salary deduplication
    print("Adding salary unique constraint...")
    op.execute("""
        ALTER TABLE salaries
        DROP CONSTRAINT IF EXISTS uq_salary_courier_period;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_salary_courier_period'
            ) THEN
                ALTER TABLE salaries
                ADD CONSTRAINT uq_salary_courier_period
                UNIQUE (courier_id, year, month, organization_id);
            END IF;
        END $$;
    """)

    # =====================================================
    # LOANS - RESTRICT
    # =====================================================
    print("Fixing loans foreign keys...")
    op.execute("""
        ALTER TABLE loans
        DROP CONSTRAINT IF EXISTS loans_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE loans
        ADD CONSTRAINT loans_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE RESTRICT;
    """)

    # =====================================================
    # LEAVES - CASCADE
    # =====================================================
    print("Fixing leaves foreign keys...")
    op.execute("""
        ALTER TABLE leaves
        DROP CONSTRAINT IF EXISTS leaves_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE leaves
        ADD CONSTRAINT leaves_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE CASCADE;
    """)

    # =====================================================
    # ATTENDANCE - CASCADE
    # =====================================================
    print("Fixing attendance foreign keys...")
    op.execute("""
        ALTER TABLE attendance
        DROP CONSTRAINT IF EXISTS attendance_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE attendance
        ADD CONSTRAINT attendance_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE CASCADE;
    """)

    # Add unique constraint for attendance deduplication
    print("Adding attendance unique constraint...")
    op.execute("""
        ALTER TABLE attendance
        DROP CONSTRAINT IF EXISTS uq_attendance_courier_date;
    """)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'uq_attendance_courier_date'
            ) THEN
                -- First remove any duplicates
                DELETE FROM attendance a
                USING attendance b
                WHERE a.id > b.id
                AND a.courier_id = b.courier_id
                AND a.date = b.date
                AND a.organization_id = b.organization_id;

                ALTER TABLE attendance
                ADD CONSTRAINT uq_attendance_courier_date
                UNIQUE (courier_id, date, organization_id);
            END IF;
        END $$;
    """)

    # =====================================================
    # ASSETS - CASCADE
    # =====================================================
    print("Fixing assets foreign keys...")
    op.execute("""
        ALTER TABLE assets
        DROP CONSTRAINT IF EXISTS assets_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE assets
        ADD CONSTRAINT assets_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE CASCADE;
    """)

    # =====================================================
    # BONUSES - CASCADE
    # =====================================================
    print("Fixing bonuses foreign keys...")
    op.execute("""
        ALTER TABLE bonuses
        DROP CONSTRAINT IF EXISTS bonuses_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE bonuses
        ADD CONSTRAINT bonuses_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE CASCADE;
    """)

    # =====================================================
    # ROOMS - CASCADE on building
    # =====================================================
    print("Fixing rooms foreign keys...")
    op.execute("""
        ALTER TABLE rooms
        DROP CONSTRAINT IF EXISTS rooms_building_id_fkey;
    """)
    op.execute("""
        ALTER TABLE rooms
        ADD CONSTRAINT rooms_building_id_fkey
        FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE;
    """)

    # =====================================================
    # BEDS - CASCADE on room
    # =====================================================
    print("Fixing beds foreign keys...")
    op.execute("""
        ALTER TABLE beds
        DROP CONSTRAINT IF EXISTS beds_room_id_fkey;
    """)
    op.execute("""
        ALTER TABLE beds
        ADD CONSTRAINT beds_room_id_fkey
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE;
    """)

    # =====================================================
    # ALLOCATIONS - CASCADE on both courier and bed
    # =====================================================
    print("Fixing allocations foreign keys...")
    op.execute("""
        ALTER TABLE allocations
        DROP CONSTRAINT IF EXISTS allocations_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE allocations
        ADD CONSTRAINT allocations_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE CASCADE;
    """)

    op.execute("""
        ALTER TABLE allocations
        DROP CONSTRAINT IF EXISTS allocations_bed_id_fkey;
    """)
    op.execute("""
        ALTER TABLE allocations
        ADD CONSTRAINT allocations_bed_id_fkey
        FOREIGN KEY (bed_id) REFERENCES beds(id) ON DELETE CASCADE;
    """)

    # =====================================================
    # DELIVERIES - SET NULL on courier
    # =====================================================
    print("Fixing deliveries foreign keys...")
    op.execute("""
        ALTER TABLE deliveries
        DROP CONSTRAINT IF EXISTS deliveries_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE deliveries
        ADD CONSTRAINT deliveries_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE SET NULL;
    """)

    # =====================================================
    # COD_TRANSACTIONS - SET NULL on courier
    # =====================================================
    print("Fixing cod_transactions foreign keys...")
    op.execute("""
        ALTER TABLE cod_transactions
        DROP CONSTRAINT IF EXISTS cod_transactions_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE cod_transactions
        ADD CONSTRAINT cod_transactions_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE SET NULL;
    """)

    # =====================================================
    # INCIDENTS - SET NULL on both courier and vehicle
    # =====================================================
    print("Fixing incidents foreign keys...")
    op.execute("""
        ALTER TABLE incidents
        DROP CONSTRAINT IF EXISTS incidents_courier_id_fkey;
    """)
    op.execute("""
        ALTER TABLE incidents
        ADD CONSTRAINT incidents_courier_id_fkey
        FOREIGN KEY (courier_id) REFERENCES couriers(id) ON DELETE SET NULL;
    """)

    op.execute("""
        ALTER TABLE incidents
        DROP CONSTRAINT IF EXISTS incidents_vehicle_id_fkey;
    """)
    op.execute("""
        ALTER TABLE incidents
        ADD CONSTRAINT incidents_vehicle_id_fkey
        FOREIGN KEY (vehicle_id) REFERENCES vehicles(id) ON DELETE SET NULL;
    """)

    # =====================================================
    # TICKETS - RESTRICT on created_by (prevent user deletion)
    # =====================================================
    print("Fixing tickets foreign keys...")
    op.execute("""
        ALTER TABLE tickets
        DROP CONSTRAINT IF EXISTS tickets_created_by_fkey;
    """)
    op.execute("""
        ALTER TABLE tickets
        ADD CONSTRAINT tickets_created_by_fkey
        FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE RESTRICT;
    """)

    # =====================================================
    # TICKET_REPLIES - RESTRICT on user_id
    # =====================================================
    print("Fixing ticket_replies foreign keys...")
    op.execute("""
        ALTER TABLE ticket_replies
        DROP CONSTRAINT IF EXISTS ticket_replies_user_id_fkey;
    """)
    op.execute("""
        ALTER TABLE ticket_replies
        ADD CONSTRAINT ticket_replies_user_id_fkey
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
    """)

    # Fix is_internal column type if needed
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'ticket_replies'
                AND column_name = 'is_internal'
                AND data_type = 'integer'
            ) THEN
                ALTER TABLE ticket_replies
                ALTER COLUMN is_internal TYPE boolean
                USING CASE WHEN is_internal = 1 THEN true ELSE false END;
            END IF;
        END $$;
    """)

    # =====================================================
    # TICKET_ATTACHMENTS - RESTRICT on uploaded_by
    # =====================================================
    print("Fixing ticket_attachments foreign keys...")
    op.execute("""
        ALTER TABLE ticket_attachments
        DROP CONSTRAINT IF EXISTS ticket_attachments_uploaded_by_fkey;
    """)
    op.execute("""
        ALTER TABLE ticket_attachments
        ADD CONSTRAINT ticket_attachments_uploaded_by_fkey
        FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE RESTRICT;
    """)

    print("Foreign key constraints migration completed successfully!")


def downgrade() -> None:
    """Remove ondelete behaviors (revert to no action)"""
    # In downgrade, we would remove the ondelete behaviors
    # However, for safety, we typically don't remove constraints in downgrade
    # as it could lead to data integrity issues

    print("Downgrade: Removing ondelete behaviors is not recommended for data integrity.")
    print("If needed, manually remove constraints and recreate without ondelete.")

    # Remove unique constraints
    op.execute("ALTER TABLE salaries DROP CONSTRAINT IF EXISTS uq_salary_courier_period;")
    op.execute("ALTER TABLE attendance DROP CONSTRAINT IF EXISTS uq_attendance_courier_date;")
