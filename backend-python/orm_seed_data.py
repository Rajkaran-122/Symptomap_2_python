#!/usr/bin/env python3
"""
ORM-based Production Data Seeder for SymptoMap
Seeds 5000 outbreaks, 200 pending approvals, and 100 alerts using SQLAlchemy async
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, timezone
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Database URL
DATABASE_URL = "sqlite+aiosqlite:///./symptomap.db"

# Configuration
TOTAL_OUTBREAKS = 5000
PENDING_APPROVALS = 200
TOTAL_ALERTS = 100

# Data
CITIES = [
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"city": "Delhi", "state": "Delhi", "lat": 28.7041, "lng": 77.1025},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376},
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882},
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
    {"city": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311},
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366},
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362},
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296},
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245},
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794},
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lng": 78.0322},
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734},
    {"city": "Srinagar", "state": "J&K", "lat": 34.0837, "lng": 74.7973},
    {"city": "Jammu", "state": "J&K", "lat": 32.7266, "lng": 74.8570},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lng": 75.8573},
    {"city": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lng": 78.0081},
    {"city": "Meerut", "state": "Uttar Pradesh", "lat": 28.9845, "lng": 77.7064},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lng": 73.7898},
    {"city": "Aurangabad", "state": "Maharashtra", "lat": 19.8762, "lng": 75.3433},
    {"city": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lng": 70.8022},
    {"city": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lng": 73.1812},
    {"city": "Mangalore", "state": "Karnataka", "lat": 12.9141, "lng": 74.8560},
    {"city": "Mysore", "state": "Karnataka", "lat": 12.2958, "lng": 76.6394},
    {"city": "Hubli", "state": "Karnataka", "lat": 15.3647, "lng": 75.1240},
    {"city": "Salem", "state": "Tamil Nadu", "lat": 11.6643, "lng": 78.1460},
    {"city": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lng": 78.1198},
    {"city": "Tiruchirappalli", "state": "Tamil Nadu", "lat": 10.7905, "lng": 78.7047},
    {"city": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480},
    {"city": "Warangal", "state": "Telangana", "lat": 17.9784, "lng": 79.5941},
    {"city": "Guntur", "state": "Andhra Pradesh", "lat": 16.3067, "lng": 80.4365},
    {"city": "Cuttack", "state": "Odisha", "lat": 20.4625, "lng": 85.8830},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125},
]

DISEASES = [
    "Dengue", "Malaria", "Typhoid", "Cholera", "COVID-19", 
    "Viral Fever", "Chikungunya", "Flu", "Hepatitis A", "Tuberculosis",
    "Japanese Encephalitis", "Leptospirosis", "Measles", "Mumps", "Rubella",
    "Diphtheria", "Pertussis", "Meningitis", "Gastroenteritis", "Pneumonia"
]

SEVERITIES = ["mild", "moderate", "severe", "critical"]
SEVERITY_WEIGHTS = [0.35, 0.35, 0.2, 0.1]

HOSPITALS = [
    "City Hospital", "District Medical Center", "Apollo Hospital", "AIIMS",
    "Government Hospital", "Max Healthcare", "Fortis Hospital", "Medanta",
    "KIMS Hospital", "Care Hospital", "Manipal Hospital", "Narayana Health"
]

SYMPTOMS = {
    "Dengue": '["High fever", "Severe headache", "Pain behind eyes", "Joint pain", "Rash"]',
    "Malaria": '["Fever with chills", "Sweating", "Headache", "Nausea", "Body aches"]',
    "Typhoid": '["Prolonged fever", "Weakness", "Abdominal pain", "Headache", "Diarrhea"]',
    "COVID-19": '["Fever", "Cough", "Difficulty breathing", "Loss of taste/smell", "Fatigue"]',
    "Viral Fever": '["High fever", "Body aches", "Headache", "Fatigue", "Chills"]',
    "Flu": '["Fever", "Cough", "Sore throat", "Runny nose", "Body aches"]',
}


async def seed_data():
    """Main seeding function using raw SQL for reliability"""
    print("=" * 70)
    print("🚀 SymptoMap ORM Data Seeder")
    print("=" * 70)
    print(f"Database: {DATABASE_URL}")
    print(f"Time: {datetime.now().isoformat()}")
    print("-" * 70)
    print(f"Configuration:")
    print(f"   - Outbreaks: {TOTAL_OUTBREAKS}")
    print(f"   - Pending Approvals: {PENDING_APPROVALS}")
    print(f"   - Alerts: {TOTAL_ALERTS}")
    print("-" * 70)
    
    # Create engine
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get user for reported_by field
        result = await session.execute(text("SELECT id FROM users LIMIT 1"))
        user_row = result.fetchone()
        user_id = user_row[0] if user_row else str(uuid.uuid4())
        
        print(f"\n✅ Using user ID: {user_id[:8]}...")
        
        # Seed Outbreaks
        print(f"\n📊 Seeding {TOTAL_OUTBREAKS} outbreak records...")
        outbreak_count = 0
        
        for i in range(TOTAL_OUTBREAKS):
            city_data = random.choice(CITIES)
            disease = random.choice(DISEASES)
            severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
            
            if severity == "critical":
                patient_count = random.randint(100, 500)
            elif severity == "severe":
                patient_count = random.randint(50, 150)
            elif severity == "moderate":
                patient_count = random.randint(20, 80)
            else:
                patient_count = random.randint(5, 30)
            
            days_ago = random.randint(0, 730)
            date_started = datetime.now(timezone.utc) - timedelta(days=days_ago)
            date_reported = date_started + timedelta(hours=random.randint(1, 48))
            
            lat = city_data["lat"] + random.uniform(-0.2, 0.2)
            lng = city_data["lng"] + random.uniform(-0.2, 0.2)
            
            symptoms = SYMPTOMS.get(disease, '["Fever", "Fatigue", "Headache"]')
            
            outbreak_id = str(uuid.uuid4())
            hospital_id = str(uuid.uuid4())
            
            try:
                await session.execute(text("""
                    INSERT INTO outbreaks (
                        id, hospital_id, reported_by, disease_type, patient_count,
                        date_started, date_reported, severity, 
                        age_distribution, gender_distribution, symptoms, notes,
                        latitude, longitude, verified, created_at, updated_at
                    ) VALUES (
                        :id, :hospital_id, :reported_by, :disease_type, :patient_count,
                        :date_started, :date_reported, :severity,
                        :age_distribution, :gender_distribution, :symptoms, :notes,
                        :latitude, :longitude, :verified, :created_at, :updated_at
                    )
                """), {
                    "id": outbreak_id,
                    "hospital_id": hospital_id,
                    "reported_by": user_id,
                    "disease_type": disease,
                    "patient_count": patient_count,
                    "date_started": date_started.isoformat(),
                    "date_reported": date_reported.isoformat(),
                    "severity": severity,
                    "age_distribution": f'{{"0-18": {random.randint(10, 30)}, "19-45": {random.randint(30, 50)}, "46+": {random.randint(20, 40)}}}',
                    "gender_distribution": f'{{"male": {random.randint(40, 60)}, "female": {100 - random.randint(40, 60)}}}',
                    "symptoms": symptoms,
                    "notes": f"Outbreak of {disease} in {city_data['city']}. {patient_count} cases confirmed.",
                    "latitude": lat,
                    "longitude": lng,
                    "verified": 1 if random.random() > 0.2 else 0,
                    "created_at": date_reported.isoformat(),
                    "updated_at": date_reported.isoformat()
                })
                outbreak_count += 1
            except Exception as e:
                if "UNIQUE" not in str(e):
                    print(f"Error: {e}")
            
            if (i + 1) % 500 == 0:
                await session.commit()
                print(f"   📍 Progress: {i + 1}/{TOTAL_OUTBREAKS} ({(i+1)/TOTAL_OUTBREAKS*100:.1f}%)")
        
        await session.commit()
        print(f"   ✅ Inserted {outbreak_count} outbreaks")
        
        # Seed Pending Approvals
        print(f"\n📋 Seeding {PENDING_APPROVALS} pending approval requests...")
        approval_count = 0
        
        for i in range(PENDING_APPROVALS):
            city_data = random.choice(CITIES)
            disease = random.choice(DISEASES)
            severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
            
            days_ago = random.randint(0, 14)
            date_reported = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            lat = city_data["lat"] + random.uniform(-0.15, 0.15)
            lng = city_data["lng"] + random.uniform(-0.15, 0.15)
            
            patient_count = random.randint(5, 100)
            
            try:
                await session.execute(text("""
                    INSERT INTO doctor_outbreaks (
                        id, disease_type, patient_count, severity, latitude, longitude,
                        location_name, city, state, description, date_reported,
                        submitted_by, status, created_at
                    ) VALUES (
                        :id, :disease_type, :patient_count, :severity, :latitude, :longitude,
                        :location_name, :city, :state, :description, :date_reported,
                        :submitted_by, :status, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "disease_type": disease,
                    "patient_count": patient_count,
                    "severity": severity,
                    "latitude": lat,
                    "longitude": lng,
                    "location_name": f"{city_data['city']} {random.choice(HOSPITALS)}",
                    "city": city_data["city"],
                    "state": city_data["state"],
                    "description": f"Suspected {disease} outbreak. {patient_count} patients showing symptoms. Requesting verification.",
                    "date_reported": date_reported.isoformat(),
                    "submitted_by": f"dr_{random.choice(['kumar', 'sharma', 'singh', 'patel', 'gupta'])}",
                    "status": "pending",
                    "created_at": date_reported.isoformat()
                })
                approval_count += 1
            except Exception as e:
                if "UNIQUE" not in str(e):
                    print(f"Error: {e}")
            
            if (i + 1) % 50 == 0:
                print(f"   📝 Progress: {i + 1}/{PENDING_APPROVALS}")
        
        await session.commit()
        print(f"   ✅ Inserted {approval_count} pending approvals")
        
        # Seed Alerts
        print(f"\n🔔 Seeding {TOTAL_ALERTS} alerts...")
        alert_count = 0
        
        alert_templates = [
            ("🚨 High Priority: {} Outbreak", "critical", "outbreak"),
            ("⚠️ {} Cases Rising", "warning", "outbreak"),
            ("📢 {} Alert: New Cases Detected", "info", "surveillance"),
            ("🏥 Hospital Capacity Warning: {}", "warning", "capacity"),
            ("🔬 {} Cluster Identified", "critical", "cluster"),
            ("📊 Unusual {} Pattern Detected", "warning", "pattern"),
        ]
        
        for i in range(TOTAL_ALERTS):
            city_data = random.choice(CITIES)
            disease = random.choice(DISEASES)
            
            template = random.choice(alert_templates)
            title = template[0].format(disease)
            severity = template[1]
            alert_type = template[2]
            
            days_ago = random.randint(0, 30)
            created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            affected_count = random.randint(10, 500)
            
            message = f"Alert: {disease} outbreak detected in {city_data['city']}, {city_data['state']}. " \
                      f"Approximately {affected_count} cases reported."
            
            try:
                await session.execute(text("""
                    INSERT INTO alerts (
                        id, alert_type, severity, title, message, zone_name,
                        recipients, delivery_status, acknowledged_by,
                        sent_at, created_at
                    ) VALUES (
                        :id, :alert_type, :severity, :title, :message, :zone_name,
                        :recipients, :delivery_status, :acknowledged_by,
                        :sent_at, :created_at
                    )
                """), {
                    "id": str(uuid.uuid4()),
                    "alert_type": alert_type,
                    "severity": severity,
                    "title": title,
                    "message": message,
                    "zone_name": f"{city_data['city']}, {city_data['state']}",
                    "recipients": f'{{"emails": ["health@{city_data["city"].lower()}.gov.in"]}}',
                    "delivery_status": '{"email": "sent"}',
                    "acknowledged_by": "[]" if random.random() > 0.3 else f'[{{"user": "admin", "time": "{created_at.isoformat()}"}}]',
                    "sent_at": created_at.isoformat(),
                    "created_at": created_at.isoformat()
                })
                alert_count += 1
            except Exception as e:
                if "UNIQUE" not in str(e):
                    print(f"Error: {e}")
            
            if (i + 1) % 20 == 0:
                print(f"   🔔 Progress: {i + 1}/{TOTAL_ALERTS}")
        
        await session.commit()
        print(f"   ✅ Inserted {alert_count} alerts")
        
        # Verify data
        print("\n📊 Verifying seeded data...")
        
        result = await session.execute(text("SELECT COUNT(*) FROM outbreaks"))
        total_outbreaks = result.scalar()
        print(f"   📍 Total outbreaks: {total_outbreaks}")
        
        result = await session.execute(text("SELECT COUNT(*) FROM doctor_outbreaks WHERE status = 'pending'"))
        total_pending = result.scalar()
        print(f"   📋 Pending approvals: {total_pending}")
        
        result = await session.execute(text("SELECT COUNT(*) FROM alerts"))
        total_alerts = result.scalar()
        print(f"   🔔 Total alerts: {total_alerts}")
        
        # Disease distribution
        result = await session.execute(text("""
            SELECT disease_type, COUNT(*) as count 
            FROM outbreaks 
            GROUP BY disease_type 
            ORDER BY count DESC 
            LIMIT 5
        """))
        print("\n   Top 5 diseases:")
        for row in result.fetchall():
            print(f"      - {row[0]}: {row[1]} cases")
        
        print("\n" + "=" * 70)
        print("✨ DATA SEEDING COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   ✅ Outbreaks: {outbreak_count} records added")
        print(f"   ✅ Pending Approvals: {approval_count} records added")
        print(f"   ✅ Alerts: {alert_count} records added")
        print(f"\n🎯 Your AI prediction model now has {total_outbreaks}+ training records.")
        print(f"📋 The Approval Requests page shows {total_pending} pending submissions.")
        print(f"🔔 The Alerts page displays {total_alerts} alerts.")
        print("\n" + "=" * 70)


if __name__ == "__main__":
    asyncio.run(seed_data())
