"""Seed initial data into the database"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import db_manager
from app.models.user import User
from app.core.security import get_password_hash


def seed_users(db: Session) -> None:
    """Create initial users"""
    print("Seeding users...")

    # Check if admin user exists
    admin = db.query(User).filter(User.email == "admin@barq.com").first()
    if not admin:
        admin = User(
            email="admin@barq.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            role="admin",
            is_active=True,
            is_superuser=True
        )
        db.add(admin)
        db.flush()
        print(f"✓ Created admin user: {admin.email}")
    else:
        print(f"✓ Admin user already exists: {admin.email}")

    # Check if regular user exists
    user = db.query(User).filter(User.email == "user@barq.com").first()
    if not user:
        user = User(
            email="user@barq.com",
            hashed_password=get_password_hash("user123"),
            full_name="Regular User",
            role="user",
            is_active=True,
            is_superuser=False
        )
        db.add(user)
        db.flush()
        print(f"✓ Created regular user: {user.email}")
    else:
        print(f"✓ Regular user already exists: {user.email}")


def main() -> None:
    """Main seeding function"""
    print("Starting database seeding...")

    db = db_manager.SessionLocal()
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
