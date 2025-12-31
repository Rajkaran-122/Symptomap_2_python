"""
Pure SQL Database Population - No ORM
Directly populates PostgreSQL database with outbreak data
"""

import psycopg2
from psycopg2.extras import Json
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

# Parse DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL', '')
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

# Remove postgresql+asyncpg:// prefix if present
DATABASE_URL = DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://')

print("\n🔧 Connecting to Database...\n")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Step 1: Create admin user
    cursor.execute("""
        INSERT INTO users (email, full_name, hashed_password, role, is_verified)
        VALUES ('demo@symptomap.com', 'Demo Admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TcxMQJqo6Bsh/j4YSDi5yB/qU7IW', 'admin', true)
        ON CONFLICT (email) DO NOTHING
        RETURNING id
    """)
    
    result = cursor.fetchone()
    if result:
        admin_id = result[0]
    else:
        cursor.execute("SELECT id FROM users WHERE email = 'demo@symptomap.com'")
        admin_id = cursor.fetchone()[0]
    
    print(f"✅ Admin user ID: {admin_id}\n")
    
    # Test data
    outbreaks = [
        ("Lilavati Hospital Mumbai", 19.0760, 72.8777, "Mumbai", "Maharashtra", "Dengue", 145, "severe"),
        ("KEM Hospital Mumbai", 19.0033, 72.8400, "Mumbai", "Maharashtra", "Malaria", 95, "severe"),
        ("Ruby Hall Clinic Pune", 18.5204, 73.8567, "Pune", "Maharashtra", "Viral Fever", 52, "moderate"),
        ("Jehangir Hospital Pune", 18.5275, 73.8570, "Pune", "Maharashtra", "Flu", 28, "mild"),
        ("AIIMS Delhi", 28.5672, 77.2100, "Delhi", "Delhi", "Covid-19", 68, "moderate"),
    ]
    
    severity_icons = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}
    
    for idx, (name, lat, lng, city, state, disease, patients, severity) in enumerate(outbreaks, 1):
        # Insert hospital
        cursor.execute("""
            INSERT INTO hospitals 
            (name, address, city, state, country, pincode, phone, email, 
             total_beds, icu_beds, available_beds, hospital_type, registration_number, location)
            VALUES 
            (%s, %s, %s, %s, 'India', '400001', '+91-9876543210', %s,
             500, 50, 150, 'private', %s,
             ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            RETURNING id
        """, (name, f"{name}, {city}", city, state, f"contact@hospital{idx}.com", f"REG{10000+idx}", lng, lat))
        
        hospital_id = cursor.fetchone()[0]
        
        # Insert outbreak
        date_started = datetime.now(timezone.utc) - timedelta(days=3)
        date_reported = datetime.now(timezone.utc)
        
        age_dist = Json({"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10})
        gender_dist = Json({"male": 52, "female": 48})
        symptoms = Json(["Fever", "Fatigue", "Body Ache"])
        
        cursor.execute("""
            INSERT INTO outbreaks
            (hospital_id, reported_by, disease_type, patient_count, date_started, date_reported,
             severity, verified, age_distribution, gender_distribution, symptoms, notes, location)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, true, %s, %s, %s, %s,
             ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        """, (hospital_id, admin_id, disease, patients, date_started, date_reported,
              severity, age_dist, gender_dist, symptoms, f"{severity.upper()} outbreak at {name}",
              lng, lat))
        
        icon = severity_icons[severity]
        print(f"{icon} {severity.upper():8} | {name:30} | {disease:12} | {patients:3} patients")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Successfully added {len(outbreaks)} outbreaks!")
    print("\n" + "="*80)
    print("🎉 DATABASE POPULATED!")
    print("="*80)
    print("\n📍 NEXT STEPS:")
    print("   1. Open: http://localhost:5173/")
    print("   2. Press Ctrl+Shift+R (hard refresh)")
    print("   3. You should now see:")
    print("      ✅ Dashboard: 5 outbreaks (not 0)")
    print("      ✅ Map: Colored pins over Mumbai, Pune, Delhi")
    print("      ✅ Analytics: Real charts with data")
    print("\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'conn' in locals():
        conn.rollback()
