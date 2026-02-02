"""
Enhanced Production Data Seeder - 5000+ Outbreaks for ML Training
Seeds hospitals and outbreaks across all Indian states with proper city/state data
Includes specific zones: 2 in Delhi (1 red, 1 yellow), 2 yellow in Pune
"""

import asyncio
from datetime import datetime, timedelta, timezone
import random
import uuid

from app.core.database import AsyncSessionLocal
from app.models.outbreak import Hospital, Outbreak
from app.models.user import User
from sqlalchemy import select, delete

# Comprehensive India locations with proper city/state data
INDIA_LOCATIONS = [
    # Maharashtra - Major Cities
    {"city": "Mumbai Central", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"city": "Mumbai Suburbs", "state": "Maharashtra", "lat": 19.1136, "lng": 72.8697},
    {"city": "Thane", "state": "Maharashtra", "lat": 19.2183, "lng": 72.9781},
    {"city": "Pune East", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},  # Yellow Zone 1
    {"city": "Pune West", "state": "Maharashtra", "lat": 18.5018, "lng": 73.8069},  # Yellow Zone 2
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lng": 73.7898},
    {"city": "Aurangabad", "state": "Maharashtra", "lat": 19.8762, "lng": 75.3433},
    {"city": "Solapur", "state": "Maharashtra", "lat": 17.6599, "lng": 75.9064},
    {"city": "Kolhapur", "state": "Maharashtra", "lat": 16.7050, "lng": 74.2433},
    
    # Delhi NCR - Special Zones
    {"city": "New Delhi Central", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},  # Red Zone
    {"city": "South Delhi", "state": "Delhi", "lat": 28.5245, "lng": 77.2066},  # Yellow Zone
    {"city": "North Delhi", "state": "Delhi", "lat": 28.7041, "lng": 77.1025},
    {"city": "East Delhi", "state": "Delhi", "lat": 28.6280, "lng": 77.2949},
    {"city": "Gurgaon", "state": "Haryana", "lat": 28.4595, "lng": 77.0266},
    {"city": "Noida", "state": "Uttar Pradesh", "lat": 28.5355, "lng": 77.3910},
    {"city": "Faridabad", "state": "Haryana", "lat": 28.4089, "lng": 77.3178},
    {"city": "Ghaziabad", "state": "Uttar Pradesh", "lat": 28.6692, "lng": 77.4538},
    
    # Karnataka
    {"city": "Bangalore Central", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"city": "Bangalore North", "state": "Karnataka", "lat": 13.0358, "lng": 77.5970},
    {"city": "Bangalore South", "state": "Karnataka", "lat": 12.9141, "lng": 77.6411},
    {"city": "Mysore", "state": "Karnataka", "lat": 12.2958, "lng": 76.6394},
    {"city": "Mangalore", "state": "Karnataka", "lat": 12.9141, "lng": 74.8560},
    {"city": "Hubli-Dharwad", "state": "Karnataka", "lat": 15.3647, "lng": 75.1240},
    {"city": "Belgaum", "state": "Karnataka", "lat": 15.8497, "lng": 74.4977},
    
    # Tamil Nadu
    {"city": "Chennai Central", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    {"city": "Chennai South", "state": "Tamil Nadu", "lat": 12.9855, "lng": 80.2421},
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
    {"city": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lng": 78.1198},
    {"city": "Tiruchirappalli", "state": "Tamil Nadu", "lat": 10.7905, "lng": 78.7047},
    {"city": "Salem", "state": "Tamil Nadu", "lat": 11.6643, "lng": 78.1460},
    {"city": "Vellore", "state": "Tamil Nadu", "lat": 12.9165, "lng": 79.1325},
    
    # Gujarat
    {"city": "Ahmedabad East", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714},
    {"city": "Ahmedabad West", "state": "Gujarat", "lat": 23.0300, "lng": 72.5200},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311},
    {"city": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lng": 73.1812},
    {"city": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lng": 70.8022},
    {"city": "Gandhinagar", "state": "Gujarat", "lat": 23.2156, "lng": 72.6369},
    
    # Rajasthan
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125},
    {"city": "Ajmer", "state": "Rajasthan", "lat": 26.4499, "lng": 74.6399},
    {"city": "Kota", "state": "Rajasthan", "lat": 25.2138, "lng": 75.8648},
    {"city": "Bikaner", "state": "Rajasthan", "lat": 28.0229, "lng": 73.3119},
    
    # West Bengal
    {"city": "Kolkata Central", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    {"city": "Kolkata North", "state": "West Bengal", "lat": 22.6200, "lng": 88.3700},
    {"city": "Howrah", "state": "West Bengal", "lat": 22.5958, "lng": 88.2636},
    {"city": "Siliguri", "state": "West Bengal", "lat": 26.7271, "lng": 88.6393},
    {"city": "Durgapur", "state": "West Bengal", "lat": 23.5204, "lng": 87.3119},
    {"city": "Asansol", "state": "West Bengal", "lat": 23.6739, "lng": 86.9524},
    
    # Telangana
    {"city": "Hyderabad Central", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    {"city": "Secunderabad", "state": "Telangana", "lat": 17.4399, "lng": 78.4983},
    {"city": "Warangal", "state": "Telangana", "lat": 17.9784, "lng": 79.5941},
    {"city": "Nizamabad", "state": "Telangana", "lat": 18.6725, "lng": 78.0941},
    {"city": "Karimnagar", "state": "Telangana", "lat": 18.4386, "lng": 79.1288},
    
    # Andhra Pradesh
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
    {"city": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480},
    {"city": "Tirupati", "state": "Andhra Pradesh", "lat": 13.6288, "lng": 79.4192},
    {"city": "Guntur", "state": "Andhra Pradesh", "lat": 16.3067, "lng": 80.4365},
    {"city": "Nellore", "state": "Andhra Pradesh", "lat": 14.4426, "lng": 79.9865},
    {"city": "Kakinada", "state": "Andhra Pradesh", "lat": 16.9891, "lng": 82.2475},
    
    # Kerala
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366},
    {"city": "Kozhikode", "state": "Kerala", "lat": 11.2588, "lng": 75.7804},
    {"city": "Thrissur", "state": "Kerala", "lat": 10.5276, "lng": 76.2144},
    {"city": "Kannur", "state": "Kerala", "lat": 11.8745, "lng": 75.3704},
    {"city": "Kollam", "state": "Kerala", "lat": 8.8932, "lng": 76.6141},
    
    # Uttar Pradesh
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"city": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739},
    {"city": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lng": 78.0081},
    {"city": "Prayagraj", "state": "Uttar Pradesh", "lat": 25.4358, "lng": 81.8463},
    {"city": "Meerut", "state": "Uttar Pradesh", "lat": 28.9845, "lng": 77.7064},
    {"city": "Gorakhpur", "state": "Uttar Pradesh", "lat": 26.7606, "lng": 83.3732},
    
    # Madhya Pradesh
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
    {"city": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2183, "lng": 78.1828},
    {"city": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lng": 79.9864},
    {"city": "Ujjain", "state": "Madhya Pradesh", "lat": 23.1765, "lng": 75.7885},
    
    # Bihar
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376},
    {"city": "Gaya", "state": "Bihar", "lat": 24.7914, "lng": 85.0002},
    {"city": "Muzaffarpur", "state": "Bihar", "lat": 26.1209, "lng": 85.3647},
    {"city": "Bhagalpur", "state": "Bihar", "lat": 25.2425, "lng": 86.9842},
    {"city": "Darbhanga", "state": "Bihar", "lat": 26.1542, "lng": 85.8918},
    
    # Odisha
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245},
    {"city": "Cuttack", "state": "Odisha", "lat": 20.4625, "lng": 85.8830},
    {"city": "Rourkela", "state": "Odisha", "lat": 22.2604, "lng": 84.8536},
    {"city": "Berhampur", "state": "Odisha", "lat": 19.3150, "lng": 84.7941},
    
    # Punjab & Chandigarh
    {"city": "Chandigarh", "state": "Chandigarh", "lat": 30.7333, "lng": 76.7794},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lng": 75.8573},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723},
    {"city": "Jalandhar", "state": "Punjab", "lat": 31.3260, "lng": 75.5762},
    {"city": "Patiala", "state": "Punjab", "lat": 30.3398, "lng": 76.3869},
    
    # Jharkhand
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
    {"city": "Jamshedpur", "state": "Jharkhand", "lat": 22.8046, "lng": 86.2029},
    {"city": "Dhanbad", "state": "Jharkhand", "lat": 23.7957, "lng": 86.4304},
    {"city": "Bokaro", "state": "Jharkhand", "lat": 23.6693, "lng": 86.1511},
    
    # Chhattisgarh
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296},
    {"city": "Bhilai", "state": "Chhattisgarh", "lat": 21.2167, "lng": 81.4333},
    {"city": "Bilaspur", "state": "Chhattisgarh", "lat": 22.0796, "lng": 82.1391},
    {"city": "Korba", "state": "Chhattisgarh", "lat": 22.3595, "lng": 82.7501},
    
    # Assam & Northeast
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362},
    {"city": "Silchar", "state": "Assam", "lat": 24.8333, "lng": 92.8000},
    {"city": "Dibrugarh", "state": "Assam", "lat": 27.4728, "lng": 94.9119},
    {"city": "Jorhat", "state": "Assam", "lat": 26.7509, "lng": 94.2037},
    {"city": "Imphal", "state": "Manipur", "lat": 24.8170, "lng": 93.9368},
    {"city": "Shillong", "state": "Meghalaya", "lat": 25.5788, "lng": 91.8933},
    {"city": "Aizawl", "state": "Mizoram", "lat": 23.7271, "lng": 92.7176},
    {"city": "Agartala", "state": "Tripura", "lat": 23.8315, "lng": 91.2868},
    {"city": "Gangtok", "state": "Sikkim", "lat": 27.3389, "lng": 88.6065},
    {"city": "Itanagar", "state": "Arunachal Pradesh", "lat": 27.0844, "lng": 93.6053},
    {"city": "Kohima", "state": "Nagaland", "lat": 25.6751, "lng": 94.1086},
    
    # Uttarakhand
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lng": 78.0322},
    {"city": "Haridwar", "state": "Uttarakhand", "lat": 29.9457, "lng": 78.1642},
    {"city": "Rishikesh", "state": "Uttarakhand", "lat": 30.0869, "lng": 78.2676},
    {"city": "Haldwani", "state": "Uttarakhand", "lat": 29.2183, "lng": 79.5130},
    
    # Himachal Pradesh
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734},
    {"city": "Dharamshala", "state": "Himachal Pradesh", "lat": 32.2190, "lng": 76.3234},
    {"city": "Manali", "state": "Himachal Pradesh", "lat": 32.2396, "lng": 77.1887},
    {"city": "Kullu", "state": "Himachal Pradesh", "lat": 31.9592, "lng": 77.1089},
    
    # Jammu & Kashmir
    {"city": "Srinagar", "state": "Jammu & Kashmir", "lat": 34.0837, "lng": 74.7973},
    {"city": "Jammu", "state": "Jammu & Kashmir", "lat": 32.7266, "lng": 74.8570},
    {"city": "Leh", "state": "Ladakh", "lat": 34.1526, "lng": 77.5771},
    
    # Goa
    {"city": "Panaji", "state": "Goa", "lat": 15.4909, "lng": 73.8278},
    {"city": "Margao", "state": "Goa", "lat": 15.2832, "lng": 73.9862},
    {"city": "Vasco da Gama", "state": "Goa", "lat": 15.3982, "lng": 73.8113},
]

HOSPITAL_PREFIXES = [
    "City General", "Metro Medical", "District", "Apollo", "Fortis",
    "Max Super Specialty", "AIIMS", "Government Medical College",
    "Red Cross", "Community Health", "Civil", "Regional Medical",
    "Primary Health Center", "Multispecialty", "Care", "Life",
    "Sunshine", "Rainbow", "Golden", "Star", "Wellness"
]

DISEASES = ["Viral Fever", "Dengue", "Malaria", "Covid-19", "Flu", "Typhoid", "Chikungunya", "Hepatitis", "Cholera", "Tuberculosis"]
SEVERITIES = ["mild", "moderate", "severe", "critical"]

# Special zones configuration
SPECIAL_ZONES = {
    "New Delhi Central": {"severity": "severe", "min_cases": 150, "max_cases": 300},  # Red zone
    "South Delhi": {"severity": "moderate", "min_cases": 50, "max_cases": 100},  # Yellow zone
    "Pune East": {"severity": "moderate", "min_cases": 40, "max_cases": 80},  # Yellow zone
    "Pune West": {"severity": "moderate", "min_cases": 45, "max_cases": 90},  # Yellow zone
}


async def seed_5000_outbreaks():
    """Seed 5000+ outbreaks across all Indian states for ML training"""
    print("\n" + "="*60)
    print("🌱 ENHANCED PRODUCTION DATA SEEDER - 5000 Outbreaks")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as db:
        # Get or create admin user
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
        
        # Clear existing data for clean seed
        print("🗑️ Clearing existing outbreak data...")
        await db.execute(delete(Outbreak))
        await db.execute(delete(Hospital))
        await db.commit()
        
        # Create hospitals - 2-3 per location
        print("🏥 Creating hospitals...")
        hospitals = []
        hospital_by_city = {}
        
        for loc in INDIA_LOCATIONS:
            num_hospitals = random.randint(2, 3)
            hospital_by_city[loc['city']] = []
            
            for i in range(num_hospitals):
                prefix = random.choice(HOSPITAL_PREFIXES)
                hospital_name = f"{loc['city']} {prefix} Hospital"
                
                # Slight coordinate variation within city
                lat = loc['lat'] + random.uniform(-0.02, 0.02)
                lng = loc['lng'] + random.uniform(-0.02, 0.02)
                
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
                    email=f"info@{hospital_name.lower().replace(' ', '').replace(',', '')[:20]}.hospital.in",
                    total_beds=random.randint(100, 800),
                    icu_beds=random.randint(20, 100),
                    available_beds=random.randint(20, 200),
                    hospital_type=random.choice(["government", "private", "charitable"]),
                    registration_number=f"REG{random.randint(10000, 99999)}"
                )
                db.add(hospital)
                hospitals.append(hospital)
                hospital_by_city[loc['city']].append(hospital)
        
        await db.commit()
        
        # Refresh to get IDs
        for h in hospitals:
            await db.refresh(h)
        
        print(f"✅ Created {len(hospitals)} hospitals across {len(INDIA_LOCATIONS)} cities")
        
        # Create 5000 outbreaks
        print("\n🦠 Creating 5000 outbreaks...")
        outbreaks_created = 0
        target_outbreaks = 5000
        
        # First, create special zone outbreaks
        for city_name, config in SPECIAL_ZONES.items():
            if city_name in hospital_by_city:
                for hospital in hospital_by_city[city_name]:
                    # Create 3-5 outbreaks per hospital in special zones
                    for _ in range(random.randint(3, 5)):
                        days_ago = random.randint(1, 30)
                        date_started = datetime.now(timezone.utc) - timedelta(days=days_ago)
                        
                        outbreak = Outbreak(
                            hospital_id=hospital.id,
                            reported_by=admin.id,
                            disease_type=random.choice(DISEASES),
                            patient_count=random.randint(config["min_cases"], config["max_cases"]),
                            date_started=date_started,
                            date_reported=date_started + timedelta(hours=random.randint(1, 24)),
                            severity=config["severity"],
                            age_distribution={
                                "0-18": random.randint(10, 25),
                                "19-40": random.randint(30, 45),
                                "41-60": random.randint(20, 35),
                                "60+": random.randint(5, 15)
                            },
                            gender_distribution={
                                "male": random.randint(45, 55),
                                "female": random.randint(45, 55)
                            },
                            symptoms=random.sample(["Fever", "Cough", "Headache", "Body Ache", "Fatigue", "Nausea", "Vomiting", "Diarrhea", "Rash", "Joint Pain"], k=random.randint(3, 5)),
                            notes=f"Special monitoring zone - {config['severity']} outbreak",
                            latitude=hospital.latitude,
                            longitude=hospital.longitude,
                            location=hospital.location,
                            verified=True
                        )
                        db.add(outbreak)
                        outbreaks_created += 1
        
        await db.commit()
        print(f"   ✅ Created {outbreaks_created} special zone outbreaks")
        
        # Create remaining outbreaks distributed across all hospitals
        remaining = target_outbreaks - outbreaks_created
        outbreaks_per_hospital = remaining // len(hospitals)
        
        for hospital in hospitals:
            # Skip special zone hospitals (already processed)
            if hospital.city in SPECIAL_ZONES:
                continue
            
            # Create 10-50 outbreaks per hospital to reach 5000
            num_outbreaks = random.randint(max(5, outbreaks_per_hospital - 10), outbreaks_per_hospital + 20)
            
            for _ in range(num_outbreaks):
                if outbreaks_created >= target_outbreaks:
                    break
                
                # Weighted severity distribution
                severity = random.choices(
                    SEVERITIES,
                    weights=[0.40, 0.35, 0.20, 0.05]
                )[0]
                
                # Patient count based on severity
                if severity == "critical":
                    patient_count = random.randint(100, 300)
                elif severity == "severe":
                    patient_count = random.randint(50, 150)
                elif severity == "moderate":
                    patient_count = random.randint(20, 80)
                else:
                    patient_count = random.randint(5, 30)
                
                # Date within last 60 days for more historical data
                days_ago = random.randint(1, 60)
                date_started = datetime.now(timezone.utc) - timedelta(days=days_ago)
                
                outbreak = Outbreak(
                    hospital_id=hospital.id,
                    reported_by=admin.id,
                    disease_type=random.choice(DISEASES),
                    patient_count=patient_count,
                    date_started=date_started,
                    date_reported=date_started + timedelta(hours=random.randint(1, 48)),
                    severity=severity,
                    age_distribution={
                        "0-18": random.randint(8, 25),
                        "19-40": random.randint(25, 45),
                        "41-60": random.randint(15, 35),
                        "60+": random.randint(5, 20)
                    },
                    gender_distribution={
                        "male": random.randint(45, 55),
                        "female": random.randint(45, 55)
                    },
                    symptoms=random.sample(
                        ["Fever", "Cough", "Headache", "Body Ache", "Fatigue", "Nausea", "Vomiting", "Diarrhea", "Rash", "Joint Pain", "Chills", "Sore Throat"],
                        k=random.randint(2, 5)
                    ),
                    notes=f"Outbreak at {hospital.name}",
                    latitude=hospital.latitude,
                    longitude=hospital.longitude,
                    location=hospital.location,
                    verified=random.choice([True, True, True, False])  # 75% verified
                )
                db.add(outbreak)
                outbreaks_created += 1
                
                if outbreaks_created % 500 == 0:
                    await db.commit()
                    print(f"   ... {outbreaks_created} outbreaks created")
        
        await db.commit()
        
        # Summary
        print("\n" + "="*60)
        print("📊 SEEDING SUMMARY")
        print("="*60)
        print(f"✅ Hospitals created: {len(hospitals)}")
        print(f"✅ Outbreaks created: {outbreaks_created}")
        print(f"✅ States covered: {len(set(loc['state'] for loc in INDIA_LOCATIONS))}")
        print(f"✅ Cities covered: {len(INDIA_LOCATIONS)}")
        
        # Verify special zones
        print("\n🎯 Special Zones:")
        for city_name, config in SPECIAL_ZONES.items():
            result = await db.execute(
                select(Outbreak).join(Hospital).where(Hospital.city == city_name)
            )
            count = len(result.scalars().all())
            color = "🔴" if config["severity"] == "severe" else "🟡"
            print(f"   {color} {city_name}: {count} outbreaks ({config['severity']})")
        
        print("\n✨ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_5000_outbreaks())
