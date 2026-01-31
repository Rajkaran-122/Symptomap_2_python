import asyncio
import sys
from app.core.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select

def log(msg):
    with open("debug_log.txt", "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

async def debug_user():
    log("Connecting to DB...")
    async with AsyncSessionLocal() as db:
        try:
            user_id = "a17d7b96-0e1a-4408-947f-8136d48a92cc"
            import uuid
            u_uuid = uuid.UUID(user_id)
            log(f"Querying User ID {user_id}...")
            result = await db.execute(select(User).where(User.id == u_uuid))
            user = result.scalar_one_or_none()
            if user:
                log(f"FOUND User: {user.email}, ID: {user.id} ({type(user.id)})")
            else:
                log("User not found.")
        except Exception as e:
            log(f"ERROR: {e}")
            import traceback
            log(traceback.format_exc())

if __name__ == "__main__":
    open("debug_log.txt", "w").close()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debug_user())
