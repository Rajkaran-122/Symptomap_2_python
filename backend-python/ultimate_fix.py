"""
ULTIMATE FIX: Direct database insertion using SQLAlchemy async
This will add data directly to the database bypassing authentication
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta, timezone

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def add_data_directly():
    """Add outbreaks directly to database"""
    from app.core.database import AsyncSessionLocal
    from app.models.outbreak import Hospital, Outbreak
    from app.models.user import User
    from app.core.security import get_password_hash
    from geoalchemy2.elements import WKTElement
    from sqlalchemy import select
    
    print("\n" + "="*80)
    print("🔥 ULTIMATE DATABASE FIX - Direct Async Insertion")
    print("="*80)
    print("\nThis will add data directly to your database bypassing all API layers\n")
    
    async with AsyncSessionLocal() as db:
        # Create admin user
        result = await db.execute(select(User).where(User.email == "admin@symptomap.com"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Creating admin user...")
            admin = User(
                email="admin@symptomap.com",
                full_name="System Admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_verified=True
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
        
        print(f"✅ Admin user ready (ID: {admin.id})\n")
        
        # Check current outbreak count
        result = await db.execute(select(Outbreak))
        current_count = len(result.scalars().all())
        print(f"Current outbreaks in database: {current_count}\n")
        
        if current_count > 0:
            print("⚠️  Database already has outbreaks. Skipping data insertion.")
            print("If you want to add more, the data insertion logic is ready.\n")
            return current_count
        
        # Professional outbreak data
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
            # Create hospital
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
        
        print(f"\n✅ Successfully added {added} outbreaks to database!")
        print("\n" + "="*80)
        print("🎉 DATABASE POPULATED!")
        print("="*80)
        print("\n📊 NEXT STEPS:")
        print("1. Open Dashboard: http://localhost:5173/")
        print("2. Press Ctrl+Shift+R (hard refresh)")
        print("3. You should now see:")
        print("   ✅ Dashboard showing 5 outbreaks (not 0)")
        print("   ✅ Map with colored circles:")
        print("      - 🔴 2 RED circles (Mumbai - severe)")
        print("      - 🟡 2 YELLOW circles (Pune/Delhi - moderate)")
        print("      - 🟢 1 GREEN circle (Pune - mild)")
        print("   ✅ Analytics with real data")
        print("\n")
        
        return added

if __name__ == "__main__":
    try:
        result = asyncio.run(add_data_directly())
        print(f"✅ Process completed successfully. {result} outbreaks in database.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
