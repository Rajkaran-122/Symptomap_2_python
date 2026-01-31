import asyncio
import sys
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_doctor():
    email = "doctor@symptomap.com"
    password = "DoctorUser123!@#"
    
    async with AsyncSessionLocal() as db:
        # Check if exists
        result = await db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            print(f"User {email} already exists.")
            return

        user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name="Dr. Sarah Smith",
            role="doctor",
            verification_status="verified",
            is_active=True,
            mfa_enabled=False
        )
        db.add(user)
        await db.commit()
        print(f"✅ Created user: {email}")
        print(f"🔑 Password: {password}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(create_doctor())
