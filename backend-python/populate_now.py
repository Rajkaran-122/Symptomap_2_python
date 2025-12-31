"""
DIRECT Database Population Script
Adds outbreak data directly to the database synchronously
Run this and data will immediately appear in the app!
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from datetime import datetime, timedelta, timezone
import json

# Import settings to get DATABASE_URL
from app.core.config import settings

print("\n🔧 Populating Database Directly...\n")
print(f"Database: {settings.DATABASE_URL[:50]}...\n")

# Create synchronous engine
engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))

with engine.begin() as conn:
    # Step 1: Create admin user if doesn't exist
    conn.execute(text("""
        INSERT INTO users (email, full_name, hashed_password, role, is_verified)
        VALUES ('demo@symptomap.com', 'Demo Admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TcxMQJqo6Bsh/j4YSDi5yB/qU7IW', 'admin', true)
        ON CONFLICT (email) DO NOTHING
    """))
    
    # Get admin user ID
    result = conn.execute(text("SELECT id FROM users WHERE email = 'demo@symptomap.com'"))
    admin_id = result.fetchone()[0]
    print(f"✅ Admin user ID: {admin_id}\n")
    
    # Test data with real coordinates
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
        hospital_result = conn.execute(text("""
            INSERT INTO hospitals 
            (name, address, city, state, country, pincode, phone, email, 
             total_beds, icu_beds, available_beds, hospital_type, registration_number, location)
            VALUES 
            (:name, :address, :city, :state, 'India', '400001', '+91-9876543210', :email,
             500, 50, 150, 'private', :reg,
             ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
            RETURNING id
        """), {
            "name": name,
            "address": f"{name}, {city}",
            "city": city,
            "state": state,
            "email": f"contact@hospital{idx}.com",
            "reg": f"REG{10000+idx}",
            "lat": lat,
            "lng": lng
        })
        hospital_id = hospital_result.fetchone()[0]
        
        # Insert outbreak
        date_started = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        date_reported = datetime.now(timezone.utc).isoformat()
        
        conn.execute(text("""
            INSERT INTO outbreaks
            (hospital_id, reported_by, disease_type, patient_count, date_started, date_reported,
             severity, verified, age_distribution, gender_distribution, symptoms, notes, location)
            VALUES
            (:hospital_id, :admin_id, :disease, :patients, :date_started, :date_reported,
             :severity, true, :age_dist, :gender_dist, :symptoms, :notes,
             ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
        """), {
            "hospital_id": hospital_id,
            "admin_id": admin_id,
            "disease": disease,
            "patients": patients,
            "date_started": date_started,
            "date_reported": date_reported,
            "severity": severity,
            "age_dist": json.dumps({"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10}),
            "gender_dist": json.dumps({"male": 52, "female": 48}),
            "symptoms": json.dumps(["Fever", "Fatigue", "Body Ache"]),
            "notes": f"{severity.upper()} outbreak at {name}",
            "lat": lat,
            "lng": lng
        })
        
        icon = severity_icons[severity]
        print(f"{icon} {severity.upper():8} | {name:30} | {disease:12} | {patients:3} patients")

print(f"\n✅ Successfully added {len(outbreaks)} outbreaks!")
print("\n" + "="*80)
print("🎉 Database Populated Successfully!")
print("="*80)
print("\n📍 NOW DO THIS:")
print("   1. Open: http://localhost:5173/")
print("   2. Press Ctrl+F5 to hard refresh")
print("   3. You should see:")
print("      - Map with colored pins over Mumbai, Pune, Delhi")
print("      - Dashboard: 5 outbreaks")
print("      - Analytics: Real charts")
print("\n")
