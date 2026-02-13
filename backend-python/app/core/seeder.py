"""
Database seeding script for SymptoMap
Populates the database with realistic outbreak data for testing and demonstration
"""

import asyncio
from datetime import datetime, timedelta, timezone
import random

from app.core.database import AsyncSessionLocal, Base, engine
from app.models.outbreak import Hospital, Outbreak
from app.models.user import User
from app.models.doctor import DoctorOutbreak, DoctorAlert


# Comprehensive list of major Indian cities with coordinates (All States)
CITIES_DATA = [
    # Rajasthan
    {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873, "state": "Rajasthan"},
    {"name": "Jodhpur", "lat": 26.2389, "lng": 73.0243, "state": "Rajasthan"},
    {"name": "Udaipur", "lat": 24.5854, "lng": 73.7125, "state": "Rajasthan"},
    {"name": "Ajmer", "lat": 26.4499, "lng": 74.6399, "state": "Rajasthan"},
    
    # Maharashtra
    {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777, "state": "Maharashtra"},
    {"name": "Pune", "lat": 18.5204, "lng": 73.8567, "state": "Maharashtra"},
    {"name": "Nagpur", "lat": 21.1458, "lng": 79.0882, "state": "Maharashtra"},
    {"name": "Nashik", "lat": 19.9975, "lng": 73.7898, "state": "Maharashtra"},
    
    # Delhi NCR
    {"name": "New Delhi", "lat": 28.6139, "lng": 77.2090, "state": "Delhi"},
    {"name": "Gurgaon", "lat": 28.4595, "lng": 77.0266, "state": "Haryana"},
    {"name": "Noida", "lat": 28.5355, "lng": 77.3910, "state": "Uttar Pradesh"},
    
    # Karnataka
    {"name": "Bangalore", "lat": 12.9716, "lng": 77.5946, "state": "Karnataka"},
    {"name": "Mysore", "lat": 12.2958, "lng": 76.6394, "state": "Karnataka"},
    {"name": "Mangalore", "lat": 12.9141, "lng": 74.8560, "state": "Karnataka"},
    
    # Tamil Nadu
    {"name": "Chennai", "lat": 13.0827, "lng": 80.2707, "state": "Tamil Nadu"},
    {"name": "Coimbatore", "lat": 11.0168, "lng": 76.9558, "state": "Tamil Nadu"},
    {"name": "Madurai", "lat": 9.9252, "lng": 78.1198, "state": "Tamil Nadu"},
    
    # Gujarat
    {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714, "state": "Gujarat"},
    {"name": "Surat", "lat": 21.1702, "lng": 72.8311, "state": "Gujarat"},
    {"name": "Vadodara", "lat": 22.3072, "lng": 73.1812, "state": "Gujarat"},
    {"name": "Rajkot", "lat": 22.3039, "lng": 70.8022, "state": "Gujarat"},
    
    # West Bengal
    {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639, "state": "West Bengal"},
    {"name": "Howrah", "lat": 22.5958, "lng": 88.2636, "state": "West Bengal"},
    {"name": "Siliguri", "lat": 26.7271, "lng": 88.6393, "state": "West Bengal"},
    
    # Telangana
    {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867, "state": "Telangana"},
    {"name": "Warangal", "lat": 17.9784, "lng": 79.5941, "state": "Telangana"},
    
    # Andhra Pradesh
    {"name": "Visakhapatnam", "lat": 17.6868, "lng": 83.2185, "state": "Andhra Pradesh"},
    {"name": "Vijayawada", "lat": 16.5062, "lng": 80.6480, "state": "Andhra Pradesh"},
    {"name": "Tirupati", "lat": 13.6288, "lng": 79.4192, "state": "Andhra Pradesh"},
    
    # Kerala
    {"name": "Kochi", "lat": 9.9312, "lng": 76.2673, "state": "Kerala"},
    {"name": "Thiruvananthapuram", "lat": 8.5241, "lng": 76.9366, "state": "Kerala"},
    {"name": "Kozhikode", "lat": 11.2588, "lng": 75.7804, "state": "Kerala"},
    
    # Uttar Pradesh
    {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462, "state": "Uttar Pradesh"},
    {"name": "Kanpur", "lat": 26.4499, "lng": 80.3319, "state": "Uttar Pradesh"},
    {"name": "Varanasi", "lat": 25.3176, "lng": 82.9739, "state": "Uttar Pradesh"},
    {"name": "Agra", "lat": 27.1767, "lng": 78.0081, "state": "Uttar Pradesh"},
    {"name": "Prayagraj", "lat": 25.4358, "lng": 81.8463, "state": "Uttar Pradesh"},
    
    # Madhya Pradesh
    {"name": "Bhopal", "lat": 23.2599, "lng": 77.4126, "state": "Madhya Pradesh"},
    {"name": "Indore", "lat": 22.7196, "lng": 75.8577, "state": "Madhya Pradesh"},
    {"name": "Gwalior", "lat": 26.2183, "lng": 78.1828, "state": "Madhya Pradesh"},
    {"name": "Jabalpur", "lat": 23.1815, "lng": 79.9864, "state": "Madhya Pradesh"},
    
    # Bihar
    {"name": "Patna", "lat": 25.5941, "lng": 85.1376, "state": "Bihar"},
    {"name": "Gaya", "lat": 24.7914, "lng": 85.0002, "state": "Bihar"},
    {"name": "Muzaffarpur", "lat": 26.1209, "lng": 85.3647, "state": "Bihar"},
    
    # Odisha
    {"name": "Bhubaneswar", "lat": 20.2961, "lng": 85.8245, "state": "Odisha"},
    {"name": "Cuttack", "lat": 20.4625, "lng": 85.8830, "state": "Odisha"},
    
    # Punjab
    {"name": "Chandigarh", "lat": 30.7333, "lng": 76.7794, "state": "Punjab"},
    {"name": "Ludhiana", "lat": 30.9010, "lng": 75.8573, "state": "Punjab"},
    {"name": "Amritsar", "lat": 31.6340, "lng": 74.8723, "state": "Punjab"},
    
    # Jharkhand
    {"name": "Ranchi", "lat": 23.3441, "lng": 85.3096, "state": "Jharkhand"},
    {"name": "Jamshedpur", "lat": 22.8046, "lng": 86.2029, "state": "Jharkhand"},
    
    # Chhattisgarh
    {"name": "Raipur", "lat": 21.2514, "lng": 81.6296, "state": "Chhattisgarh"},
    {"name": "Bhilai", "lat": 21.2167, "lng": 81.4333, "state": "Chhattisgarh"},
    
    # Assam
    {"name": "Guwahati", "lat": 26.1445, "lng": 91.7362, "state": "Assam"},
    {"name": "Silchar", "lat": 24.8333, "lng": 92.8000, "state": "Assam"},
    
    # Uttarakhand
    {"name": "Dehradun", "lat": 30.3165, "lng": 78.0322, "state": "Uttarakhand"},
    {"name": "Haridwar", "lat": 29.9457, "lng": 78.1642, "state": "Uttarakhand"},
    
    # Himachal Pradesh
    {"name": "Shimla", "lat": 31.1048, "lng": 77.1734, "state": "Himachal Pradesh"},
    {"name": "Dharamshala", "lat": 32.2190, "lng": 76.3234, "state": "Himachal Pradesh"},
    
    # Jammu & Kashmir
    {"name": "Srinagar", "lat": 34.0837, "lng": 74.7973, "state": "Jammu & Kashmir"},
    {"name": "Jammu", "lat": 32.7266, "lng": 74.8570, "state": "Jammu & Kashmir"},
    
    # Goa
    {"name": "Panaji", "lat": 15.4909, "lng": 73.8278, "state": "Goa"},
    
    # Northeast
    {"name": "Imphal", "lat": 24.8170, "lng": 93.9368, "state": "Manipur"},
    {"name": "Shillong", "lat": 25.5788, "lng": 91.8933, "state": "Meghalaya"},
    {"name": "Aizawl", "lat": 23.7271, "lng": 92.7176, "state": "Mizoram"},
    {"name": "Agartala", "lat": 23.8315, "lng": 91.2868, "state": "Tripura"},
    {"name": "Gangtok", "lat": 27.3389, "lng": 88.6065, "state": "Sikkim"},
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
            
            lat = city['lat'] + lat_offset
            lng = city['lng'] + lng_offset
            
            hospital = Hospital(
                name=hospital_name,
                address=f"Sector {random.randint(1, 50)}, {city['name']}, {city['state']}",
                latitude=lat,
                longitude=lng,
                location=f"POINT({lng} {lat})",  # Store as WKT string for SQLite compatibility
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
        password_hash=get_password_hash("admin123"),
        role="admin",
        verification_status="verified"
    )
    
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    
    print("✅ Created admin user (admin@symptomap.com / admin123)")
    return admin


async def create_doctor_user(db):
    """Create a default doctor user for testing"""
    from app.core.security import get_password_hash
    from app.core.config import settings
    
    # Use the configured doctor password
    password = settings.DOCTOR_PASSWORD
    
    # Check if exists
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == "doctor@symptomap.com"))
    if result.scalar_one_or_none():
        return
        
    doctor = User(
        email="doctor@symptomap.com",
        full_name="Dr. Sarah Johnson",
        password_hash=get_password_hash(password),
        role="doctor",
        verification_status="verified"
    )
    
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    
    print(f"✅ Created doctor user (doctor@symptomap.com / {password})")
    return doctor


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
            latitude=hospital.latitude,
            longitude=hospital.longitude,
            location=hospital.location,  # Already a string from hospital
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
        
        # Create doctor user
        await create_doctor_user(db)
        
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
