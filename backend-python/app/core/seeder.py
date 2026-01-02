"""
Database seeding script for SymptoMap
Populates the database with realistic outbreak data for testing and demonstration
"""

import asyncio
from datetime import datetime, timedelta, timezone
from geoalchemy2.elements import WKTElement
import random

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.outbreak import Hospital, Outbreak
from app.models.user import User
from app.models.doctor import DoctorOutbreak, DoctorAlert


# Major Indian cities with coordinates
CITIES_DATA = [
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777, "state": "Maharashtra"},
    {"name": "Delhi", "lat": 28.7041, "lng": 77.1025, "state": "Delhi"},
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946, "state": "Karnataka"},
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707, "state": "Tamil Nadu"},
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639, "state": "West Bengal"},
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867, "state": "Telangana"},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567, "state": "Maharashtra"},
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714, "state": "Gujarat"},
    {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873, "state": "Rajasthan"},
    {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462, "state": "Uttar Pradesh"},
]

HOSPITAL_NAMES = [
    "City General Hospital",
    "Metro Medical Center",
    "District Health Center",
    "Apollo Specialty Hospital",
    "Fortis Healthcare",
    "Max Super Specialty",
    "AIIMS Medical College",
    "Government Hospital",
    "Red Cross Hospital",
    "Community Health Clinic",
]

DISEASES = [
    "Viral Fever",
    "Dengue",
    "Malaria",
    "Covid-19",
    "Flu",
    "Typhoid",
    "Chikungunya",
]

SEVERITIES = ["mild", "moderate", "severe"]


async def create_hospitals(db):
    """Create hospital records for each major city"""
    hospitals = []
    
    for city in CITIES_DATA:
        # Create 1-2 hospitals per city
        num_hospitals = random.randint(1, 2)
        
        for i in range(num_hospitals):
            hospital_name = f"{city['name']} {random.choice(HOSPITAL_NAMES)}"
            
            # Add slight randomness to coordinates (within ~5km)
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            
            hospital = Hospital(
                name=hospital_name,
                address=f"Sector {random.randint(1, 50)}, {city['name']}, {city['state']}",
                location=WKTElement(
                    f"POINT({city['lng'] + lng_offset} {city['lat'] + lat_offset})",
                    srid=4326
                ),
                city=city['name'],
                state=city['state'],
                country="India",
                pincode=f"{random.randint(100000, 999999)}",
                phone=f"+91-{random.randint(7000000000, 9999999999)}",
                email=f"contact@{hospital_name.lower().replace(' ', '')}.in",
                total_beds=random.randint(50, 500),
                icu_beds=random.randint(10, 50),
                available_beds=random.randint(10, 100),
                hospital_type=random.choice(["government", "private", "charitable"]),
                registration_number=f"REG{random.randint(10000, 99999)}"
            )
            
            db.add(hospital)
            hospitals.append(hospital)
    
    await db.commit()
    print(f"✅ Created {len(hospitals)} hospitals")
    return hospitals


async def create_admin_user(db):
    """Create an admin user for testing"""
    from app.core.security import get_password_hash
    
    admin = User(
        email="admin@symptomap.com",
        full_name="System Administrator",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_verified=True
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    print("✅ Created admin user (admin@symptomap.com / admin123)")
    return admin


async def create_outbreaks(db, hospitals, admin_user):
    """Create realistic outbreak records"""
    outbreaks = []
    
    # Create 15-25 outbreak records
    num_outbreaks = random.randint(18, 25)
    
    for i in range(num_outbreaks):
        hospital = random.choice(hospitals)
        disease = random.choice(DISEASES)
        
        # Weight severities (more mild/moderate, fewer severe)
        severity_weights = [0.5, 0.35, 0.15]  # mild, moderate, severe
        severity = random.choices(SEVERITIES, weights=severity_weights)[0]
        
        # Patient count based on severity
        if severity == "severe":
            patient_count = random.randint(50, 200)
        elif severity == "moderate":
            patient_count = random.randint(20, 80)
        else:
            patient_count = random.randint(5, 30)
        
        # Date within last 30 days
        days_ago = random.randint(1, 30)
        date_started = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        outbreak = Outbreak(
            hospital_id=hospital.id,
            reported_by=admin_user.id,
            disease_type=disease,
            patient_count=patient_count,
            date_started=date_started,
            severity=severity,
            age_distribution={
                "0-18": random.randint(10, 30),
                "19-40": random.randint(30, 50),
                "41-60": random.randint(15, 30),
                "60+": random.randint(5, 15)
            },
            gender_distribution={
                "male": random.randint(40, 60),
                "female": random.randint(40, 60)
            },
            symptoms=[
                random.choice(["Fever", "Cough", "Headache", "Body Ache", "Fatigue"])
                for _ in range(random.randint(2, 4))
            ],
            notes=f"Outbreak reported from {hospital.name}. Monitoring situation closely.",
            location=hospital.location,
            verified=random.choice([True, True, False])  # 66% verified
        )
        
        db.add(outbreak)
        outbreaks.append(outbreak)
    
    await db.commit()
    print(f"✅ Created {len(outbreaks)} outbreak records")
    
    # Print summary
    severity_counts = {s: sum(1 for o in outbreaks if o.severity == s) for s in SEVERITIES}
    print(f"   Breakdown: {severity_counts}")
    
    return outbreaks

async def create_doctor_data(db):
    """Create doctor submissions (pending and approved)"""
    # 1. Pending Outbreaks
    print("   Creating pending doctor outbreaks...")
    pending_locs = [
        {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126, "h": "Gandhi Medical College"},
        {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577, "h": "MY Hospital"},
        {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376, "h": "AIIMS Patna"},
    ]
    
    for i in range(15):
        loc = random.choice(pending_locs)
        disease = random.choice(DISEASES)
        doc_outbreak = DoctorOutbreak(
             disease_type=disease,
             patient_count=random.randint(5, 50),
             severity='moderate' if random.random() > 0.7 else 'mild',
             latitude=loc['lat'] + random.uniform(-0.05, 0.05),
             longitude=loc['lng'] + random.uniform(-0.05, 0.05),
             location_name=loc['h'],
             city=loc['city'],
             state=loc['state'],
             description=f"Suspected {disease} cluster reported.",
             date_reported=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
             submitted_by="dr_verification_test",
             status="pending"
        )
        db.add(doc_outbreak)
        
    # 2. Approved Outbreaks (for public view)
    print("   Creating approved doctor outbreaks...")
    for i in range(10):
        disease = random.choice(DISEASES)
        doc_outbreak = DoctorOutbreak(
             disease_type=disease,
             patient_count=random.randint(20, 100),
             severity='severe',
             latitude=20.5937 + random.uniform(-5, 5),
             longitude=78.9629 + random.uniform(-5, 5),
             location_name="City General Hospital",
             city="Nagpur",
             state="Maharashtra",
             description=f"Confirmed {disease} outbreak.",
             date_reported=datetime.now(timezone.utc) - timedelta(days=random.randint(2, 10)),
             submitted_by="dr_verification_test",
             status="approved"
        )
        db.add(doc_outbreak)
        
    await db.commit()
    print("✅ Created doctor outbreaks (pending & approved)")


async def seed_database():
    """Main seeding function"""
    print("\n🌱 Starting database seeding...\n")
    
    async with AsyncSessionLocal() as db:
        # Create hospitals
        hospitals = await create_hospitals(db)
        
        # Create admin user
        admin_user = await create_admin_user(db)
        
        # Create outbreaks
        outbreaks = await create_outbreaks(db, hospitals, admin_user)

        # Create doctor data
        await create_doctor_data(db)
    
    print("\n✨ Database seeding completed successfully!\n")
    print(f"Summary:")
    print(f"  - {len(hospitals)} hospitals across {len(CITIES_DATA)} cities")
    print(f"  - {len(outbreaks)} outbreak records")
    print(f"  - 1 admin user account")
    print(f"\nYou can now:")
    print(f"  1. Login as admin@symptomap.com / admin123")
    print(f"  2. View outbreaks on the map")
    print(f"  3. Add more outbreaks via Doctor Station")


if __name__ == "__main__":
    asyncio.run(seed_database())
