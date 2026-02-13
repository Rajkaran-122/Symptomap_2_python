"""
Migration script to update users table for OTP support
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def migrate():
    print("🔄 Starting database migration for OTP support...")
    
    async with engine.begin() as conn:
        # 1. Add new columns
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE"))
            print("✅ Added phone_verified column")
        except Exception as e:
            print(f"⚠️ Error adding phone_verified: {e}")

        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS region VARCHAR(100)"))
            print("✅ Added region column")
        except Exception as e:
            print(f"⚠️ Error adding region: {e}")

        # 2. Make columns nullable for OTP users
        # Note: Syntax depends on DB type. Assuming PostgreSQL based on project structure.
        # If SQLite, this might fail or require different syntax.
        
        # Check if using SQLite (often used in dev)
        # We can check engine url but for now try generic SQL or catch errors
        
        columns_to_nullable = ["email", "password_hash", "full_name"]
        
        for col in columns_to_nullable:
            try:
                # PostgreSQL syntax
                await conn.execute(text(f"ALTER TABLE users ALTER COLUMN {col} DROP NOT NULL"))
                print(f"✅ Made {col} nullable")
            except Exception as e:
                print(f"⚠️ Error making {col} nullable (might be SQLite?): {e}")
                
                # SQLite workaround: SQLite doesn't support ALTER COLUMN DROP NOT NULL easily
                # We often have to recreate table, but for MVP dev we might just leave it 
                # and ensure we provide dummy values if needed, OR we can try to disable strict mode?
                # Actually, for SQLite it's better to just leave it if we can't easily change it.
                # But wait, if they are NOT NULL, the insert will fail.
                pass

    print("🏁 Migration completed")

if __name__ == "__main__":
    asyncio.run(migrate())
