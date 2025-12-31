"""
Populate database with multiple hospitals per zone across India
"""
import sqlite3
from datetime import datetime, timedelta, timezone
import json
import uuid

DB_PATH = "symptomap.db"

print("\n🔧 POPULATING DATABASE WITH ZONE-BASED OUTBREAKS\n")

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

# Zone-based outbreak data - Multiple hospitals per zone
zones = [
    # RED ZONE - Delhi (Severe)
    {
        "zone": "Delhi - Severe Zone",
        "severity": "severe",
        "disease": "Dengue",
        "hospitals": [
            {"name": "AIIMS Delhi", "lat": 28.5672, "lng": 77.2100, "patients": 145},
            {"name": "Safdarjung Hospital", "lat": 28.5677, "lng": 77.2065, "patients": 128},
            {"name": "Ram Manohar Lohia Hospital", "lat": 28.6289, "lng": 77.2065, "patients": 98},
            {"name": "GB Pant Hospital", "lat": 28.6526, "lng": 77.2452, "patients": 112},
            {"name": "GTB Hospital Delhi", "lat": 28.6872, "lng": 77.3075, "patients": 87},
        ],
        "city": "Delhi",
        "state": "Delhi"
    },
    # YELLOW ZONE - Pune (Moderate)
    {
        "zone": "Pune - Moderate Zone",
        "severity": "moderate",
        "disease": "Viral Fever",
        "hospitals": [
            {"name": "Ruby Hall Clinic", "lat": 18.5204, "lng": 73.8567, "patients": 65},
            {"name": "Jehangir Hospital", "lat": 18.5275, "lng": 73.8570, "patients": 58},
            {"name": "Deenanath Mangeshkar Hospital", "lat": 18.4671, "lng": 73.8077, "patients": 72},
            {"name": "Columbia Asia Hospital Pune", "lat": 18.5642, "lng": 73.7770, "patients": 51},
        ],
        "city": "Pune",
        "state": "Maharashtra"
    },
    # GREEN ZONE - Uttarakhand (Mild)
    {
        "zone": "Uttarakhand - Mild Zone",
        "severity": "mild",
        "disease": "Flu",
        "hospitals": [
            {"name": "Doon Hospital Dehradun", "lat": 30.3165, "lng": 78.0322, "patients": 28},
            {"name": "Max Hospital Dehradun", "lat": 30.3255, "lng": 78.0436, "patients": 35},
            {"name": "Shri Mahant Indiresh Hospital", "lat": 30.3398, "lng": 78.0657, "patients": 22},
        ],
        "city": "Dehradun",
        "state": "Uttarakhand"
    },
    # YELLOW ZONE - Bangalore (Moderate)
    {
        "zone": "Bangalore - Moderate Zone",
        "severity": "moderate",
        "disease": "COVID-19",
        "hospitals": [
            {"name": "NIMHANS Bangalore", "lat": 12.9443, "lng": 77.5980, "patients": 68},
            {"name": "Manipal Hospital", "lat": 12.9698, "lng": 77.7500, "patients": 55},
            {"name": "Apollo Hospitals Bangalore", "lat": 12.9539, "lng": 77.6377, "patients": 62},
            {"name": "Fortis Hospital Bangalore", "lat": 13.0209, "lng": 77.6409, "patients": 48},
        ],
        "city": "Bangalore",
        "state": "Karnataka"
    },
]

severity_icons = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}
total_added = 0

for zone in zones:
    print(f"\n{severity_icons[zone['severity']]} {zone['zone']}")
    print(f"   Disease: {zone['disease']}")
    print(f"   Hospitals:")
    
    for hosp in zone["hospitals"]:
        location_placeholder = ""
        
        hospital_id = str(uuid.uuid4())
        outbreak_id = str(uuid.uuid4())
        
        # Insert hospital
        cursor.execute("""
            INSERT INTO hospitals 
            (id, name, address, city, state, country, pincode, phone, email,
             total_beds, icu_beds, available_beds, hospital_type, registration_number,
             latitude, longitude, location, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            hospital_id, hosp["name"], f"{hosp['name']}, {zone['city']}, {zone['state']}",
            zone["city"], zone["state"], "India", "110001", "+91-9876543210",
            f"contact@hospital.com", 500, 50, 150, "government",
            f"REG{hash(hosp['name']) % 100000}",
            hosp["lat"], hosp["lng"],
            location_placeholder
        ))
        
        # Insert outbreak
        date_started = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        date_reported = datetime.now(timezone.utc).isoformat()
        
        age_dist = json.dumps({"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10})
        gender_dist = json.dumps({"male": 52, "female": 48})
        symptoms = json.dumps(["Fever", "Fatigue", "Body Ache"])
        
        cursor.execute("""
            INSERT INTO outbreaks
            (id, hospital_id, reported_by, disease_type, patient_count,
             date_started, date_reported, severity, verified,
             age_distribution, gender_distribution, symptoms, notes,
             latitude, longitude, location, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            outbreak_id, hospital_id, user_id, zone["disease"], hosp["patients"],
            date_started, date_reported, zone["severity"],
            age_dist, gender_dist, symptoms,
            f"{zone['severity'].upper()} outbreak - {zone['zone']}",
            hosp["lat"], hosp["lng"],
            location_placeholder
        ))
        
        print(f"      ✓ {hosp['name']:40} | {hosp['patients']:3} patients | ({hosp['lat']:.4f}, {hosp['lng']:.4f})")
        total_added += 1

conn.commit()
conn.close()

print(f"\n✅ Successfully added {total_added} hospital outbreaks across {len(zones)} zones!")
print("\n" + "="*80)
print("🎉 ZONE-BASED DATA POPULATED!")
print("="*80)
print(f"\n📊 Summary:")
print(f"   Total Zones: {len(zones)}")
print(f"   Total Hospitals: {total_added}")
print(f"   🔴 Severe Zones: 1 (Delhi)")
print(f"   🟡 Moderate Zones: 2 (Pune, Bangalore)")
print(f"   🟢 Mild Zones: 1 (Uttarakhand)")
print(f"\n📍 View at: http://localhost:3000/\n")
