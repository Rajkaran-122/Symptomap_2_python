from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import traceback
import sys
import os

# Ensure we can import from root
sys.path.append(os.getcwd())

try:
    from seed_production_data import seed_hospitals_and_outbreaks
except ImportError:
    # Fallback if import fails (should not happen in correct env)
    seed_hospitals_and_outbreaks = None

from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

router = APIRouter(prefix="/admin-ops", tags=["Admin Operations"])

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "admin"

@router.get("/seed-production")
async def trigger_production_seed():
    """
    Trigger the production seeding script via HTTP.
    Useful for environments where shell access is restricted (e.g. Render Free Tier).
    """
    if not seed_hospitals_and_outbreaks:
        raise HTTPException(status_code=500, detail="Seeding script not found")
        
    try:
        await seed_hospitals_and_outbreaks()
        return {"status": "success", "message": "Production database seeded successfully. You can now login as admin@symptomap.com"}
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@router.post("/create-user")
async def create_custom_user(user_data: UserCreate):
    """
    Create a specific user account via HTTP.
    """
    try:
        async with AsyncSessionLocal() as db:
            # Check if exists
            result = await db.execute(select(User).where(User.email == user_data.email))
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="User already exists")
            
            user = User(
                email=user_data.email,
                password_hash=get_password_hash(user_data.password),
                full_name=user_data.full_name,
                role=user_data.role,
                is_active=True,
                verification_status="verified",
                is_verified=True
            )
            db.add(user)
            await db.commit()
            
            return {"status": "success", "message": f"User {user_data.email} created successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e), 
            "traceback": traceback.format_exc()
        }
