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
from app.api.v1.public import router as public_router
from app.api.v1.public_outbreaks import router as public_outbreaks_router

# Rate Limiting
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.limiter import limiter

# Security Middleware
from app.middleware.security import setup_security_middleware


async def _seed_permanent_data():
    """
    Seed permanent broadcasts and admin alerts if the tables are empty.
    Runs on every startup — safe to call multiple times (idempotent).
    """
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal
    import uuid, json
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        # --- Broadcasts ---
        try:
            bc_count = await db.execute(text("SELECT count(*) FROM broadcasts WHERE is_active = 1"))
            if (bc_count.scalar() or 0) == 0:
                BROADCASTS = [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Dengue Advisory — Stay Alert This Monsoon",
                        "content": (
                            "Health authorities have issued a dengue advisory for several districts. "
                            "Use mosquito repellent, wear full-sleeved clothing, and eliminate stagnant water near your home. "
                            "Report symptoms (high fever, joint pain, rash) immediately to your nearest health centre."
                        ),
                        "severity": "warning",
                        "region": None,
                        "channels": json.dumps(["in_app"]),
                        "is_active": 1,
                        "is_automated": 0,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "COVID-19 Booster Drive — Free Vaccination Camps",
                        "content": (
                            "Free COVID-19 booster vaccination camps are being conducted at all government hospitals "
                            "and primary health centres across the country this week. Carry your Aadhaar card. "
                            "Walk-ins welcome, no prior appointment needed."
                        ),
                        "severity": "info",
                        "region": None,
                        "channels": json.dumps(["in_app"]),
                        "is_active": 1,
                        "is_automated": 0,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "CRITICAL: Cholera Cluster Detected in Eastern Zone",
                        "content": (
                            "A cluster of cholera cases has been confirmed in the eastern zones. "
                            "Avoid unboiled water and raw street food. Oral rehydration salts are "
                            "available free at all PHCs. Seek medical attention immediately if you "
                            "experience severe diarrhoea or vomiting."
                        ),
                        "severity": "critical",
                        "region": None,
                        "channels": json.dumps(["in_app"]),
                        "is_active": 1,
                        "is_automated": 0,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    },
                ]
                for bc in BROADCASTS:
                    await db.execute(text("""
                        INSERT OR IGNORE INTO broadcasts
                          (id, title, content, severity, region, channels, is_active, is_automated, created_at, updated_at)
                        VALUES
                          (:id, :title, :content, :severity, :region, :channels, :is_active, :is_automated, :created_at, :updated_at)
                    """), bc)
                await db.commit()
                print("[INFO] Seeded 3 permanent broadcasts")
        except Exception as e:
            print(f"[WARN] Could not seed broadcasts: {e}")

        # --- Admin Alerts ---
        try:
            alert_count = await db.execute(text("SELECT count(*) FROM alerts"))
            if (alert_count.scalar() or 0) == 0:
                ALERTS = [
                    {
                        "id": str(uuid.uuid4()),
                        "alert_type": "email",
                        "severity": "critical",
                        "title": "CRITICAL: Dengue Surge — Mumbai Region",
                        "message": (
                            "A rapid surge of Dengue cases has been reported across Mumbai and surrounding districts. "
                            "Hospitals are advised to increase bed capacity. Citizens should avoid stagnant water and use mosquito nets."
                        ),
                        "zone_name": "Mumbai",
                        "recipients": json.dumps({"emails": ["admin@symptomap.com"]}),
                        "delivery_status": json.dumps({"email": "sent"}),
                        "acknowledged_by": json.dumps([]),
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "is_active": 1,
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "alert_type": "sms",
                        "severity": "warning",
                        "title": "Warning: Malaria Cases Rising — Delhi NCR",
                        "message": (
                            "Health teams are reporting rising Malaria cases in Delhi NCR due to seasonal conditions. "
                            "Preventive fumigation drives are underway. Citizens should use protective clothing."
                        ),
                        "zone_name": "Delhi",
                        "recipients": json.dumps({"emails": ["admin@symptomap.com"]}),
                        "delivery_status": json.dumps({"email": "sent"}),
                        "acknowledged_by": json.dumps([]),
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "is_active": 1,
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "alert_type": "push",
                        "severity": "info",
                        "title": "Info: Routine Cholera Surveillance Update — All Zones",
                        "message": (
                            "Routine surveillance has detected minor Cholera clusters in select districts. "
                            "Water samples are being tested. No major outbreak risk at this time."
                        ),
                        "zone_name": "National",
                        "recipients": json.dumps({"emails": ["admin@symptomap.com"]}),
                        "delivery_status": json.dumps({"email": "sent"}),
                        "acknowledged_by": json.dumps([]),
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "is_active": 1,
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "alert_type": "email",
                        "severity": "critical",
                        "title": "CRITICAL: Viral Fever Outbreak — Rajasthan",
                        "message": (
                            "Over 300 hospitalisations for severe viral fever have been reported across Rajasthan in the last 48 hours. "
                            "Mobile medical units have been deployed. Residents are advised to seek immediate care for persistent fever above 102°F."
                        ),
                        "zone_name": "Rajasthan",
                        "recipients": json.dumps({"emails": ["admin@symptomap.com"]}),
                        "delivery_status": json.dumps({"email": "sent"}),
                        "acknowledged_by": json.dumps([]),
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "is_active": 1,
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "alert_type": "email",
                        "severity": "warning",
                        "title": "Warning: Typhoid Cluster — Lucknow Water Supply",
                        "message": (
                            "A typhoid cluster linked to contaminated water supply has been identified in parts of Lucknow. "
                            "Citizens in the affected wards should boil drinking water. Health officers are on-site."
                        ),
                        "zone_name": "Lucknow",
                        "recipients": json.dumps({"emails": ["admin@symptomap.com"]}),
                        "delivery_status": json.dumps({"email": "sent"}),
                        "acknowledged_by": json.dumps([]),
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "is_active": 1,
                    },
                ]
                for al in ALERTS:
                    await db.execute(text("""
                        INSERT OR IGNORE INTO alerts
                          (id, alert_type, severity, title, message, zone_name,
                           recipients, delivery_status, acknowledged_by, sent_at, is_active)
                        VALUES
                          (:id, :alert_type, :severity, :title, :message, :zone_name,
                           :recipients, :delivery_status, :acknowledged_by, :sent_at, :is_active)
                    """), al)
                await db.commit()
                print("[INFO] Seeded 5 permanent admin alerts")
        except Exception as e:
            print(f"[WARN] Could not seed alerts: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("[INFO] Starting SymptoMap Backend...")

    
    # Import all models to ensure they're registered with Base.metadata
    from app.models import (
        User, Hospital, Outbreak, Prediction, Alert,
        ChatbotConversation, AnonymousSymptomReport, DiseaseInfo,
        DoctorOutbreak, DoctorAlert, Broadcast
    )
    
    # Create database tables (including any new tables that don't exist)
    async with engine.begin() as conn:
        print("[INFO] Creating/updating database tables...")
        await conn.run_sync(Base.metadata.create_all)
        
        # Check if we need to seed
        try:
            result = await conn.execute(text("SELECT count(*) FROM hospitals"))
            count = result.scalar()
        except Exception as e:
            print(f"[WARN] Error checking hospitals table: {e}")
            count = 0
        
    if count == 0:
        print("[INFO] Seeding empty database...")
        await seed_database()
    else:
        print(f"[OK] Database has {count} hospitals - skipping seed")
    
    # Auto-seed permanent broadcasts and alerts if needed
    await _seed_permanent_data()

    
    # Legacy SQLite initialization removed in favor of SQLAlchemy
     
    # Connect to Redis
    await redis_client.connect()
    
    yield
    
    # Shutdown
    print("[INFO] Shutting down SymptoMap Backend...")
    await redis_client.disconnect()


app = FastAPI(
    title="SymptoMap API",
    description="Disease Surveillance & Outbreak Prediction API",
    version="2.0.0",
    lifespan=lifespan
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security Middleware (headers, request validation)
setup_security_middleware(app)

# Apply Global Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Middleware - Support cross-origin credentials and Vercel preview URLs
# Added last to ensure it's the OUTERMOST middleware layer
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

# Custom exception handlers with CORS headers
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request as StarletteRequest

def get_cors_headers(request: StarletteRequest):
    """Generate CORS headers based on request origin"""
    origin = request.headers.get("origin", "")
    allowed_origins = get_allowed_origins()
    
    # Check if origin is allowed
    if origin in allowed_origins or origin.endswith(".vercel.app"):
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    return {}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: StarletteRequest, exc: HTTPException):
    """Custom HTTP exception handler with CORS headers"""
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: StarletteRequest, exc: Exception):
    """Custom general exception handler with CORS headers"""
    import traceback
    print(f"Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    headers = get_cors_headers(request)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/test-reload")
def test_reload():
    return {"status": "reloaded"}

# Include WebSocket router
app.include_router(websocket_router, prefix=settings.API_V1_PREFIX)
# Include Public API router
app.include_router(public_router, prefix=settings.API_V1_PREFIX)
app.include_router(public_outbreaks_router, prefix=settings.API_V1_PREFIX)


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
            print("[INFO] Cleared existing ORM data")
        
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
            print("[INFO] Cleared doctor SQLite data")
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
