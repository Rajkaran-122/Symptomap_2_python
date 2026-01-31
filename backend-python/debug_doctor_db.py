import asyncio
import sys
from app.core.database import AsyncSessionLocal
from app.models.doctor import DoctorOutbreak as DoctorOutbreakModel
from sqlalchemy import select

async def debug_db():
    print("Connecting to DB...")
    async with AsyncSessionLocal() as db:
        try:
            print("Querying DoctorOutbreakModel...")
            result = await db.execute(select(DoctorOutbreakModel))
            rows = result.scalars().all()
            print(f"✅ Found {len(rows)} rows.")
            for r in rows:
                print(f" - ID: {r.id}, Report Date: {r.date_reported} ({type(r.date_reported)})")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_db())
