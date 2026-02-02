"""
Seed pending approvals and manual alerts with correct schema
"""
import sqlite3
import random
from datetime import datetime, timedelta

# Connect to SQLite database
DB_PATH = "symptomap.db"

DISEASES = ["Viral Fever", "Dengue", "Malaria", "Covid-19", "Flu", "Typhoid", "Chikungunya"]
SEVERITIES = ["mild", "moderate", "severe"]

CITIES = [
    ("North Delhi", "Delhi", 28.7041, 77.1025),
    ("South Delhi", "Delhi", 28.5244, 77.2066),
    ("Central Delhi", "Delhi", 28.6139, 77.2090),
    ("Pune East", "Maharashtra", 18.5204, 73.8567),
    ("Pune West", "Maharashtra", 18.5018, 73.8069),
    ("Mumbai Central", "Maharashtra", 19.0760, 72.8777),
    ("Bangalore Central", "Karnataka", 12.9716, 77.5946),
    ("Chennai Central", "Tamil Nadu", 13.0827, 80.2707),
    ("Kolkata Central", "West Bengal", 22.5726, 88.3639),
    ("Hyderabad Central", "Telangana", 17.3850, 78.4867),
    ("Ahmedabad", "Gujarat", 23.0225, 72.5714),
    ("Jaipur", "Rajasthan", 26.9124, 75.7873),
    ("Lucknow", "Uttar Pradesh", 26.8467, 80.9462),
    ("Patna", "Bihar", 25.5941, 85.1376),
    ("Bhopal", "Madhya Pradesh", 23.2599, 77.4126),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create doctor_outbreaks table with correct schema
cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctor_outbreaks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease_type TEXT NOT NULL,
        patient_count INTEGER NOT NULL,
        severity TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        location_name TEXT,
        city TEXT,
        state TEXT,
        description TEXT,
        date_reported TEXT,
        submitted_by TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'pending'
    )
''')
conn.commit()

# Clear existing pending approvals
cursor.execute("DELETE FROM doctor_outbreaks WHERE status = 'pending'")
conn.commit()

# Add 200 pending approvals
print("Creating 200 pending approvals...")
now = datetime.now()

for i in range(200):
    city, state, lat, lng = random.choice(CITIES)
    location_name = f"{city} Medical Center"
    
    days_ago = random.randint(1, 14)
    date_reported = (now - timedelta(days=days_ago)).isoformat()
    created_at = date_reported
    
    cursor.execute('''
        INSERT INTO doctor_outbreaks 
        (disease_type, patient_count, severity, latitude, longitude, location_name, city, state, description, date_reported, submitted_by, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    ''', (
        random.choice(DISEASES),
        random.randint(10, 150),
        random.choice(SEVERITIES),
        lat,
        lng,
        location_name,
        city,
        state,
        f"Doctor submission #{i+1} from {city}, {state}. Symptoms: Fever, Cough, Fatigue.",
        date_reported,
        f"Dr. Submission {i+1}",
        created_at
    ))

conn.commit()
print("✅ Created 200 pending approvals")

# Count pending
cursor.execute("SELECT COUNT(*) FROM doctor_outbreaks WHERE status = 'pending'")
print(f"   Pending count: {cursor.fetchone()[0]}")

# Add 50 manual alerts to doctor_alerts table
print("\nCreating 50 manual alerts...")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctor_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_type TEXT,
        title TEXT,
        message TEXT,
        latitude REAL,
        longitude REAL,
        affected_area TEXT,
        expiry_date TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'active'
    )
''')
conn.commit()

# Clear existing alerts
cursor.execute("DELETE FROM doctor_alerts")
conn.commit()

ALERT_TYPES = ["outbreak", "warning", "critical", "health_advisory"]

for i in range(50):
    city, state, lat, lng = random.choice(CITIES)
    days_ago = random.randint(0, 7)
    created_at = (now - timedelta(days=days_ago)).isoformat()
    expiry_date = (now + timedelta(days=random.randint(3, 14))).isoformat()
    
    cursor.execute('''
        INSERT INTO doctor_alerts
        (alert_type, title, message, latitude, longitude, affected_area, expiry_date, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')
    ''', (
        random.choice(ALERT_TYPES),
        f"{random.choice(DISEASES)} Alert - {city}",
        f"Health alert for {city}, {state}. Please take necessary precautions and report symptoms immediately.",
        lat,
        lng,
        f"{city}, {state}",
        expiry_date,
        created_at
    ))

conn.commit()
print("✅ Created 50 manual alerts")

cursor.execute("SELECT COUNT(*) FROM doctor_alerts WHERE status = 'active'")
print(f"   Active alerts: {cursor.fetchone()[0]}")

conn.close()
print("\n✅ Seeding complete!")
