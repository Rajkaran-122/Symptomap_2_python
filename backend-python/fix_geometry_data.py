"""
Clear and re-populate database using proper ORM methods
This will create proper geometry objects that SQLAlchemy can read
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def repopulate_database():
    from app.core.database import AsyncSessionLocal
    from app.models.outbreak import Hospital, Outbreak
    from app.models.user import User
    from geoalchemy2.elements import WKTElement
    from sqlalchemy import select, delete
    
    print("\n🔧 RE-POPULATING DATABASE WITH PROPER GEOMETRY\n")
    
    async with AsyncSessionLocal() as db:
        # Clear existing data
        print("Clearing existing data...")
        await db.execute(delete(Outbreak))
        await db.execute(delete(Hospital))
        await db.commit()
        print("✅ Cleared outbreaks and hospitals\n")
        
        # Use existing admin user
        result = await db.execute(select(User).limit(1))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("❌ No user found in database. Please create a user first.")
            return
        
        print(f"✅ Using user: {admin.email}\n")
        
        # Outbreak data
        outbreaks_data = [
            {"name": "Lilavati Hospital Mumbai", "lat": 19.0760, "lng": 72.8777, "city": "Mumbai", "state": "Maharashtra", "disease": "Dengue", "patients": 145, "severity": "severe"},
            {"name": "KEM Hospital Mumbai", "lat": 19.0033, "lng": 72.8400, "city": "Mumbai", "state": "Maharashtra", "disease": "Malaria", "patients": 95, "severity": "severe"},
            {"name": "Ruby Hall Clinic Pune", "lat": 18.5204, "lng": 73.8567, "city": "Pune", "state": "Maharashtra", "disease": "Viral Fever", "patients": 52, "severity": "moderate"},
            {"name": "Jehangir Hospital Pune", "lat": 18.5275, "lng": 73.8570, "city": "Pune", "state": "Maharashtra", "disease": "Flu", "patients": 28, "severity": "mild"},
            {"name": "AIIMS Delhi", "lat": 28.5672, "lng": 77.2100, "city": "Delhi", "state": "Delhi", "disease": "Covid-19", "patients": 68, "severity": "moderate"},
        ]
        
        severity_icons = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}
        added = 0
        
        for data in outbreaks_data:
            # Create hospital with proper WKTElement
            hospital = Hospital(
                name=data["name"],
                address=f"{data['name']}, {data['city']}, {data['state']}",
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
                severity=data["severity"],
                verified=True,
                age_distribution={"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10},
                gender_distribution={"male": 52, "female": 48},
                symptoms=["Fever", "Fatigue", "Body Ache"],
                notes=f"{data['severity'].upper()} outbreak at {data['name']}",
                location=WKTElement(f"POINT({data['lng']} {data['lat']})", srid=4326)
            )
            db.add(outbreak)
            
            icon = severity_icons[data["severity"]]
            print(f"{icon} {data['severity'].upper():8} | {data['name']:35} | {data['disease']:12} | {data['patients']:3} patients")
            added += 1
        
        await db.commit()
        
        print(f"\n✅ Successfully added {added} outbreaks with proper geometry!")
        print("\n" + "="*80)
        print("🎉 DATABASE RE-POPULATED!")
        print("="*80)
        print("\n📍 NEXT STEPS:")
        print("   1. Refresh http://localhost:5173/")
        print("   2. Dashboard should now show 5 outbreaks")
        print("   3. No more 500 errors - API can read geometry data!")
        print("\n")

if __name__ == "__main__":
    try:
        asyncio.run(repopulate_database())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
