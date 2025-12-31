"""
Direct SQLite database population - bypasses all API/ORM issues
"""
import sqlite3
from datetime import datetime, timedelta, timezone
import json
import uuid

DB_PATH = "symptomap.db"

# Sample outbreak data
OUTBREAKS = [
    {"hospital": "Lilavati Hospital Mumbai", "lat": 19.0760, "lng": 72.8777, "city": "Mumbai", "state": "Maharashtra", "disease": "Dengue", "patients": 145, "severity": "severe"},
    {"hospital": "KEM Hospital Mumbai", "lat": 19.0033, "lng": 72.8400, "city": "Mumbai", "state": "Maharashtra", "disease": "Malaria", "patients": 95, "severity": "severe"},
    {"hospital": "Ruby Hall Clinic Pune", "lat": 18.5204, "lng": 73.8567, "city": "Pune", "state": "Maharashtra", "disease": "Viral Fever", "patients": 52, "severity": "moderate"},
    {"hospital": "Jehangir Hospital Pune", "lat": 18.5275, "lng": 73.8570, "city": "Pune", "state": "Maharashtra", "disease": "Flu", "patients": 28, "severity": "mild"},
    {"hospital": "AIIMS Delhi", "lat": 28.5672, "lng": 77.2100, "city": "Delhi", "state": "Delhi", "disease": "Covid-19", "patients": 68, "severity": "moderate"},
]

print("\n🔧 DIRECT DATABASE POPULATION\n")
print(f"Database: {DB_PATH}\n")

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists, create if not
    cursor.execute("SELECT id FROM users LIMIT 1")
    user_row = cursor.fetchone()
    
    if not user_row:
        print("Creating test user...")
        user_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO users (id, email, full_name, password_hash, role)
            VALUES (?, 'test@symptomap.com', 'Test Admin', 'dummy_hash', 'admin')
        """, (user_id,))
        conn.commit()
    else:
        user_id = user_row[0]
    
    print(f"✅ Using user ID: {user_id}\n")
    
    severity_icons = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}
    added = 0
    
    for data in OUTBREAKS:
        try:
            # Generate IDs
            hospital_id = str(uuid.uuid4())
            outbreak_id = str(uuid.uuid4())
            
            # Create hospital
            cursor.execute("""
                INSERT INTO hospitals 
                (id, name, address, city, state, country, pincode, phone, email, 
                 total_beds, icu_beds, available_beds, hospital_type, registration_number,
                 location, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                hospital_id,
                data["hospital"],
                f"Address of {data['hospital']}",
                data["city"],
                data["state"],
                "India",
                "400001",
                "+91-9876543210",
                f"contact@hospital.com",
                500, 50, 150,
                "private",
                f"REG{hash(data['hospital']) % 100000}",
                f"POINT({data['lng']} {data['lat']})"
            ))
            
            # Create outbreak
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
                outbreak_id,
                hospital_id,
                user_id,
                data["disease"],
                data["patients"],
                date_started,
                date_reported,
                data["severity"],
                age_dist,
                gender_dist,
                symptoms,
                f"{data['severity'].upper()} outbreak at {data['hospital']}",
                f"POINT({data['lng']} {data['lat']})"
            ))
            
            icon = severity_icons[data["severity"]]
            print(f"{icon} {data['severity'].upper():8} | {data['hospital']:35} | {data['disease']:12} | {data['patients']:3} patients")
            added += 1
            
        except Exception as e:
            print(f"❌ ERROR | {data['hospital']:35} | {str(e)[:50]}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully added {added}/{len(OUTBREAKS)} outbreaks!")
    
    if added > 0:
        print("\n" + "="*80)
        print("🎉 DATABASE POPULATED SUCCESSFULLY!")
        print("="*80)
        print(f"\n📍 NEXT STEPS:")
        print(f"   1. Refresh http://localhost:5173/ in your browser")
        print(f"   2. Dashboard should now show {added} outbreaks")
        print(f"   3. Map should display colored markers:")
        print(f"      - 🔴 RED zones (severe outbreaks)")
        print(f"      - 🟡 YELLOW zones (moderate outbreaks)")
        print(f"      - 🟢 GREEN zones (mild outbreaks)")
        print(f"\n✨ Data is now visible on the dashboard!\n")
    
except Exception as e:
    print(f"\n❌ Database Error: {e}")
    import traceback
    traceback.print_exc()
