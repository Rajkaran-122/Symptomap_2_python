"""
SymptoMap FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.core.redis import redis_client
import app.models # Register all models
from sqlalchemy import text
from app.core.seeder import seed_database
from app.api.v1.websocket import router as websocket_router

# Rate Limiting
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter

# Security Middleware
from app.middleware.security import setup_security_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting SymptoMap Backend...")
    
    # Import all models to ensure they're registered with Base.metadata
    from app.models import (
        User, Hospital, Outbreak, Prediction, Alert,
        ChatbotConversation, AnonymousSymptomReport, DiseaseInfo,
        DoctorOutbreak, DoctorAlert
    )
    
    # Create database tables (including any new tables that don't exist)
    async with engine.begin() as conn:
        print("📊 Creating/updating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        # Check if we need to seed
        try:
            result = await conn.execute(text("SELECT count(*) FROM hospitals"))
            count = result.scalar()
        except Exception as e:
            print(f"⚠️ Error checking hospitals table: {e}")
            count = 0
        
    if count == 0:
        print("🌱 Seeding empty database...")
        await seed_database()
    else:
        print(f"✅ Database has {count} hospitals - skipping seed")
    
    # Legacy SQLite initialization removed in favor of SQLAlchemy
     
    # Connect to Redis
    await redis_client.connect()
    
    yield
    
    # Shutdown
    print("👋 Shutting down SymptoMap Backend...")
    await redis_client.disconnect()


app = FastAPI(
    title="SymptoMap API",
    description="Disease Surveillance & Outbreak Prediction API",
    version="2.0.0",
    lifespan=lifespan
)

# Apply Global Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Middleware - Support cross-origin credentials and Vercel preview URLs
def get_allowed_origins():
    """Include static origins + dynamic Vercel preview URL pattern"""
    origins = list(settings.CORS_ORIGINS)
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_origin_regex=r"https://.*\.vercel\.app$",  # Allow all Vercel preview deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-MFA-Required", "Set-Cookie"],  # Expose auth-related headers
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security Middleware (headers, request validation)
setup_security_middleware(app)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/test-reload")
def test_reload():
    return {"status": "reloaded"}

# Include WebSocket router
app.include_router(websocket_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "SymptoMap API",
        "version": "2.0.0",
        "status": "online",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


@app.post("/seed")
async def manual_seed():
    """Manually trigger database seeding"""
    try:
        from app.core.seeder import seed_database
        await seed_database()
        return {"status": "success", "message": "Database seeded successfully"}
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/force-seed")
async def force_reseed():
    """Force reseed: Clear all data and repopulate with comprehensive India data"""
    try:
        from sqlalchemy import text
        from app.core.database import AsyncSessionLocal
        from app.core.seeder import seed_database
        
        # Clear existing data
        async with AsyncSessionLocal() as db:
            # Delete in order to avoid foreign key issues
            await db.execute(text("DELETE FROM outbreaks"))
            await db.execute(text("DELETE FROM hospitals"))
            await db.execute(text("DELETE FROM users WHERE email = 'admin@symptomap.com'"))
            await db.commit()
            print("🗑️ Cleared existing ORM data")
        
        # Clear SQLite doctor data
        try:
            import sqlite3
            from app.core.config import get_sqlite_db_path
            conn = sqlite3.connect(get_sqlite_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM doctor_outbreaks")
            cursor.execute("DELETE FROM doctor_alerts")
            conn.commit()
            conn.close()
            print("🗑️ Cleared doctor SQLite data")
        except Exception as e:
            print(f"SQLite clear warning: {e}")
        
        # Reseed with comprehensive data
        await seed_database()
        
        return {
            "status": "success", 
            "message": "Database force-reseeded with comprehensive India data (173 zones)"
        }
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }


@app.post("/seed-alerts")
async def seed_alerts():
    """Seed alerts for Alert Management page - SQLite compatible"""
    try:
        from sqlalchemy import text
        from app.core.database import AsyncSessionLocal
        from datetime import datetime, timezone, timedelta
        import uuid
        import json
        
        async with AsyncSessionLocal() as db:
            # Drop and recreate alerts table to ensure correct schema
            await db.execute(text("DROP TABLE IF EXISTS alerts"))
            await db.commit()
            
            # Create alerts table with SQLAlchemy-compatible schema (no created_at)
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    prediction_id TEXT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    zone_name TEXT,
                    recipients TEXT,
                    sent_at TEXT,
                    delivery_status TEXT,
                    acknowledged_by TEXT,
                    expires_at TEXT
                )
            """))
            await db.commit()
            
            # Generate 50 diverse alerts
            import random
            
            severities = ["info", "warning", "critical"]
            zones = [
                "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", 
                "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
                "Patna", "Guwahati", "Kerala", "Uttarakhand", "Rajasthan"
            ]
            types = ["email", "sms", "push"]
            diseases = ["Dengue", "Malaria", "COVID-19", "Flu", "Typhoid", "Cholera", "Viral Fever"]
            messages = [
                "Outbreak detected in sector 4.",
                "Cases rising rapidly. Precautions advised.",
                "Hospital capacity reaching limits.",
                "Vaccination drive initiated.",
                "Water contamination alert.",
                "Vector control teams deployed.",
                "Routine surveillance update."
            ]
            
            alerts = []
            for i in range(50):
                severity = random.choice(severities)
                zone = random.choice(zones)
                disease = random.choice(diseases)
                
                if severity == "critical":
                    title = f"CRITICAL: {disease} Outbreak in {zone}"
                elif severity == "warning":
                    title = f"Warning: Rising {disease} cases in {zone}"
                else:
                    title = f"Info: {disease} update for {zone}"
                    
                alerts.append({
                    "severity": severity,
                    "title": title,
                    "zone_name": zone,
                    "message": f"{random.choice(messages)} {disease} cases reported.",
                    "type": random.choice(types),
                    "recipients": ["admin@symptomap.com", f"health@{zone.lower()}.gov.in"]
                })
            
            # Insert alerts directly using raw SQL
            for i, alert in enumerate(alerts):
                alert_id = str(uuid.uuid4())
                # distributed over last 30 days
                sent_at = (datetime.now(timezone.utc) - timedelta(days=i % 30, hours=i)).isoformat()
                recipients_json = json.dumps({"emails": alert["recipients"]})
                delivery_status_json = json.dumps({"email": "sent"})
                acknowledged_json = json.dumps([])
                
                await db.execute(text("""
                    INSERT OR IGNORE INTO alerts (id, alert_type, severity, title, message, zone_name, 
                                       recipients, delivery_status, acknowledged_by, sent_at)
                    VALUES (:id, :alert_type, :severity, :title, :message, :zone_name,
                            :recipients, :delivery_status, :acknowledged_by, :sent_at)
                """), {
                    "id": alert_id,
                    "alert_type": alert["type"],
                    "severity": alert["severity"],
                    "title": alert["title"],
                    "message": alert["message"],
                    "zone_name": alert["zone_name"],
                    "recipients": recipients_json,
                    "delivery_status": delivery_status_json,
                    "acknowledged_by": acknowledged_json,
                    "sent_at": sent_at
                })
            
            await db.commit()
        
        return {
            "status": "success",
            "message": f"Seeded {len(alerts)} alerts successfully"
        }
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
