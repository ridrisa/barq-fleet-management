#!/usr/bin/env python3
"""
Create initial admin user for BARQ Fleet Management System
"""
import asyncio
from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine
from app.models.user import User
from app.models.base import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    """Create initial admin user"""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    db: Session = SessionLocal()

    try:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.email == "admin@barq.com").first()

        if existing_admin:
            print("✅ Admin user already exists!")
            print(f"Email: admin@barq.com")
            return

        # Create admin user
        hashed_password = pwd_context.hash("admin123")

        admin_user = User(
            email="admin@barq.com",
            hashed_password=hashed_password,
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            role="admin"
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✅ Admin user created successfully!")
        print(f"Email: admin@barq.com")
        print(f"Password: admin123")
        print(f"Role: {admin_user.role.value}")

    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_admin_user())
