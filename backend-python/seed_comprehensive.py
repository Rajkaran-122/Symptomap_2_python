"""
COMPREHENSIVE DATA SEEDER
Seeds:
- 5000+ outbreaks with unique city names for proper map zones
- 200 pending approval requests
- 50 manual alerts
- Delhi: 3 zones (2 red, 1 yellow)
- Pune: 2 zones
"""

import asyncio
from datetime import datetime, timedelta, timezone
import random
import uuid

from app.core.database import AsyncSessionLocal
from app.models.outbreak import Hospital, Outbreak, Alert
from app.models.user import User
from sqlalchemy import select, delete, text

# UNIQUE CITY DEFINITIONS - Each city = 1 zone on map
INDIA_CITIES = [
    # DELHI NCR - 3 Special Zones
    {"city": "North Delhi", "state": "Delhi", "lat": 28.7041, "lng": 77.1025, "zone_type": "red"},
    {"city": "South Delhi", "state": "Delhi", "lat": 28.5244, "lng": 77.2066, "zone_type": "red"},
    {"city": "Central Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090, "zone_type": "yellow"},
    {"city": "East Delhi", "state": "Delhi", "lat": 28.6280, "lng": 77.2949, "zone_type": "normal"},
    {"city": "Gurgaon", "state": "Haryana", "lat": 28.4595, "lng": 77.0266, "zone_type": "normal"},
    {"city": "Noida", "state": "Uttar Pradesh", "lat": 28.5355, "lng": 77.3910, "zone_type": "normal"},
    {"city": "Ghaziabad", "state": "Uttar Pradesh", "lat": 28.6692, "lng": 77.4538, "zone_type": "normal"},
    {"city": "Faridabad", "state": "Haryana", "lat": 28.4089, "lng": 77.3178, "zone_type": "normal"},
    
    # PUNE - 2 Special Zones
    {"city": "Pune East", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567, "zone_type": "yellow"},
    {"city": "Pune West", "state": "Maharashtra", "lat": 18.5018, "lng": 73.8069, "zone_type": "yellow"},
    
    # MAHARASHTRA
    {"city": "Mumbai Central", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777, "zone_type": "red"},
    {"city": "Mumbai Suburbs", "state": "Maharashtra", "lat": 19.1136, "lng": 72.8697, "zone_type": "yellow"},
    {"city": "Thane", "state": "Maharashtra", "lat": 19.2183, "lng": 72.9781, "zone_type": "normal"},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882, "zone_type": "yellow"},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lng": 73.7898, "zone_type": "normal"},
    {"city": "Aurangabad", "state": "Maharashtra", "lat": 19.8762, "lng": 75.3433, "zone_type": "normal"},
    {"city": "Solapur", "state": "Maharashtra", "lat": 17.6599, "lng": 75.9064, "zone_type": "normal"},
    {"city": "Kolhapur", "state": "Maharashtra", "lat": 16.7050, "lng": 74.2433, "zone_type": "normal"},
    
    # KARNATAKA
    {"city": "Bangalore Central", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946, "zone_type": "red"},
    {"city": "Bangalore North", "state": "Karnataka", "lat": 13.0358, "lng": 77.5970, "zone_type": "yellow"},
    {"city": "Mysore", "state": "Karnataka", "lat": 12.2958, "lng": 76.6394, "zone_type": "normal"},
    {"city": "Mangalore", "state": "Karnataka", "lat": 12.9141, "lng": 74.8560, "zone_type": "normal"},
    {"city": "Hubli", "state": "Karnataka", "lat": 15.3647, "lng": 75.1240, "zone_type": "normal"},
    {"city": "Belgaum", "state": "Karnataka", "lat": 15.8497, "lng": 74.4977, "zone_type": "normal"},
    
    # TAMIL NADU
    {"city": "Chennai Central", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707, "zone_type": "red"},
    {"city": "Chennai South", "state": "Tamil Nadu", "lat": 12.9855, "lng": 80.2421, "zone_type": "yellow"},
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558, "zone_type": "yellow"},
    {"city": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lng": 78.1198, "zone_type": "normal"},
    {"city": "Tiruchirappalli", "state": "Tamil Nadu", "lat": 10.7905, "lng": 78.7047, "zone_type": "normal"},
    {"city": "Salem", "state": "Tamil Nadu", "lat": 11.6643, "lng": 78.1460, "zone_type": "normal"},
    
    # GUJARAT
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714, "zone_type": "red"},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311, "zone_type": "yellow"},
    {"city": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lng": 73.1812, "zone_type": "normal"},
    {"city": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lng": 70.8022, "zone_type": "normal"},
    {"city": "Gandhinagar", "state": "Gujarat", "lat": 23.2156, "lng": 72.6369, "zone_type": "normal"},
    
    # RAJASTHAN
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873, "zone_type": "yellow"},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243, "zone_type": "normal"},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125, "zone_type": "normal"},
    {"city": "Ajmer", "state": "Rajasthan", "lat": 26.4499, "lng": 74.6399, "zone_type": "normal"},
    {"city": "Kota", "state": "Rajasthan", "lat": 25.2138, "lng": 75.8648, "zone_type": "normal"},
    
    # WEST BENGAL
    {"city": "Kolkata Central", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639, "zone_type": "red"},
    {"city": "Kolkata North", "state": "West Bengal", "lat": 22.6200, "lng": 88.3700, "zone_type": "yellow"},
    {"city": "Howrah", "state": "West Bengal", "lat": 22.5958, "lng": 88.2636, "zone_type": "normal"},
    {"city": "Siliguri", "state": "West Bengal", "lat": 26.7271, "lng": 88.6393, "zone_type": "normal"},
    {"city": "Durgapur", "state": "West Bengal", "lat": 23.5204, "lng": 87.3119, "zone_type": "normal"},
    
    # TELANGANA
    {"city": "Hyderabad Central", "state": "Telangana", "lat": 17.3850, "lng": 78.4867, "zone_type": "red"},
    {"city": "Secunderabad", "state": "Telangana", "lat": 17.4399, "lng": 78.4983, "zone_type": "yellow"},
    {"city": "Warangal", "state": "Telangana", "lat": 17.9784, "lng": 79.5941, "zone_type": "normal"},
    {"city": "Nizamabad", "state": "Telangana", "lat": 18.6725, "lng": 78.0941, "zone_type": "normal"},
    
    # ANDHRA PRADESH
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185, "zone_type": "yellow"},
    {"city": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480, "zone_type": "normal"},
    {"city": "Tirupati", "state": "Andhra Pradesh", "lat": 13.6288, "lng": 79.4192, "zone_type": "normal"},
    {"city": "Guntur", "state": "Andhra Pradesh", "lat": 16.3067, "lng": 80.4365, "zone_type": "normal"},
    
    # KERALA
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673, "zone_type": "yellow"},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366, "zone_type": "normal"},
    {"city": "Kozhikode", "state": "Kerala", "lat": 11.2588, "lng": 75.7804, "zone_type": "normal"},
    {"city": "Thrissur", "state": "Kerala", "lat": 10.5276, "lng": 76.2144, "zone_type": "normal"},
    
    # UTTAR PRADESH
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462, "zone_type": "yellow"},
    {"city": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319, "zone_type": "normal"},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739, "zone_type": "normal"},
    {"city": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lng": 78.0081, "zone_type": "normal"},
    {"city": "Prayagraj", "state": "Uttar Pradesh", "lat": 25.4358, "lng": 81.8463, "zone_type": "normal"},
    {"city": "Meerut", "state": "Uttar Pradesh", "lat": 28.9845, "lng": 77.7064, "zone_type": "normal"},
    
    # MADHYA PRADESH
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126, "zone_type": "yellow"},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577, "zone_type": "normal"},
    {"city": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2183, "lng": 78.1828, "zone_type": "normal"},
    {"city": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lng": 79.9864, "zone_type": "normal"},
    
    # BIHAR
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376, "zone_type": "yellow"},
    {"city": "Gaya", "state": "Bihar", "lat": 24.7914, "lng": 85.0002, "zone_type": "normal"},
    {"city": "Muzaffarpur", "state": "Bihar", "lat": 26.1209, "lng": 85.3647, "zone_type": "normal"},
    
    # ODISHA
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245, "zone_type": "normal"},
    {"city": "Cuttack", "state": "Odisha", "lat": 20.4625, "lng": 85.8830, "zone_type": "normal"},
    {"city": "Rourkela", "state": "Odisha", "lat": 22.2604, "lng": 84.8536, "zone_type": "normal"},
    
    # PUNJAB
    {"city": "Chandigarh", "state": "Chandigarh", "lat": 30.7333, "lng": 76.7794, "zone_type": "normal"},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lng": 75.8573, "zone_type": "normal"},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723, "zone_type": "normal"},
    
    # JHARKHAND
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096, "zone_type": "normal"},
    {"city": "Jamshedpur", "state": "Jharkhand", "lat": 22.8046, "lng": 86.2029, "zone_type": "normal"},
    {"city": "Dhanbad", "state": "Jharkhand", "lat": 23.7957, "lng": 86.4304, "zone_type": "normal"},
    
    # CHHATTISGARH
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296, "zone_type": "normal"},
    {"city": "Bhilai", "state": "Chhattisgarh", "lat": 21.2167, "lng": 81.4333, "zone_type": "normal"},
    
    # ASSAM & NORTHEAST
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362, "zone_type": "normal"},
    {"city": "Dibrugarh", "state": "Assam", "lat": 27.4728, "lng": 94.9119, "zone_type": "normal"},
    {"city": "Imphal", "state": "Manipur", "lat": 24.8170, "lng": 93.9368, "zone_type": "normal"},
    {"city": "Shillong", "state": "Meghalaya", "lat": 25.5788, "lng": 91.8933, "zone_type": "normal"},
    {"city": "Aizawl", "state": "Mizoram", "lat": 23.7271, "lng": 92.7176, "zone_type": "normal"},
    {"city": "Agartala", "state": "Tripura", "lat": 23.8315, "lng": 91.2868, "zone_type": "normal"},
    {"city": "Gangtok", "state": "Sikkim", "lat": 27.3389, "lng": 88.6065, "zone_type": "normal"},
    
    # UTTARAKHAND
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lng": 78.0322, "zone_type": "normal"},
    {"city": "Haridwar", "state": "Uttarakhand", "lat": 29.9457, "lng": 78.1642, "zone_type": "normal"},
    
    # HIMACHAL PRADESH
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734, "zone_type": "normal"},
    {"city": "Dharamshala", "state": "Himachal Pradesh", "lat": 32.2190, "lng": 76.3234, "zone_type": "normal"},
    
    # JAMMU & KASHMIR
    {"city": "Srinagar", "state": "Jammu & Kashmir", "lat": 34.0837, "lng": 74.7973, "zone_type": "normal"},
    {"city": "Jammu", "state": "Jammu & Kashmir", "lat": 32.7266, "lng": 74.8570, "zone_type": "normal"},
    
    # GOA
    {"city": "Panaji", "state": "Goa", "lat": 15.4909, "lng": 73.8278, "zone_type": "normal"},
    {"city": "Margao", "state": "Goa", "lat": 15.2832, "lng": 73.9862, "zone_type": "normal"},
]

HOSPITAL_NAMES = [
    "City Hospital", "General Hospital", "Medical Center", "Apollo Hospital",
    "Fortis Hospital", "Max Hospital", "AIIMS", "Government Hospital",
    "District Hospital", "Civil Hospital", "Primary Health Center"
]

DISEASES = ["Viral Fever", "Dengue", "Malaria", "Covid-19", "Flu", "Typhoid", "Chikungunya", "Hepatitis", "Cholera", "Tuberculosis"]


async def seed_comprehensive_data():
    """Seed comprehensive data for all features"""
    print("\n" + "="*70)
    print("🌱 COMPREHENSIVE DATA SEEDER")
    print("="*70 + "\n")
    
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
        
        # Get or create doctor user
        result = await db.execute(select(User).where(User.role == "doctor").limit(1))
        doctor = result.scalar_one_or_none()
        
        if not doctor:
            from app.core.security import get_password_hash
            doctor = User(
                email="doctor@hospital.com",
                full_name="Dr. Medical Professional",
                password_hash=get_password_hash("doctor123"),
                role="doctor",
                verification_status="verified"
            )
            db.add(doctor)
            await db.commit()
            await db.refresh(doctor)
            print("✅ Created doctor user")
        
        # Clear existing data
        print("🗑️ Clearing existing data...")
        await db.execute(delete(Outbreak))
        await db.execute(delete(Hospital))
        await db.execute(text("DELETE FROM doctor_outbreaks"))
        await db.commit()
        
        # ========================================
        # PHASE 1: Create Hospitals (1 per city)
        # ========================================
        print("\n🏥 Creating hospitals...")
        hospitals = {}
        
        for i, city_data in enumerate(INDIA_CITIES):
            hospital_name = f"{city_data['city']} {random.choice(HOSPITAL_NAMES)}"
            
            hospital = Hospital(
                name=hospital_name,
                address=f"Main Road, {city_data['city']}, {city_data['state']}",
                latitude=city_data['lat'],
                longitude=city_data['lng'],
                city=city_data['city'],  # UNIQUE city name = unique zone
                state=city_data['state'],
                country="India",
                pincode=f"{random.randint(100000, 999999)}",
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                email=f"info@hospital{i}.in",
                total_beds=random.randint(100, 500),
                icu_beds=random.randint(10, 50),
                available_beds=random.randint(20, 100),
                hospital_type=random.choice(["government", "private"]),
                registration_number=f"REG{random.randint(10000, 99999)}"
            )
            db.add(hospital)
            hospitals[city_data['city']] = {"hospital": hospital, "zone_type": city_data['zone_type']}
        
        await db.commit()
        
        # Refresh to get IDs
        for city, data in hospitals.items():
            await db.refresh(data['hospital'])
        
        print(f"✅ Created {len(hospitals)} hospitals in {len(hospitals)} unique zones")
        
        # ========================================
        # PHASE 2: Create 5000+ Outbreaks
        # ========================================
        print("\n🦠 Creating 5000 outbreaks...")
        outbreaks_created = 0
        target_outbreaks = 5000
        
        now = datetime.now(timezone.utc)
        
        for city, data in hospitals.items():
            hospital = data['hospital']
            zone_type = data['zone_type']
            
            # Determine outbreak count and severity based on zone type
            if zone_type == "red":
                num_outbreaks = random.randint(80, 120)  # High outbreak count
                severity_weights = [0.1, 0.2, 0.5, 0.2]  # mild, moderate, severe, critical
            elif zone_type == "yellow":
                num_outbreaks = random.randint(40, 70)
                severity_weights = [0.2, 0.5, 0.25, 0.05]
            else:
                num_outbreaks = random.randint(20, 50)
                severity_weights = [0.5, 0.35, 0.12, 0.03]
            
            for _ in range(num_outbreaks):
                if outbreaks_created >= target_outbreaks:
                    break
                
                severity = random.choices(
                    ["mild", "moderate", "severe", "critical"],
                    weights=severity_weights
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
                
                days_ago = random.randint(1, 60)
                date_started = now - timedelta(days=days_ago)
                
                outbreak = Outbreak(
                    hospital_id=hospital.id,
                    reported_by=admin.id,
                    disease_type=random.choice(DISEASES),
                    patient_count=patient_count,
                    date_started=date_started,
                    date_reported=date_started + timedelta(hours=random.randint(1, 48)),
                    severity=severity,
                    age_distribution={
                        "0-18": random.randint(5, 25),
                        "19-40": random.randint(25, 45),
                        "41-60": random.randint(15, 35),
                        "60+": random.randint(5, 20)
                    },
                    gender_distribution={
                        "male": random.randint(45, 55),
                        "female": 100 - random.randint(45, 55)
                    },
                    symptoms=random.sample(
                        ["Fever", "Cough", "Headache", "Body Ache", "Fatigue", "Nausea", "Vomiting", "Diarrhea", "Rash", "Joint Pain"],
                        k=random.randint(2, 5)
                    ),
                    notes=f"Outbreak at {hospital.name} - {zone_type} zone",
                    latitude=hospital.latitude + random.uniform(-0.01, 0.01),
                    longitude=hospital.longitude + random.uniform(-0.01, 0.01),
                    verified=True
                )
                db.add(outbreak)
                outbreaks_created += 1
                
                if outbreaks_created % 500 == 0:
                    await db.commit()
                    print(f"   ... {outbreaks_created} outbreaks created")
        
        await db.commit()
        print(f"✅ Created {outbreaks_created} outbreaks")
        
        # ========================================
        # PHASE 3: Create 200 Pending Approvals
        # ========================================
        print("\n📋 Creating 200 pending approval requests...")
        
        try:
            # Check if DoctorOutbreak table exists
            await db.execute(text("SELECT 1 FROM doctor_outbreaks LIMIT 1"))
        except:
            # Create table if not exists
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS doctor_outbreaks (
                    id TEXT PRIMARY KEY,
                    doctor_id TEXT,
                    hospital_name TEXT,
                    disease_type TEXT,
                    patient_count INTEGER,
                    severity TEXT,
                    symptoms TEXT,
                    notes TEXT,
                    latitude REAL,
                    longitude REAL,
                    status TEXT DEFAULT 'pending',
                    submitted_at TEXT,
                    reviewed_at TEXT,
                    reviewed_by TEXT
                )
            """))
            await db.commit()
        
        approval_count = 0
        for i in range(200):
            city_data = random.choice(INDIA_CITIES)
            hospital_name = f"{city_data['city']} {random.choice(HOSPITAL_NAMES)}"
            
            approval_id = str(uuid.uuid4())
            days_ago = random.randint(1, 14)
            submitted_at = (now - timedelta(days=days_ago)).isoformat()
            
            await db.execute(text("""
                INSERT INTO doctor_outbreaks 
                (id, doctor_id, hospital_name, disease_type, patient_count, severity, symptoms, notes, latitude, longitude, status, submitted_at)
                VALUES (:id, :doctor_id, :hospital_name, :disease_type, :patient_count, :severity, :symptoms, :notes, :lat, :lng, 'pending', :submitted_at)
            """), {
                "id": approval_id,
                "doctor_id": str(doctor.id),
                "hospital_name": hospital_name,
                "disease_type": random.choice(DISEASES),
                "patient_count": random.randint(10, 100),
                "severity": random.choice(["mild", "moderate", "severe"]),
                "symptoms": ",".join(random.sample(["Fever", "Cough", "Headache", "Fatigue"], k=2)),
                "notes": f"Doctor submission #{i+1} from {city_data['city']}",
                "lat": city_data['lat'],
                "lng": city_data['lng'],
                "submitted_at": submitted_at
            })
            approval_count += 1
        
        await db.commit()
        print(f"✅ Created {approval_count} pending approval requests")
        
        # ========================================
        # PHASE 4: Create 50 Manual Alerts
        # ========================================
        print("\n🔔 Creating 50 manual alerts...")
        
        alert_types = ["outbreak", "high_risk", "critical", "warning"]
        severities = ["info", "warning", "critical"]
        
        for i in range(50):
            city_data = random.choice(INDIA_CITIES)
            days_ago = random.randint(0, 7)
            
            alert = Alert(
                alert_type=random.choice(alert_types),
                severity=random.choice(severities),
                title=f"Alert: {random.choice(DISEASES)} outbreak in {city_data['city']}",
                message=f"Health alert for {city_data['city']}, {city_data['state']}. Please take necessary precautions.",
                zone_name=city_data['city'],
                recipients={"emails": ["admin@symptomap.com"], "manual": True},
                delivery_status={"email": "sent"},
                acknowledged_by=[]
            )
            db.add(alert)
        
        await db.commit()
        print("✅ Created 50 manual alerts")
        
        # ========================================
        # SUMMARY
        # ========================================
        print("\n" + "="*70)
        print("📊 SEEDING SUMMARY")
        print("="*70)
        print(f"✅ Hospitals (unique zones): {len(hospitals)}")
        print(f"✅ Outbreaks: {outbreaks_created}")
        print(f"✅ Pending Approvals: {approval_count}")
        print(f"✅ Manual Alerts: 50")
        
        # Count special zones
        red_zones = [c for c in INDIA_CITIES if c['zone_type'] == 'red']
        yellow_zones = [c for c in INDIA_CITIES if c['zone_type'] == 'yellow']
        
        print(f"\n🔴 Red Zones: {len(red_zones)} cities")
        for z in red_zones:
            print(f"   - {z['city']}, {z['state']}")
        
        print(f"\n🟡 Yellow Zones: {len(yellow_zones)} cities")
        for z in yellow_zones[:5]:
            print(f"   - {z['city']}, {z['state']}")
        if len(yellow_zones) > 5:
            print(f"   ... and {len(yellow_zones) - 5} more")
        
        print("\n✨ Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_comprehensive_data())
