"""
Add test data using the actual async database connection
Works with the configured database (PostgreSQL or SQLite)
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

# Add app directory to path
sys.path.insert(0, '/app')

from app.core.database import AsyncSessionLocal
from app.models.outbreak import Hospital, Outbreak
from app.models.user import User
from geoalchemy2 import WKTElement

async def add_test_data():
    """Add 5 test outbreaks"""
    print("\n🔧 Adding Test Data to Database...\n")
    
    async with AsyncSessionLocal() as db:
        # Create admin user if doesn't exist
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.email == "admin@test.com"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email="admin@test.com",
                full_name="Admin User",
                hashed_password="$2b$12$test",  # Dummy hash
                role="admin",
                is_verified=True
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
        
        print(f"✅ Using admin user: {admin.email}\n")
        
        # Test data
        test_outbreaks = [
            {"name": "Lilavati Hospital Mumbai", "lat": 19.0760, "lng": 72.8777, "disease": "Dengue", "patients": 145, "severity": "severe"},
            {"name": "KEM Hospital Mumbai", "lat": 19.0033, "lng": 72.8400, "disease": "Malaria", "patients": 95, "severity": "severe"},
            {"name": "Ruby Hall Pune", "lat": 18.5204, "lng": 73.8567, "disease": "Viral Fever", "patients": 52, "severity": "moderate"},
            {"name": "Jehangir Hospital Pune", "lat": 18.5275, "lng": 73.8570, "disease": "Flu", "patients": 28, "severity": "mild"},
            {"name": "AIIMS Delhi", "lat": 28.5672, "lng": 77.2100, "disease": "Covid-19", "patients": 68, "severity": "moderate"},
        ]
        
        severity_icons = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}
        added = 0
        
        for data in test_outbreaks:
            # Create hospital
            hospital = Hospital(
                name=data["name"],
                address=f"Address of {data['name']}",
                city=data["name"].split()[-1],
                state="Maharashtra" if "Mumbai" in data["name"] or "Pune" in data["name"] else "Delhi",
                country="India",
                pincode="400001",
                phone="+91-1234567890",
                email=f"contact@{data['name'].replace(' ', '').lower()}.in",
                total_beds=500,
                icu_beds=50,
                available_beds=150,
                hospital_type="private",
                registration_number=f"REG{hash(data['name']) % 100000}",
                location=WKTElement(f"POINT({data['lng']} {data['lat']})", srid=4326)
            )
            db.add(hospital)
            await db.flush()  # Get hospital ID
            
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
                age_distribution={"0-18": 25, "19-40": 40,  "41-60": 25, "60+": 10},
                gender_distribution={"male": 52, "female": 48},
                symptoms=["Fever", "Fatigue", "Body Ache"],
                notes=f"{data['severity'].upper()} outbreak at {data['name']}",
                location=WKTElement(f"POINT({data['lng']} {data['lat']})", srid=4326)
            )
            db.add(outbreak)
            
            icon = severity_icons[data["severity"]]
            print(f"{icon} {data['severity'].upper():8} | {data['name']:30} | {data['disease']:12} | {data['patients']:3} patients")
            added += 1
        
        await db.commit()
        print(f"\n✅ Successfully added {added} outbreaks!")
        print("\n" + "="*80)
        print("🎉 Database populated!")
        print("="*80)
        print("\n📍 Refresh http://localhost:5173/ to see the data!")
        print("\n")

if __name__ == "__main__":
    asyncio.run(add_test_data())
