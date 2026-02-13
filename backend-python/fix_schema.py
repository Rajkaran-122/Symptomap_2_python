"""
Fix database schema by adding missing columns to users table.
Run this once to patch the existing SQLite database.
"""
import asyncio
import sys
from sqlalchemy import text
from app.core.database import engine

async def fix_schema():
    print("Attempting to fix schema...")
    async with engine.begin() as conn:
        try:
            # Check if column exists first (SQLite doesn't support IF NOT EXISTS for columns)
            # But simpler to just try-catch the ADD COLUMN
            print("Adding is_verified column...")
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
            print("✅ Column 'is_verified' added.")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "exists" in str(e).lower():
                print("ℹ️ Column 'is_verified' already exists.")
            else:
                print(f"⚠️ Error adding column: {e}")

        # ensure other tables exist
        from app.core.database import Base
        from app.models import OTPCode, AuthEvent
        print("Ensuring new tables exist...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables synced.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(fix_schema())
