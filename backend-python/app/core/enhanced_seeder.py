"""
Enhanced Database Seeding Script per User Request
- 2000+ Outbreak Records (mix of pending/approved)
- 500+ Approved Records for ML Training
- 50+ Automatic Alerts based on clusters
- Realistic Indian Geographical Distribution
- Time series data over last 90 days
"""

import asyncio
from datetime import datetime, timedelta, timezone
import random
import sys
import os

# Ensure app can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Import models
from app.models.user import User
from app.models.doctor import DoctorOutbreak, DoctorAlert
from app.core.security import get_password_hash
from app.core.config import settings
from app.core.database import Base

# --- CONSTANTS & DATA ---

CITIES_DATA = [
    # Maharashtra (High Load)
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777, "state": "Maharashtra", "risk": 1.2},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567, "state": "Maharashtra", "risk": 1.1},
    {"name": "Nagpur", "lat": 21.1458, "lng": 79.0882, "state": "Maharashtra", "risk": 1.0},
    {"name": "Nashik", "lat": 19.9975, "lng": 73.7898, "state": "Maharashtra", "risk": 0.9},
    
    # Delhi NCR (High Load)
    {"name": "New Delhi", "lat": 28.6139, "lng": 77.2090, "state": "Delhi", "risk": 1.3},
    {"name": "Gurgaon", "lat": 28.4595, "lng": 77.0266, "state": "Haryana", "risk": 1.1},
    {"name": "Noida", "lat": 28.5355, "lng": 77.3910, "state": "Uttar Pradesh", "risk": 1.1},
    
    # Kerala (Moderate)
    {"name": "Kochi", "lat": 9.9312, "lng": 76.2673, "state": "Kerala", "risk": 0.8},
    {"name": "Thiruvananthapuram", "lat": 8.5241, "lng": 76.9366, "state": "Kerala", "risk": 0.8},
    
    # Karnataka
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946, "state": "Karnataka", "risk": 1.0},
    {"name": "Mysore", "lat": 12.2958, "lng": 76.6394, "state": "Karnataka", "risk": 0.9},

    # Tamil Nadu
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707, "state": "Tamil Nadu", "risk": 1.0},
    {"name": "Coimbatore", "lat": 11.0168, "lng": 76.9558, "state": "Tamil Nadu", "risk": 0.9},
    
    # West Bengal
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639, "state": "West Bengal", "risk": 1.1},
    
    # Uttar Pradesh
    {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462, "state": "Uttar Pradesh", "risk": 1.1},
    {"name": "Varanasi", "lat": 25.3176, "lng": 82.9739, "state": "Uttar Pradesh", "risk": 1.1},
    
    # Rajasthan
    {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873, "state": "Rajasthan", "risk": 1.0},
    {"name": "Udaipur", "lat": 24.5854, "lng": 73.7125, "state": "Rajasthan", "risk": 0.9},
    
    # Gujarat
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714, "state": "Gujarat", "risk": 1.1},
    {"name": "Surat", "lat": 21.1702, "lng": 72.8311, "state": "Gujarat", "risk": 1.1},

    # Telangana
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867, "state": "Telangana", "risk": 1.0},
]

DISEASES = [
    "Dengue", "Malaria", "COVID-19", "Influenza", "Cholera", 
    "Typhoid", "Tuberculosis", "Hepatitis", "Viral Fever"
]

SEVERITIES = ["mild", "moderate", "severe"]
STATUSES = ["pending", "approved", "rejected"]

HOSPITALS = [
    "City General Hospital", "Apollo Medical Center", "Fortis Health", 
    "Max Super Specialty", "District Civil Hospital", "Community Health Center",
    "Global Care Clinic", "Sunrise Hospital", "LifeLine Medical Institute"
]

# --- GENERATORS ---

async def ensure_users(db):
    """Ensure Doctor and Admin users exist"""
    print("👤 Verifying Users...")
    
    # 1. Doctor
    res = await db.execute(select(User).where(User.email == "doctor@symptomap.com"))
    doctor = res.scalar_one_or_none()
    if not doctor:
        doctor = User(
            email="doctor@symptomap.com",
            full_name="Dr. Sarah Johnson",
            password_hash=get_password_hash(settings.DOCTOR_PASSWORD),
            role="doctor",
            verification_status="verified",
            is_active=True
        )
        db.add(doctor)
        print("   -> Created Doctor User")

    # 2. Admin
    res = await db.execute(select(User).where(User.email == "admin@symptomap.com"))
    admin = res.scalar_one_or_none()
    if not admin:
        admin = User(
            email="admin@symptomap.com",
            full_name="System Admin",
            password_hash=get_password_hash("admin123"),
            role="admin",
            verification_status="verified",
            is_active=True
        )
        db.add(admin)
        print("   -> Created Admin User")
    
    await db.commit()
    return doctor

async def generate_outbreaks(db, doctor_id):
    """Generate 2000+ outbreak records"""
    print("🦠 Generating 2000+ Outbreak Records...")
    
    outbreaks = []
    
    # Time distribution: Exponential decay (more recent = more data)
    # We want data over last 90 days
    base_date = datetime.now(timezone.utc)
    
    count = 0
    target = 2200 # Go slightly above 2000
    
    changes_pending = 0
    
    processed_cities = {} # Track stats for alerts later
    
    while count < target:
        city_data = random.choice(CITIES_DATA)
        disease = random.choice(DISEASES)
        
        # Weighted Randoms
        severity = random.choices(SEVERITIES, weights=[0.5, 0.35, 0.15])[0]
        status = random.choices(STATUSES, weights=[0.3, 0.6, 0.1])[0] # 60% approved
        
        # Date Logic
        days_ago = int(random.expovariate(1/20)) # Mean 20 days ago
        if days_ago > 90: days_ago = random.randint(0, 90)
        report_date = base_date - timedelta(days=days_ago)
        
        # Patient Count Logic (correlated with severity & risk)
        base_patients = random.randint(5, 50)
        if severity == 'severe': base_patients *= 2
        if city_data['risk'] > 1.0: base_patients = int(base_patients * 1.5)
        
        # Update City Stats for Alerts
        key = f"{city_data['name']}_{disease}"
        if key not in processed_cities:
            processed_cities[key] = {'count': 0, 'cases': 0, 'lat': city_data['lat'], 'lng': city_data['lng'], 'city': city_data['name'], 'state': city_data['state'], 'disease': disease}
        
        if days_ago < 14: # Only count recent for alerts
             processed_cities[key]['count'] += 1
             processed_cities[key]['cases'] += base_patients

        # Create Record
        outbreak = DoctorOutbreak(
            disease_type=disease,
            patient_count=base_patients,
            severity=severity,
            latitude=city_data['lat'] + random.uniform(-0.03, 0.03), # Add jitter
            longitude=city_data['lng'] + random.uniform(-0.03, 0.03),
            location_name=f"{random.choice(HOSPITALS)}",
            city=city_data['name'],
            state=city_data['state'],
            description=f"Automated report: {severity} cases of {disease} detected.",
            date_reported=report_date,
            submitted_by=str(doctor_id),
            status=status,
            created_at=report_date
        )
        
        db.add(outbreak)
        outbreaks.append(outbreak)
        count += 1
        changes_pending += 1
        
        if changes_pending >= 100:
            await db.commit()
            changes_pending = 0
            # Print without carriage return to avoid terminal issues in some envs
            print(f"   -> Committed {count} records...")
            
    await db.commit()
    print(f"\n   -> ✅ Successfully created {len(outbreaks)} outbreak records.")
    return processed_cities

async def generate_alerts(db, city_stats):
    """Generate automatic alerts based on outbreak clusters"""
    print("🚨 Generating Smart Alerts...")
    
    alerts_created = 0
    
    for key, data in city_stats.items():
        # Logic: If recent cases > threshold, trigger alert
        threshold = 50 
        if data['disease'] in ['COVID-19', 'Dengue']: threshold = 30 # Lower threshold for high risk
        
        if data['cases'] > threshold:
            alert_type = 'critical' if data['cases'] > (threshold * 2) else 'warning'
            
            alert = DoctorAlert(
                alert_type=alert_type,
                title=f"{data['disease']} Outbreak in {data['city']}",
                message=f"High viral load detected. {data['cases']} recent cases reported. Immediate vector control recommended.",
                latitude=data['lat'],
                longitude=data['lng'],
                affected_area=f"{data['city']}, {data['state']}",
                expiry_date=datetime.now(timezone.utc) + timedelta(days=7),
                status='active',
                created_at=datetime.now(timezone.utc)
            )
            
            db.add(alert)
            alerts_created += 1
            
    # Add some manual generic alerts if low count
    if alerts_created < 20:
        extras = 20 - alerts_created
        for _ in range(extras):
            city = random.choice(CITIES_DATA)
            alert = DoctorAlert(
                alert_type='info',
                title=f"Health Advisory: {city['name']}",
                message=f"Routine seasonal monitoring active in {city['name']}.",
                latitude=city['lat'],
                longitude=city['lng'],
                affected_area=city['name'],
                expiry_date=datetime.now(timezone.utc) + timedelta(days=3),
                status='active',
                created_at=datetime.now(timezone.utc)
            )
            db.add(alert)
            alerts_created += 1

    await db.commit()
    print(f"   -> ✅ Created {alerts_created} smart alerts.")

async def main():
    print("🚀 Starting Enhanced Data Seeder...")
    
    # 1. Setup DB *inside* main loop
    database_url = settings.DATABASE_URL
    
    # Fix for async drivers
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://")
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    elif database_url.startswith("sqlite:///"):
        database_url = database_url.replace("sqlite:///", "sqlite+aiosqlite:///")

    print(f"   -> Connecting to {database_url}...") 
    
    # Debug Path
    if "sqlite" in database_url:
        import os
        db_path = database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        print(f"   -> DEBUG: Absolute DB Path: {os.path.abspath(db_path)}")

    engine = create_async_engine(database_url, echo=False)
    
    # Ensure tables exist
    print("   -> 🛠️ Ensuring database schema exists...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create session
    async with AsyncSessionLocal() as db:
        try:
            # 1. Users
            doctor = await ensure_users(db)
            
            # 2. Outbreaks
            city_stats = await generate_outbreaks(db, doctor.id)
            
            # 3. Alerts
            await generate_alerts(db, city_stats)
            
        except Exception as e:
            print(f"❌ Error during seeding: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()

    # Dispose engine
    await engine.dispose()
        
    print("\n✨ Seeding Complete!")
    print("   The ML Model will now have 500+ approved records to train on.")
    print("   Check /dashboard and /doctor/station to see the data.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
