"""
Database initialization endpoint
Adds test outbreak data for demonstration
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
from geoalchemy2 import WKTElement

from app.core.database import get_db
from app.models.outbreak import Hospital, Outbreak
from app.models.user import User
from app.core.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/initialize-demo-data")
async def initialize_demo_data(db: AsyncSession = Depends(get_db)):
    """Initialize database with demo outbreak data"""
    
    # Check if data already exists
    result = await db.execute(select(Outbreak))
    existing = result.scalars().all()
    
    if len(existing) > 0:
        return {
            "message": "Database already has data",
            "outbreak_count": len(existing)
        }
    
    # Create admin user
    result = await db.execute(select(User).where(User.email == "demo@symptomap.com"))
    admin = result.scalar_one_or_none()
    
    if not admin:
        admin = User(
            email="demo@symptomap.com",
            full_name="Demo Admin",
            hashed_password=get_password_hash("demo123"),
            role="admin",
            is_verified=True
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
    
    # Test outbreak data
    test_data = [
        {"name": "Lilavati Hospital Mumbai", "lat": 19.0760, "lng": 72.8777, "city": "Mumbai", "state": "Maharashtra", "disease": "Dengue", "patients": 145, "severity": "severe"},
        {"name": "KEM Hospital Mumbai", "lat": 19.0033, "lng": 72.8400, "city": "Mumbai", "state": "Maharashtra", "disease": "Malaria", "patients": 95, "severity": "severe"},
        {"name": "Ruby Hall Clinic Pune", "lat": 18.5204, "lng": 73.8567, "city": "Pune", "state": "Maharashtra", "disease": "Viral Fever", "patients": 52, "severity": "moderate"},
        {"name": "Jehangir Hospital Pune", "lat": 18.5275, "lng": 73.8570, "city": "Pune", "state": "Maharashtra", "disease": "Flu", "patients": 28, "severity": "mild"},
        {"name": "AIIMS Delhi", "lat": 28.5672, "lng": 77.2100, "city": "Delhi", "state": "Delhi", "disease": "Covid-19", "patients": 68, "severity": "moderate"},
    ]
    
    added_outbreaks = []
    
    for data in test_data:
        # Create hospital
        hospital = Hospital(
            name=data["name"],
            address=f"{data['name']}, {data['city']}",
            city=data["city"],
            state=data["state"],
            country="India",
            pincode="400001",
            phone="+91-9876543210",
            email=f"contact@{data['name'].replace(' ', '').lower()}.com",
            total_beds=500,
            icu_beds=50,
            available_beds=150,
            hospital_type="private",
            registration_number=f"REG{hash(data['name']) % 100000}",
            location=WKTElement(f"POINT({data['lng']} {data['lat']})", srid=4326)
        )
        db.add(hospital)
        await db.flush()
        
        # Create outbreak
        outbreak = Outbreak(
            hospital_id=hospital.id,
            reported_by=admin.id,
            disease_type=data["disease"],
            patient_count=data["patients"],
            date_started=datetime.now(timezone.utc) - timedelta(days=3),
            date_reported=datetime.now(timezone.utc),
            severity=data["severity"],
            verified=True,
            age_distribution={"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10},
            gender_distribution={"male": 52, "female": 48},
            symptoms=["Fever", "Fatigue", "Body Ache"],
            notes=f"{data['severity'].upper()} outbreak at {data['name']}",
            location=WKTElement(f"POINT({data['lng']} {data['lat']})", srid=4326)
        )
        db.add(outbreak)
        added_outbreaks.append({
            "hospital": data["name"],
            "disease": data["disease"],
            "patients": data["patients"],
            "severity": data["severity"]
        })
    
    await db.commit()
    
    return {
        "message": "Demo data initialized successfully",
        "outbreaks_added": len(added_outbreaks),
        "outbreaks": added_outbreaks
    }
