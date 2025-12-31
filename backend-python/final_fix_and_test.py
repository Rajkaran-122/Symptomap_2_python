"""
Final fix: Add data with location and test if API can handle it
Using the exact same format as before but ensuring data is clean
"""
import sqlite3
from datetime import datetime, timedelta, timezone
import json
import uuid

DB_PATH = "symptomap.db"

print("\n🔧 FINAL DATABASE FIX\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear existing data
print("Clearing existing data...")
cursor.execute("DELETE FROM outbreaks")
cursor.execute("DELETE FROM hospitals") 
conn.commit()
print("✅ Cleared\n")

# Get user
cursor.execute("SELECT id FROM users LIMIT 1")
user_row = cursor.fetchone()
if not user_row:
    print("❌ No user found")
    exit(1)
user_id = user_row[0]
print(f"✅ Using user ID: {user_id}\n")

# Sample outbreak data
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
    hospital_id = str(uuid.uuid4())
    outbreak_id = str(uuid.uuid4())
    
    # Create POINT as text - this is what we had before
    location_wkt = f"POINT({data['lng']} {data['lat']})"
    
    # Insert hospital WITH location
    cursor.execute("""
        INSERT INTO hospitals 
        (id, name, address, city, state, country, pincode, phone, email,
         total_beds, icu_beds, available_beds, hospital_type, registration_number,
         location, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        hospital_id, data["name"], f"{data['name']}, {data['city']}, {data['state']}",
        data["city"], data["state"], "India", "400001", "+91-9876543210",
        f"contact@hospital.com", 500, 50, 150, "private",
        f"REG{hash(data['name']) % 100000}",
        location_wkt  # Add as text
    ))
    
    # Insert outbreak WITH location
    date_started = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    date_reported = datetime.now(timezone.utc).isoformat()
    
    age_dist = json.dumps({"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10})
    gender_dist = json.dumps({"male": 52, "female": 48})
    symptoms = json.dumps(["Fever", "Fatigue", "Body Ache"])
    
    cursor.execute("""
        INSERT INTO outbreaks
        (id, hospital_id, reported_by, disease_type, patient_count,
         date_started, date_reported, severity, verified,
         age_distribution, gender_distribution, symptoms, notes,
         location, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    """, (
        outbreak_id, hospital_id, user_id, data["disease"], data["patients"],
        date_started, date_reported, data["severity"],
        age_dist, gender_dist, symptoms,
        f"{data['severity'].upper()} outbreak at {data['name']}",
        location_wkt  # Add as text
    ))
    
    icon = severity_icons[data["severity"]]
    print(f"{icon} {data['severity'].upper():8} | {data['name']:35} | {data['disease']:12} | {data['patients']:3} patients")
    added += 1

conn.commit()
conn.close()

print(f"\n✅ Successfully added {added} outbreaks!")
print("\n" + "="*80)
print("🎉 DATABASE POPULATED!")
print("="*80)
print("\n⚠️  NOTE: Location data is stored as text POINT format")
print("   The API may still return 500 if it can't deserialize")
print("   Testing API now...\n")

# Test API
import requests
try:
    print("Testing GET /outbreaks/...")
    response = requests.get("http://localhost:8000/api/v1/outbreaks/", timeout=5)
    if response.status_code == 200:
        data_resp = response.json()
        print(f"✅ GET /outbreaks/ works! Returned {len(data_resp)} outbreaks")
        print(f"\n✨ SUCCESS! API can read the data!")
        print(f"📍 Dashboard should now show {len(data_resp)} outbreaks\n")
    else:
        print(f"❌ GET /outbreaks/ failed with status {response.status_code}")
        print(f"   The 500 error persists - geometry deserialization issue")
        print(f"   This means GeoAlchemy2 still can't read text-based location\n")
except Exception as e:
    print(f"❌ Error testing API: {e}\n")
