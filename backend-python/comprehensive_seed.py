#!/usr/bin/env python3
"""
Comprehensive Production Data Seeder for SymptoMap
Adds 5000+ outbreaks, 200 approval requests, and 50+ alerts

This script connects directly to the database to bypass API rate limits
for bulk data insertion.
"""

import sqlite3
import random
import json
from datetime import datetime, timedelta
from pathlib import Path

# Database path - will be created in the same directory
DB_PATH = Path(__file__).parent / "symptomap.db"

# India cities with coordinates
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
    "Diphtheria", "Pertussis", "Tetanus", "Meningitis", "Gastroenteritis"
]

SEVERITIES = ["mild", "moderate", "severe", "critical"]
SEVERITY_WEIGHTS = [0.35, 0.35, 0.2, 0.1]

HOSPITALS = [
    "City Hospital", "District Medical Center", "Apollo Hospital", "AIIMS",
    "Government Hospital", "Max Healthcare", "Fortis Hospital", "Medanta",
    "KIMS Hospital", "Care Hospital", "Manipal Hospital", "Narayana Health",
    "Columbia Asia", "Aster Hospital", "Yashoda Hospital", "Global Hospital",
    "Ruby Hall Clinic", "Kokilaben Hospital", "Lilavati Hospital", "Breach Candy Hospital"
]

SYMPTOMS_MAP = {
    "Dengue": ["High fever", "Severe headache", "Pain behind eyes", "Joint pain", "Rash", "Bleeding gums"],
    "Malaria": ["Fever with chills", "Sweating", "Headache", "Nausea", "Vomiting", "Body aches"],
    "Typhoid": ["Prolonged fever", "Weakness", "Abdominal pain", "Headache", "Loss of appetite", "Diarrhea"],
    "Cholera": ["Severe watery diarrhea", "Dehydration", "Vomiting", "Leg cramps", "Rapid heart rate"],
    "COVID-19": ["Fever", "Cough", "Difficulty breathing", "Loss of taste/smell", "Fatigue", "Body aches"],
    "Viral Fever": ["High fever", "Body aches", "Headache", "Fatigue", "Chills", "Sore throat"],
    "Chikungunya": ["High fever", "Severe joint pain", "Muscle pain", "Headache", "Rash", "Fatigue"],
    "Flu": ["Fever", "Cough", "Sore throat", "Runny nose", "Body aches", "Fatigue"],
    "Hepatitis A": ["Fatigue", "Nausea", "Abdominal pain", "Loss of appetite", "Jaundice", "Dark urine"],
    "Tuberculosis": ["Persistent cough", "Coughing blood", "Night sweats", "Weight loss", "Fatigue", "Fever"],
}

def get_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def create_tables_if_needed(conn):
    """Ensure all required tables exist"""
    cursor = conn.cursor()
    
    # Check if outbreaks table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='outbreaks'")
    if not cursor.fetchone():
        print("Creating outbreaks table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outbreaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hospital_id INTEGER,
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
                verified INTEGER DEFAULT 0,
                verified_by TEXT,
                verification_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    # Check if doctor_outbreaks table exists (for pending approvals)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='doctor_outbreaks'")
    if not cursor.fetchone():
        print("Creating doctor_outbreaks table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctor_outbreaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    
    # Check if alerts table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
    if not cursor.fetchone():
        print("Creating alerts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT,
                severity TEXT DEFAULT 'warning',
                category TEXT DEFAULT 'outbreak',
                location TEXT,
                latitude REAL,
                longitude REAL,
                disease_type TEXT,
                affected_count INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,
                auto_generated INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT,
                acknowledged_by TEXT,
                acknowledged_at TEXT
            )
        """)
    
    conn.commit()

def seed_outbreaks(conn, count=5000):
    """Seed outbreak records for prediction model training"""
    print(f"\n📊 Seeding {count} outbreak records...")
    
    cursor = conn.cursor()
    outbreaks = []
    
    # Generate outbreaks spread over the last 2 years for training data
    for i in range(count):
        city_data = random.choice(CITIES)
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        
        # Spread dates over 2 years for better training data
        days_ago = random.randint(0, 730)
        date_started = datetime.now() - timedelta(days=days_ago)
        date_reported = date_started + timedelta(hours=random.randint(1, 48))
        
        # Add some randomness to coordinates
        lat = city_data["lat"] + random.uniform(-0.2, 0.2)
        lng = city_data["lng"] + random.uniform(-0.2, 0.2)
        
        # Get symptoms for this disease
        symptoms = SYMPTOMS_MAP.get(disease, ["Fever", "Fatigue", "Headache"])
        selected_symptoms = random.sample(symptoms, min(len(symptoms), random.randint(2, 4)))
        
        # Patient count based on severity
        if severity == "critical":
            patient_count = random.randint(100, 500)
        elif severity == "severe":
            patient_count = random.randint(50, 150)
        elif severity == "moderate":
            patient_count = random.randint(20, 80)
        else:
            patient_count = random.randint(5, 30)
        
        outbreak = (
            random.randint(1, 100),  # hospital_id
            f"dr_{random.choice(['kumar', 'sharma', 'singh', 'patel', 'gupta', 'verma'])}",
            disease,
            patient_count,
            date_started.isoformat(),
            date_reported.isoformat(),
            severity,
            json.dumps({"0-18": random.randint(10, 30), "19-45": random.randint(30, 50), "46+": random.randint(20, 40)}),
            json.dumps({"male": random.randint(40, 60), "female": 100 - random.randint(40, 60)}),
            json.dumps(selected_symptoms),
            f"Outbreak of {disease} reported in {city_data['city']}. {patient_count} cases confirmed.",
            lat,
            lng,
            1 if random.random() > 0.2 else 0,  # 80% verified
            "admin" if random.random() > 0.2 else None,
            (date_reported + timedelta(hours=random.randint(1, 24))).isoformat() if random.random() > 0.2 else None,
            date_reported.isoformat(),
            date_reported.isoformat()
        )
        outbreaks.append(outbreak)
        
        if (i + 1) % 500 == 0:
            print(f"   Generated {i + 1}/{count} outbreak records...")
    
    # Batch insert
    cursor.executemany("""
        INSERT INTO outbreaks (
            hospital_id, reported_by, disease_type, patient_count,
            date_started, date_reported, severity, age_distribution,
            gender_distribution, symptoms, notes, latitude, longitude,
            verified, verified_by, verification_date, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, outbreaks)
    
    conn.commit()
    print(f"   ✅ Inserted {count} outbreak records")

def seed_pending_approvals(conn, count=200):
    """Seed pending doctor submissions for approval"""
    print(f"\n📋 Seeding {count} pending approval requests...")
    
    cursor = conn.cursor()
    submissions = []
    
    for i in range(count):
        city_data = random.choice(CITIES)
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=SEVERITY_WEIGHTS)[0]
        
        # Recent submissions (last 14 days)
        days_ago = random.randint(0, 14)
        date_reported = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        lat = city_data["lat"] + random.uniform(-0.15, 0.15)
        lng = city_data["lng"] + random.uniform(-0.15, 0.15)
        
        patient_count = random.randint(5, 100)
        
        submission = (
            disease,
            patient_count,
            severity,
            lat,
            lng,
            random.choice(HOSPITALS),
            city_data["city"],
            city_data["state"],
            f"Suspected {disease} outbreak. {patient_count} patients showing symptoms including fever and fatigue. Requesting verification and resources.",
            date_reported.isoformat(),
            f"dr_{random.choice(['agarwal', 'joshi', 'mishra', 'pandey', 'tiwari', 'yadav', 'chauhan', 'dubey'])}",
            "pending",
            date_reported.isoformat()
        )
        submissions.append(submission)
    
    cursor.executemany("""
        INSERT INTO doctor_outbreaks (
            disease_type, patient_count, severity, latitude, longitude,
            location_name, city, state, description, date_reported,
            submitted_by, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, submissions)
    
    conn.commit()
    print(f"   ✅ Inserted {count} pending approval requests")

def seed_alerts(conn, count=50):
    """Seed alerts for Alert Management"""
    print(f"\n🔔 Seeding {count} alerts...")
    
    cursor = conn.cursor()
    alerts = []
    
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
        category = template[2]
        
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        expires_at = created_at + timedelta(days=random.randint(7, 30))
        
        affected_count = random.randint(10, 500)
        
        message = f"Alert: {disease} outbreak detected in {city_data['city']}, {city_data['state']}. " \
                  f"Approximately {affected_count} cases reported. " \
                  f"Healthcare facilities are advised to increase surveillance and stock essential supplies."
        
        alert = (
            title,
            message,
            severity,
            category,
            f"{city_data['city']}, {city_data['state']}",
            city_data["lat"] + random.uniform(-0.1, 0.1),
            city_data["lng"] + random.uniform(-0.1, 0.1),
            disease,
            affected_count,
            1 if random.random() > 0.1 else 0,  # 90% active
            1 if random.random() > 0.5 else 0,  # 50% auto-generated
            created_at.isoformat(),
            expires_at.isoformat()
        )
        alerts.append(alert)
    
    cursor.executemany("""
        INSERT INTO alerts (
            title, message, severity, category, location,
            latitude, longitude, disease_type, affected_count,
            is_active, auto_generated, created_at, expires_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, alerts)
    
    conn.commit()
    print(f"   ✅ Inserted {count} alerts")

def verify_data(conn):
    """Verify the seeded data"""
    print("\n📊 Verifying seeded data...")
    
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM outbreaks")
    outbreak_count = cursor.fetchone()[0]
    print(f"   📍 Total outbreaks: {outbreak_count}")
    
    cursor.execute("SELECT COUNT(*) FROM doctor_outbreaks WHERE status = 'pending'")
    pending_count = cursor.fetchone()[0]
    print(f"   📋 Pending approvals: {pending_count}")
    
    cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_active = 1")
    alert_count = cursor.fetchone()[0]
    print(f"   🔔 Active alerts: {alert_count}")
    
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

def main():
    print("=" * 60)
    print("SymptoMap Comprehensive Data Seeder")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Time: {datetime.now().isoformat()}")
    
    conn = get_connection()
    
    try:
        # Ensure tables exist
        create_tables_if_needed(conn)
        
        # Seed data
        seed_outbreaks(conn, count=5000)
        seed_pending_approvals(conn, count=200)
        seed_alerts(conn, count=50)
        
        # Verify
        verify_data(conn)
        
        print("\n" + "=" * 60)
        print("✨ Data seeding complete!")
        print("=" * 60)
        print("\nYour prediction model now has 5000+ training records.")
        print("The Approval Requests page shows 200 pending submissions.")
        print("The Alerts page displays 50 alerts.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
