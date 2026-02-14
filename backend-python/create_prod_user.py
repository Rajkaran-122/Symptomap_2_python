import asyncio
import sys
from getpass import getpass

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_user():
    print("\n👤 Create Production User")
    print("-------------------------")
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email required")
        return

    # Check existence
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"❌ User {email} already exists!")
            return

    password = getpass("Password (min 12 chars): ").strip()
    if len(password) < 12:
        print("⚠️ Password too short (min 12). Proceeding anyway for admin override...")

    full_name = input("Full Name: ").strip()
    role = input("Role (patient/doctor/admin) [admin]: ").strip() or "admin"

    async with AsyncSessionLocal() as db:
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            role=role,
            is_active=True,
            verification_status="verified",
            is_verified=True
        )
        db.add(user)
        await db.commit()
        print(f"\n✅ Successfully created user: {email}")
        print(f"   Role: {role}")
        print("   You can now login on the production site.")

if __name__ == "__main__":
    asyncio.run(create_user())
