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
    
    # Initialize SQLite tables for doctor station (Render ephemeral filesystem fix)
    try:
        from app.core.config import get_sqlite_db_path
        import sqlite3
        sqlite_path = get_sqlite_db_path()
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Create doctor_outbreaks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_outbreaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_type TEXT NOT NULL,
                patient_count INTEGER NOT NULL,
                severity TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                location_name TEXT,
                city TEXT,
                state TEXT,
                description TEXT,
                date_reported TEXT,
                submitted_by TEXT,
                created_at TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Create doctor_alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                affected_area TEXT,
                expiry_date TEXT,
                submitted_by TEXT,
                created_at TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ SQLite tables initialized at {sqlite_path}")
    except Exception as e:
        print(f"⚠️ SQLite init warning: {e}")
    
    # Connect to Redis
    await redis_client.connect()
    
    yield
    
    # Shutdown
    print("👋 Shutting down SymptoMap Backend...")
    await redis_client.disconnect()


app = FastAPI(
    title="SymptoMap API",
    description="AI-Powered Disease Surveillance & Patient Triage Platform",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

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
            
            # Create alerts table with SQLite-compatible schema
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
                    expires_at TEXT,
                    created_at TEXT
                )
            """))
            await db.commit()
            
            # Alert data - 20 diverse alerts across India
            alerts = [
                {"severity": "critical", "title": "Critical Dengue Outbreak Alert - Delhi", "zone_name": "Delhi", "message": "Severe dengue outbreak detected. All healthcare workers advised to take immediate precautions.", "type": "email", "recipients": ["admin@symptomap.com", "heath@delhi.gov.in", "doctor@example.com"]},
                {"severity": "critical", "title": "Emergency: Vector Control Teams Deployed", "zone_name": "Delhi - Severe Zone", "message": "Emergency vector control teams deployed. Residents advised to use mosquito repellents.", "type": "email", "recipients": ["delhi@health.gov.in"]},
                {"severity": "critical", "title": "Critical Dengue Outbreak - Immediate Action Required", "zone_name": "Delhi - Severe Zone", "message": "Hospital capacity reaching critical levels. Public advised to avoid outdoor activities during peak mosquito hours.", "type": "email", "recipients": []},
                {"severity": "warning", "title": "Moderate Viral Fever Cases - Pune", "zone_name": "Pune", "message": "Increasing viral fever cases reported. Citizens advised to maintain good hygiene.", "type": "email", "recipients": ["pune@health.gov.in", "docs@pune.com"]},
                {"severity": "critical", "title": "Critical Alert: AIIMS Delhi Capacity Critical", "zone_name": "Delhi - Severe Zone", "message": "AIIMS Delhi reaching 95% capacity. Patients advised to visit nearby hospitals for non-emergency cases.", "type": "email", "recipients": ["aiims@health.gov.in"]},
                {"severity": "warning", "title": "COVID-19 Monitoring Alert - Bangalore", "zone_name": "Bangalore", "message": "Slight increase in COVID-19 cases in Bangalore tech corridors. Mask advisory in effect.", "type": "email", "recipients": ["blr@health.gov.in", "admin@blr.gov.in"]},
                {"severity": "warning", "title": "Moderate Viral Fever Outbreak in Pune", "zone_name": "Pune - Moderate Zone", "message": "Moderate viral fever cases rising. Health department conducting awareness camps.", "type": "email", "recipients": []},
                {"severity": "info", "title": "Flu Season Advisory - Uttarakhand", "zone_name": "Uttarakhand", "message": "Seasonal flu increase expected. Residents advised to get flu vaccinations.", "type": "email", "recipients": ["uk@health.gov.in", "uttarakhand@nha.gov.in"]},
                {"severity": "warning", "title": "COVID-19 Cases Rising in Bangalore", "zone_name": "Bangalore - Moderate Zone", "message": "Continued rise in COVID-19 cases. Enhanced testing at key locations.", "type": "email", "recipients": []},
                {"severity": "info", "title": "Disease Surveillance Update - Multi-Zone", "zone_name": "All Zones", "message": "Weekly disease surveillance report available. Overall situation stable.", "type": "email", "recipients": ["national@nha.gov.in", "surveillance@health.gov.in"]},
                {"severity": "info", "title": "Seasonal Flu Outbreak - Uttarakhand", "zone_name": "Uttarakhand - Mild Zone", "message": "Mild seasonal flu outbreak in hill regions. Health centers stocked with medications.", "type": "email", "recipients": []},
                {"severity": "critical", "title": "Cholera Outbreak - Mumbai Slums", "zone_name": "Mumbai", "message": "Cholera outbreak confirmed in Dharavi area. Immediate water sanitation measures deployed.", "type": "email", "recipients": ["mumbai@health.gov.in", "bmc@gov.in"]},
                {"severity": "warning", "title": "Malaria Cases Surge - Kolkata", "zone_name": "Kolkata", "message": "Malaria cases increasing post-monsoon. Anti-malarial drugs distributed to primary health centers.", "type": "email", "recipients": ["kolkata@health.gov.in"]},
                {"severity": "critical", "title": "Typhoid Emergency - Chennai", "zone_name": "Chennai", "message": "Typhoid outbreak in north Chennai. Contaminated water source identified and sealed.", "type": "email", "recipients": ["chennai@health.gov.in", "tn@nha.gov.in"]},
                {"severity": "warning", "title": "Chikungunya Alert - Hyderabad", "zone_name": "Hyderabad", "message": "Rising chikungunya cases. Fumigation drives underway in affected areas.", "type": "email", "recipients": ["hyderabad@health.gov.in"]},
                {"severity": "info", "title": "Vaccination Drive - Rajasthan", "zone_name": "Rajasthan", "message": "State-wide polio vaccination drive scheduled for next week. All children under 5 to be vaccinated.", "type": "email", "recipients": ["rajasthan@health.gov.in"]},
                {"severity": "warning", "title": "Hepatitis A Alert - Gujarat", "zone_name": "Ahmedabad", "message": "Hepatitis A cases reported in old city areas. Boil water advisory issued.", "type": "email", "recipients": ["ahmedabad@health.gov.in", "gujarat@nha.gov.in"]},
                {"severity": "critical", "title": "Measles Outbreak - Bihar", "zone_name": "Patna", "message": "Measles outbreak in rural areas. Emergency vaccination camps set up.", "type": "email", "recipients": ["bihar@health.gov.in", "patna@nha.gov.in"]},
                {"severity": "info", "title": "Health Camp Announcement - Kerala", "zone_name": "Kerala", "message": "Free health checkup camps organized across all districts. Focus on diabetes and hypertension.", "type": "email", "recipients": ["kerala@health.gov.in"]},
                {"severity": "warning", "title": "Leptospirosis Warning - Assam", "zone_name": "Guwahati", "message": "Post-flood leptospirosis cases rising. Prophylactic antibiotics distributed to flood-affected areas.", "type": "email", "recipients": ["assam@health.gov.in", "guwahati@nha.gov.in"]},
            ]
            
            # Insert alerts directly using raw SQL
            for i, alert in enumerate(alerts):
                alert_id = str(uuid.uuid4())
                sent_at = (datetime.now(timezone.utc) - timedelta(days=i % 7, hours=i)).isoformat()
                recipients_json = json.dumps({"emails": alert["recipients"]})
                delivery_status_json = json.dumps({"email": "sent"})
                acknowledged_json = json.dumps([])
                
                await db.execute(text("""
                    INSERT OR IGNORE INTO alerts (id, alert_type, severity, title, message, zone_name, 
                                       recipients, delivery_status, acknowledged_by, sent_at, created_at)
                    VALUES (:id, :alert_type, :severity, :title, :message, :zone_name,
                            :recipients, :delivery_status, :acknowledged_by, :sent_at, :created_at)
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
                    "sent_at": sent_at,
                    "created_at": sent_at
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
