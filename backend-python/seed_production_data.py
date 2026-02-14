"""
Production Data Seeder - Multi-State Hospitals and Outbreaks
Seeds 120+ hospitals across all Indian states with 250+ outbreak records
"""

import asyncio
from datetime import datetime, timedelta, timezone
import random

from app.core.database import AsyncSessionLocal
from app.models.outbreak import Hospital, Outbreak
from app.models.user import User

# All Indian states and UTs with major cities
INDIA_LOCATIONS = [
    # Maharashtra
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lng": 73.7898},
    {"city": "Aurangabad", "state": "Maharashtra", "lat": 19.8762, "lng": 75.3433},
    
    # Delhi & NCR
    {"city": "New Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"city": "Gurgaon", "state": "Haryana", "lat": 28.4595, "lng": 77.0266},
    {"city": "Noida", "state": "Uttar Pradesh", "lat": 28.5355, "lng": 77.3910},
    {"city": "Faridabad", "state": "Haryana", "lat": 28.4089, "lng": 77.3178},
    
    # Karnataka
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"city": "Mysore", "state": "Karnataka", "lat": 12.2958, "lng": 76.6394},
    {"city": "Mangalore", "state": "Karnataka", "lat": 12.9141, "lng": 74.8560},
    {"city": "Hubli", "state": "Karnataka", "lat": 15.3647, "lng": 75.1240},
    
    # Tamil Nadu
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
    {"city": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lng": 78.1198},
    {"city": "Trichy", "state": "Tamil Nadu", "lat": 10.7905, "lng": 78.7047},
    
    # Gujarat
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311},
    {"city": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lng": 73.1812},
    {"city": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lng": 70.8022},
    
    # Rajasthan
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125},
    {"city": "Ajmer", "state": "Rajasthan", "lat": 26.4499, "lng": 74.6399},
    
    # West Bengal
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    {"city": "Howrah", "state": "West Bengal", "lat": 22.5958, "lng": 88.2636},
    {"city": "Siliguri", "state": "West Bengal", "lat": 26.7271, "lng": 88.6393},
    {"city": "Durgapur", "state": "West Bengal", "lat": 23.5204, "lng": 87.3119},
    
    # Telangana
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    {"city": "Warangal", "state": "Telangana", "lat": 17.9784, "lng": 79.5941},
    {"city": "Nizamabad", "state": "Telangana", "lat": 18.6725, "lng": 78.0941},
    
    # Andhra Pradesh
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
    {"city": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480},
    {"city": "Tirupati", "state": "Andhra Pradesh", "lat": 13.6288, "lng": 79.4192},
    {"city": "Guntur", "state": "Andhra Pradesh", "lat": 16.3067, "lng": 80.4365},
    
    # Kerala
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366},
    {"city": "Kozhikode", "state": "Kerala", "lat": 11.2588, "lng": 75.7804},
    {"city": "Thrissur", "state": "Kerala", "lat": 10.5276, "lng": 76.2144},
    
    # Uttar Pradesh
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"city": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739},
    {"city": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lng": 78.0081},
    {"city": "Prayagraj", "state": "Uttar Pradesh", "lat": 25.4358, "lng": 81.8463},
    
    # Madhya Pradesh
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
    {"city": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2183, "lng": 78.1828},
    {"city": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lng": 79.9864},
    
    # Bihar
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376},
    {"city": "Gaya", "state": "Bihar", "lat": 24.7914, "lng": 85.0002},
    {"city": "Muzaffarpur", "state": "Bihar", "lat": 26.1209, "lng": 85.3647},
    {"city": "Bhagalpur", "state": "Bihar", "lat": 25.2425, "lng": 86.9842},
    
    # Odisha
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245},
    {"city": "Cuttack", "state": "Odisha", "lat": 20.4625, "lng": 85.8830},
    {"city": "Rourkela", "state": "Odisha", "lat": 22.2604, "lng": 84.8536},
    
    # Punjab
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lng": 75.8573},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723},
    {"city": "Jalandhar", "state": "Punjab", "lat": 31.3260, "lng": 75.5762},
    
    # Jharkhand
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
    {"city": "Jamshedpur", "state": "Jharkhand", "lat": 22.8046, "lng": 86.2029},
    {"city": "Dhanbad", "state": "Jharkhand", "lat": 23.7957, "lng": 86.4304},
    
    # Chhattisgarh
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296},
    {"city": "Bhilai", "state": "Chhattisgarh", "lat": 21.2167, "lng": 81.4333},
    {"city": "Bilaspur", "state": "Chhattisgarh", "lat": 22.0796, "lng": 82.1391},
    
    # Assam
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362},
    {"city": "Silchar", "state": "Assam", "lat": 24.8333, "lng": 92.8000},
    {"city": "Dibrugarh", "state": "Assam", "lat": 27.4728, "lng": 94.9119},
    
    # Uttarakhand
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lng": 78.0322},
    {"city": "Haridwar", "state": "Uttarakhand", "lat": 29.9457, "lng": 78.1642},
    {"city": "Rishikesh", "state": "Uttarakhand", "lat": 30.0869, "lng": 78.2676},
    
    # Himachal Pradesh
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734},
    {"city": "Dharamshala", "state": "Himachal Pradesh", "lat": 32.2190, "lng": 76.3234},
    {"city": "Manali", "state": "Himachal Pradesh", "lat": 32.2396, "lng": 77.1887},
    
    # Jammu & Kashmir
    {"city": "Srinagar", "state": "Jammu & Kashmir", "lat": 34.0837, "lng": 74.7973},
    {"city": "Jammu", "state": "Jammu & Kashmir", "lat": 32.7266, "lng": 74.8570},
    
    # Goa
    {"city": "Panaji", "state": "Goa", "lat": 15.4909, "lng": 73.8278},
    {"city": "Margao", "state": "Goa", "lat": 15.2832, "lng": 73.9862},
    
    # Northeast States
    {"city": "Imphal", "state": "Manipur", "lat": 24.8170, "lng": 93.9368},
    {"city": "Shillong", "state": "Meghalaya", "lat": 25.5788, "lng": 91.8933},
    {"city": "Aizawl", "state": "Mizoram", "lat": 23.7271, "lng": 92.7176},
    {"city": "Agartala", "state": "Tripura", "lat": 23.8315, "lng": 91.2868},
    {"city": "Gangtok", "state": "Sikkim", "lat": 27.3389, "lng": 88.6065},
    {"city": "Itanagar", "state": "Arunachal Pradesh", "lat": 27.0844, "lng": 93.6053},
    {"city": "Kohima", "state": "Nagaland", "lat": 25.6751, "lng": 94.1086},
]

HOSPITAL_NAMES = [
    "City General Hospital",
    "Metro Medical Center",
    "District Health Center",
    "Apollo Hospital",
    "Fortis Healthcare",
    "Max Super Specialty",
    "AIIMS",
    "Government Medical College",
    "Red Cross Hospital",
    "Community Health Clinic",
    "Civil Hospital",
    "Regional Medical Center",
    "Primary Health Center",
    "Multispecialty Hospital",
]

DISEASES = ["Viral Fever", "Dengue", "Malaria", "Covid-19", "Flu", "Typhoid", "Chikungunya", "Hepatitis"]
SEVERITIES = ["mild", "moderate", "severe", "critical"]


async def seed_hospitals_and_outbreaks():
    """Seed hospitals and outbreaks across all Indian states"""
    print("\n🌱 Starting Production Data Seeding...\n")
    
    async with AsyncSessionLocal() as db:
        # Check for existing admin user
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.role == "admin").limit(1))
        admin = result.scalar_one_or_none()
        
        if not admin:
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
            print("✅ Created admin user")

        # Check for existing patient user
        result = await db.execute(select(User).where(User.email == "user@symptomap.com").limit(1))
        patient = result.scalar_one_or_none()
        
        if not patient:
            from app.core.security import get_password_hash
            patient = User(
                email="user@symptomap.com",
                full_name="Demo User",
                password_hash=get_password_hash("user123"),
                role="patient",
                verification_status="verified",
                is_active=True,
                is_verified=True
            )
            db.add(patient)
            await db.commit()
            print("✅ Created default patient user (user@symptomap.com)")
        
        # Create hospitals - 1-2 per city
        hospitals = []
        for loc in INDIA_LOCATIONS:
            num_hospitals = random.randint(1, 2)
            for i in range(num_hospitals):
                hospital_name = f"{loc['city']} {random.choice(HOSPITAL_NAMES)}"
                
                # Slight coordinate variation
                lat = loc['lat'] + random.uniform(-0.03, 0.03)
                lng = loc['lng'] + random.uniform(-0.03, 0.03)
                
                hospital = Hospital(
                    name=hospital_name,
                    address=f"Sector {random.randint(1, 50)}, {loc['city']}, {loc['state']}",
                    latitude=lat,
                    longitude=lng,
                    location=f"POINT({lng} {lat})",
                    city=loc['city'],
                    state=loc['state'],
                    country="India",
                    pincode=f"{random.randint(100000, 999999)}",
                    phone=f"+91-{random.randint(7000000000, 9999999999)}",
                    email=f"contact@{hospital_name.lower().replace(' ', '').replace(',', '')}hospital.in",
                    total_beds=random.randint(50, 500),
                    icu_beds=random.randint(10, 50),
                    available_beds=random.randint(10, 100),
                    hospital_type=random.choice(["government", "private", "charitable"]),
                    registration_number=f"REG{random.randint(10000, 99999)}"
                )
                db.add(hospital)
                hospitals.append(hospital)
        
        await db.commit()
        print(f"✅ Created {len(hospitals)} hospitals across {len(set(loc['state'] for loc in INDIA_LOCATIONS))} states")
        
        # Refresh to get IDs
        for h in hospitals:
            await db.refresh(h)
        
        # Create outbreaks
        outbreaks = []
        num_outbreaks = 250
        
        for i in range(num_outbreaks):
            hospital = random.choice(hospitals)
            disease = random.choice(DISEASES)
            
            # Weight severities
            severity = random.choices(SEVERITIES, weights=[0.4, 0.35, 0.2, 0.05])[0]
            
            # Patient count based on severity
            if severity == "critical":
                patient_count = random.randint(100, 300)
            elif severity == "severe":
                patient_count = random.randint(50, 150)
            elif severity == "moderate":
                patient_count = random.randint(20, 80)
            else:
                patient_count = random.randint(5, 30)
            
            # Date within last 30 days
            days_ago = random.randint(1, 30)
            date_started = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            outbreak = Outbreak(
                hospital_id=hospital.id,
                reported_by=admin.id,
                disease_type=disease,
                patient_count=patient_count,
                date_started=date_started,
                date_reported=date_started + timedelta(hours=random.randint(1, 24)),
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
                    random.choice(["Fever", "Cough", "Headache", "Body Ache", "Fatigue", "Nausea", "Vomiting"])
                    for _ in range(random.randint(2, 4))
                ],
                notes=f"Outbreak of {disease} at {hospital.name}",
                latitude=hospital.latitude,
                longitude=hospital.longitude,
                location=hospital.location,
                verified=random.choice([True, True, True, False])  # 75% verified
            )
            db.add(outbreak)
            outbreaks.append(outbreak)
        
        await db.commit()
        print(f"✅ Created {len(outbreaks)} outbreak records")
        
        # Summary
        severity_counts = {s: sum(1 for o in outbreaks if o.severity == s) for s in SEVERITIES}
        disease_counts = {d: sum(1 for o in outbreaks if o.disease_type == d) for d in DISEASES}
        
        print(f"\n📊 Summary:")
        print(f"   Severities: {severity_counts}")
        print(f"   Top Diseases: {dict(sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:5])}")
        print(f"\n✨ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_hospitals_and_outbreaks())
