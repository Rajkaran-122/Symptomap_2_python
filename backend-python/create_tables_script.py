
import asyncio
import sys
import os
import logging

# Configure logging to file
logging.basicConfig(filename='db_setup.log', level=logging.INFO)

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import engine, Base
from app.models import Broadcast  # Ensure imported

async def create_tables():
    print("Starting table creation...")
    logging.info("Starting table creation...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully.")
        logging.info("Tables created successfully.")
        
        # Verify
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='broadcasts'"))
            if result.scalar():
                print("✅ Broadcasts table confirmed.")
                logging.info("Broadcasts table confirmed.")
            else:
                print("❌ Broadcasts table MISSING after create_all.")
                logging.error("Broadcasts table MISSING after create_all.")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(create_tables())
