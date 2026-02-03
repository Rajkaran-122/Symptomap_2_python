#!/usr/bin/env python3
"""
Fresh Production Data Seeder for SymptoMap
Seeds 5000 outbreaks, 200 pending approvals, and 100 alerts
Handles existing data gracefully - appends new records
"""

import sqlite3
import random
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent / "symptomap.db"

print("=" * 70)
print("🚀 SymptoMap Fresh Data Seeder")
print("=" * 70)
print(f"Database: {DB_PATH}")
print(f"Time: {datetime.now().isoformat()}")
print("-" * 70)

# India cities with coordinates (50+ cities)
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
    "KIMS Hospital", "Care Hospital", "Manipal Hospital", "Narayana Health",
    "Columbia Asia", "Aster Hospital", "Yashoda Hospital", "Global Hospital"
]

SYMPTOMS_MAP = {
    "Dengue": ["High fever", "Severe headache", "Pain behind eyes", "Joint pain", "Rash"],
    "Malaria": ["Fever with chills", "Sweating", "Headache", "Nausea", "Body aches"],
    "Typhoid": ["Prolonged fever", "Weakness", "Abdominal pain", "Headache", "Diarrhea"],
    "Cholera": ["Severe watery diarrhea", "Dehydration", "Vomiting", "Leg cramps"],
    "COVID-19": ["Fever", "Cough", "Difficulty breathing", "Loss of taste/smell", "Fatigue"],
    "Viral Fever": ["High fever", "Body aches", "Headache", "Fatigue", "Chills"],
    "Chikungunya": ["High fever", "Severe joint pain", "Muscle pain", "Headache", "Rash"],
    "Flu": ["Fever", "Cough", "Sore throat", "Runny nose", "Body aches"],
}


def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables(conn):
    """Create tables if they don't exist"""
    cursor = conn.cursor()
    
    # Create outbreaks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outbreaks (
            id TEXT PRIMARY KEY,
            hospital_id TEXT,
            reported_by TEXT,
            disease_type TEXT NOT NULL,
            patient_count INTEGER DEFAULT 1,
            date_started TEXT,
            date_reported TEXT,
            severity TEXT DEFAULT 'moderate',
            age_distribution TEXT,
            gender_distribution TEXT,
            symptoms TEXT,
            notes TEXT,
            latitude REAL,
            longitude REAL,
            location TEXT,
            verified INTEGER DEFAULT 0,
            verified_by TEXT,
            verification_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create doctor_outbreaks table (for pending approvals)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctor_outbreaks (
            id TEXT PRIMARY KEY,
            disease_type TEXT NOT NULL,
            patient_count INTEGER DEFAULT 1,
            severity TEXT DEFAULT 'moderate',
            latitude REAL,
            longitude REAL,
            location_name TEXT,
            city TEXT,
            state TEXT,
            description TEXT,
            date_reported TEXT,
            submitted_by TEXT,
            status TEXT DEFAULT 'pending',
            reviewed_by TEXT,
            reviewed_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            prediction_id TEXT,
            alert_type TEXT NOT NULL,
            severity TEXT DEFAULT 'warning',
            title TEXT NOT NULL,
            message TEXT,
            zone_name TEXT,
            recipients TEXT,
            delivery_status TEXT,
            acknowledged_by TEXT,
            sent_at TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create hospitals table if needed
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT,
            city TEXT,
            state TEXT,
            country TEXT DEFAULT 'India',
            pincode TEXT,
            phone TEXT,
            email TEXT,
            total_beds INTEGER DEFAULT 100,
            icu_beds INTEGER DEFAULT 10,
            available_beds INTEGER DEFAULT 50,
            hospital_type TEXT DEFAULT 'government',
            registration_number TEXT,
            latitude REAL,
            longitude REAL,
            location TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    print("✅ Database tables verified/created")


def seed_outbreaks(conn, count=5000):
    """Seed outbreak records"""
    print(f"\n📊 Seeding {count} outbreak records...")
    
    cursor = conn.cursor()
    inserted = 0
    
    for i in range(count):
        city_data = random.choice(CITIES)
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        
        # Patient count based on severity
        if severity == "critical":
            patient_count = random.randint(100, 500)
        elif severity == "severe":
            patient_count = random.randint(50, 150)
        elif severity == "moderate":
            patient_count = random.randint(20, 80)
        else:
            patient_count = random.randint(5, 30)
        
        # Spread dates over 2 years
        days_ago = random.randint(0, 730)
        date_started = datetime.now() - timedelta(days=days_ago)
        date_reported = date_started + timedelta(hours=random.randint(1, 48))
        
        lat = city_data["lat"] + random.uniform(-0.2, 0.2)
        lng = city_data["lng"] + random.uniform(-0.2, 0.2)
        
        symptoms = SYMPTOMS_MAP.get(disease, ["Fever", "Fatigue", "Headache"])
        selected_symptoms = random.sample(symptoms, min(len(symptoms), random.randint(2, 4)))
        
        outbreak_id = str(uuid.uuid4())
        hospital_id = str(uuid.uuid4())
        
        try:
            cursor.execute("""
                INSERT INTO outbreaks (
                    id, hospital_id, reported_by, disease_type, patient_count,
                    date_started, date_reported, severity, age_distribution,
                    gender_distribution, symptoms, notes, latitude, longitude,
                    location, verified, verified_by, verification_date,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                outbreak_id,
                hospital_id,
                f"dr_{random.choice(['kumar', 'sharma', 'singh', 'patel', 'gupta'])}",
                disease,
                patient_count,
                date_started.isoformat(),
                date_reported.isoformat(),
                severity,
                json.dumps({"0-18": random.randint(10, 30), "19-45": random.randint(30, 50), "46+": random.randint(20, 40)}),
                json.dumps({"male": random.randint(40, 60), "female": 100 - random.randint(40, 60)}),
                json.dumps(selected_symptoms),
                f"Outbreak of {disease} in {city_data['city']}. {patient_count} cases.",
                lat,
                lng,
                f"POINT({lng} {lat})",
                1 if random.random() > 0.2 else 0,
                "admin" if random.random() > 0.2 else None,
                (date_reported + timedelta(hours=random.randint(1, 24))).isoformat() if random.random() > 0.2 else None,
                date_reported.isoformat(),
                date_reported.isoformat()
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass  # Skip duplicates
        
        if (i + 1) % 500 == 0:
            conn.commit()
            print(f"   📍 Progress: {i + 1}/{count} ({(i+1)/count*100:.1f}%)")
    
    conn.commit()
    print(f"   ✅ Inserted {inserted} outbreak records")
    return inserted


def seed_pending_approvals(conn, count=200):
    """Seed pending approval requests"""
    print(f"\n📋 Seeding {count} pending approval requests...")
    
    cursor = conn.cursor()
    inserted = 0
    
    for i in range(count):
        city_data = random.choice(CITIES)
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        
        days_ago = random.randint(0, 14)
        date_reported = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        lat = city_data["lat"] + random.uniform(-0.15, 0.15)
        lng = city_data["lng"] + random.uniform(-0.15, 0.15)
        
        patient_count = random.randint(5, 100)
        
        try:
            cursor.execute("""
                INSERT INTO doctor_outbreaks (
                    id, disease_type, patient_count, severity, latitude, longitude,
                    location_name, city, state, description, date_reported,
                    submitted_by, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                disease,
                patient_count,
                severity,
                lat,
                lng,
                f"{city_data['city']} {random.choice(HOSPITALS)}",
                city_data["city"],
                city_data["state"],
                f"Suspected {disease} outbreak. {patient_count} patients showing symptoms. Requesting verification.",
                date_reported.isoformat(),
                f"dr_{random.choice(['agarwal', 'joshi', 'mishra', 'pandey', 'tiwari', 'yadav'])}",
                "pending",
                date_reported.isoformat()
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass
        
        if (i + 1) % 50 == 0:
            print(f"   📝 Progress: {i + 1}/{count}")
    
    conn.commit()
    print(f"   ✅ Inserted {inserted} pending approvals")
    return inserted


def seed_alerts(conn, count=100):
    """Seed alerts"""
    print(f"\n🔔 Seeding {count} alerts...")
    
    cursor = conn.cursor()
    inserted = 0
    
    alert_templates = [
        ("🚨 High Priority: {} Outbreak", "critical", "outbreak"),
        ("⚠️ {} Cases Rising", "warning", "outbreak"),
        ("📢 {} Alert: New Cases Detected", "info", "surveillance"),
        ("🏥 Hospital Capacity Warning: {}", "warning", "capacity"),
        ("🔬 {} Cluster Identified", "critical", "cluster"),
        ("📊 Unusual {} Pattern Detected", "warning", "pattern"),
        ("🌡️ {} Season Advisory", "info", "seasonal"),
        ("⚡ Rapid {} Spread Detected", "critical", "spread"),
    ]
    
    for i in range(count):
        city_data = random.choice(CITIES)
        disease = random.choice(DISEASES)
        
        template = random.choice(alert_templates)
        title = template[0].format(disease)
        severity = template[1]
        alert_type = template[2]
        
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        affected_count = random.randint(10, 500)
        
        message = f"Alert: {disease} outbreak detected in {city_data['city']}, {city_data['state']}. " \
                  f"Approximately {affected_count} cases reported. " \
                  f"Healthcare facilities are advised to increase surveillance."
        
        try:
            cursor.execute("""
                INSERT INTO alerts (
                    id, alert_type, severity, title, message, zone_name,
                    recipients, delivery_status, acknowledged_by,
                    sent_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                alert_type,
                severity,
                title,
                message,
                f"{city_data['city']}, {city_data['state']}",
                json.dumps({"emails": [f"health@{city_data['city'].lower()}.gov.in"]}),
                json.dumps({"email": "sent"}),
                json.dumps([]) if random.random() > 0.3 else json.dumps([{"user": "admin", "time": created_at.isoformat()}]),
                created_at.isoformat(),
                created_at.isoformat()
            ))
            inserted += 1
        except sqlite3.IntegrityError:
            pass
        
        if (i + 1) % 20 == 0:
            print(f"   🔔 Progress: {i + 1}/{count}")
    
    conn.commit()
    print(f"   ✅ Inserted {inserted} alerts")
    return inserted


def verify_data(conn):
    """Verify seeded data"""
    print("\n📊 Verifying seeded data...")
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM outbreaks")
    outbreak_count = cursor.fetchone()[0]
    print(f"   📍 Total outbreaks: {outbreak_count}")
    
    cursor.execute("SELECT COUNT(*) FROM doctor_outbreaks WHERE status = 'pending'")
    pending_count = cursor.fetchone()[0]
    print(f"   📋 Pending approvals: {pending_count}")
    
    cursor.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cursor.fetchone()[0]
    print(f"   🔔 Total alerts: {alert_count}")
    
    # Disease distribution
    cursor.execute("""
        SELECT disease_type, COUNT(*) as count 
        FROM outbreaks 
        GROUP BY disease_type 
        ORDER BY count DESC 
        LIMIT 5
    """)
    print("\n   Top 5 diseases:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]} cases")
    
    # Severity distribution
    cursor.execute("""
        SELECT severity, COUNT(*) as count 
        FROM outbreaks 
        GROUP BY severity 
        ORDER BY count DESC
    """)
    print("\n   Severity distribution:")
    for row in cursor.fetchall():
        print(f"      - {row[0]}: {row[1]} cases")
    
    return outbreak_count, pending_count, alert_count


def main():
    conn = get_connection()
    
    try:
        # Ensure tables exist
        ensure_tables(conn)
        
        # Seed data
        outbreaks = seed_outbreaks(conn, count=5000)
        approvals = seed_pending_approvals(conn, count=200)
        alerts = seed_alerts(conn, count=100)
        
        # Verify
        verify_data(conn)
        
        print("\n" + "=" * 70)
        print("✨ DATA SEEDING COMPLETE!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   ✅ Outbreaks: {outbreaks} records")
        print(f"   ✅ Pending Approvals: {approvals} records")
        print(f"   ✅ Alerts: {alerts} records")
        print(f"\n🎯 Your AI prediction model now has 5000+ training records.")
        print(f"📋 The Approval Requests page shows {approvals} pending submissions.")
        print(f"🔔 The Alerts page displays {alerts} alerts.")
        print("\n" + "=" * 70)
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
