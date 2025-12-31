"""
Quick database population script
Adds test outbreaks directly to see the system working
"""

import sqlite3
from datetime import datetime, timedelta, timezone
import json

DB_PATH = "symptomap.db"

# Sample outbreak data (Mumbai, Pune, Delhi)
SAMPLE_DATA = [
    # Mumbai - RED ZONES
    {"hospital": "Lilavati Hospital Mumbai", "lat": 19.0760, "lng": 72.8777, "disease": "Dengue", "patients": 145, "severity": "severe"},
    {"hospital": "KEM Hospital Mumbai", "lat": 19.0033, "lng": 72.8400, "disease": "Malaria", "patients": 95, "severity": "severe"},
    
    # Pune - YELLOW/GREEN
    {"hospital": "Ruby Hall Pune", "lat": 18.5204, "lng": 73.8567, "disease": "Viral Fever", "patients": 52, "severity": "moderate"},
    {"hospital": "Jehangir Pune", "lat": 18.5275, "lng": 73.8570, "disease": "Flu", "patients": 28, "severity": "mild"},
    
    # Delhi - MIXED
    {"hospital": "AIIMS Delhi", "lat": 28.5672, "lng": 77.2100, "disease": "Covid-19", "patients": 68, "severity": "moderate"},
]

def create_test_data():
    """Add test data directly to database"""
    print("\n🔧 Populating Database with Test Data...\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create a test user if doesn't exist
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, email, full_name, hashed_password, role, is_verified)
            VALUES (1, 'admin@test.com', 'Admin User', 'hash', 'admin', 1)
        """)
        
        added = 0
        for idx, data in enumerate(SAMPLE_DATA, 1):
            # Create hospital
            cursor.execute("""
                INSERT OR IGNORE INTO hospitals 
                (name, address, city, state, country, pincode, phone, email, 
                 total_beds, icu_beds, available_beds, hospital_type, registration_number,
                 location)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                        GeomFromText(?, 4326))
            """, (
                data["hospital"],
                f"Address of {data['hospital']}",
                data["hospital"].split()[-1],  # City name
                "Maharashtra" if "Mumbai" in data["hospital"] or "Pune" in data["hospital"] else "Delhi",
                "India",
                "400001",
                "+91-1234567890",
                f"contact@hospital{idx}.in",
                500, 50, 150,
                "private",
                f"REG{10000+idx}",
                f"POINT({data['lng']} {data['lat']})"
            ))
            
            hospital_id = cursor.lastrowid
            
            # Create outbreak
            date_started = datetime.now(timezone.utc) - timedelta(days=3)
            cursor.execute("""
                INSERT INTO outbreaks
                (hospital_id, reported_by, disease_type, patient_count, date_started, date_reported,
                 severity, verified, age_distribution, gender_distribution, symptoms, notes,
                 location)
                VALUES (?, 1, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?,
                        GeomFromText(?, 4326))
            """, (
                hospital_id,
                data["disease"],
                data["patients"],
                date_started.isoformat(),
                datetime.now(timezone.utc).isoformat(),
                data["severity"],
                json.dumps({"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10}),
                json.dumps({"male": 52, "female": 48}),
                json.dumps(["Fever", "Fatigue", "Body Ache"]),
                f"{data['severity'].upper()} outbreak at {data['hospital']}",
                f"POINT({data['lng']} {data['lat']})"
            ))
            
            severity_icon = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}[data["severity"]]
            print(f"{severity_icon} {data['severity'].upper():8} | {data['hospital']:30} | {data['disease']:12} | {data['patients']:3} patients")
            added += 1
        
        conn.commit()
        print(f"\n✅ Successfully added {added} outbreaks!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        conn.close()
    
    print("\n" + "="*80)
    print("🎉 Database populated with test data!")
    print("="*80)
    print("\n📍 View the results:")
    print("   - Dashboard: http://localhost:5173/")
    print("   - Analytics: http://localhost:5173/analytics")
    print("   - Map: Should show colored zones over Mumbai, Pune, Delhi")
    print("\n")

if __name__ == "__main__":
    create_test_data()
