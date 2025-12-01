"""Seed initial data into the database"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.crud.user import crud_user
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


def seed_users(db: Session) -> None:
    """Create initial users"""
    print("Seeding users...")

    # Check if admin user exists
    admin = crud_user.get_by_email(db, email="admin@barq.com")
    if not admin:
        admin_in = UserCreate(
            email="admin@barq.com",
            password="admin123",
            full_name="Admin User",
            role="admin"
        )
        admin = crud_user.create(db, obj_in=admin_in)
        print(f"✓ Created admin user: {admin.email}")
    else:
        print(f"✓ Admin user already exists: {admin.email}")

    # Check if regular user exists
    user = crud_user.get_by_email(db, email="user@barq.com")
    if not user:
        user_in = UserCreate(
            email="user@barq.com",
            password="user123",
            full_name="Regular User",
            role="user"
        )
        user = crud_user.create(db, obj_in=user_in)
        print(f"✓ Created regular user: {user.email}")
    else:
        print(f"✓ Regular user already exists: {user.email}")


def main() -> None:
    """Main seeding function"""
    print("Starting database seeding...")

    db = SessionLocal()
    try:
        seed_users(db)
        db.commit()
        print("\n✅ Database seeding completed successfully!")
        print("\nDefault credentials:")
        print("  Admin: admin@barq.com / admin123")
        print("  User:  user@barq.com / user123")
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
