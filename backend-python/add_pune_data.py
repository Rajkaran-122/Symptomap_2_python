"""
Add dummy outbreak data for Pune hospitals using direct SQL
Creates red, yellow, and green zones on the map
"""

import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import text

from app.core.database import AsyncSessionLocal


async def add_pune_data():
    """Add Pune hospital outbreak data using raw SQL"""
    print("\n🏥 Adding Pune Hospital Outbreak Data...\n")
    
    async with AsyncSessionLocal() as db:
        # Step 1: Create hospitals (if not exists)
        hospitals_sql = """
        INSERT INTO hospitals (name, address, location, city, state, country, pincode, phone, email, total_beds, icu_beds, available_beds, hospital_type, registration_number)
        VALUES 
            ('Ruby Hall Clinic', 'Grant Medical Foundation Ruby Hall Clinic, 40, Sassoon Road, Pune', ST_GeomFromText('POINT(73.8567 18.5204)', 4326), 'Pune', 'Maharashtra', 'India', '411001', '+91-9876543210', 'contact@rubyhallclinic.in', 750, 75, 250, 'private', 'REG12345'),
            ('Sahyadri Super Specialty Hospital', '30-C, Erandwane, Karve Road, Pune', ST_GeomFromText('POINT(73.9143 18.5679)', 4326), 'Pune', 'Maharashtra', 'India', '411004', '+91-9876543211', 'contact@sahyadri.in', 300, 30, 100, 'private', 'REG12346'),
            ('KEM Hospital Pune', '489, Rasta Peth, Sardar Moodliar Rd, Pune', ST_GeomFromText('POINT(73.8446 18.5314)', 4326), 'Pune', 'Maharashtra', 'India', '411011', '+91-9876543212', 'contact@kemhospital.in', 500, 50, 150, 'government', 'REG12347'),
            ('Jehangir Hospital', '32, Sassoon Road, Near Pune Railway Station, Pune', ST_GeomFromText('POINT(73.8570 18.5275)', 4326), 'Pune', 'Maharashtra', 'India', '411001', '+91-9876543213', 'contact@jehangir.in', 350, 35, 120, 'private', 'REG12348'),
            ('Aditya Birla Memorial Hospital', 'Pune-Satara Road, Chinchwad, Pune', ST_GeomFromText('POINT(73.8988 18.5362)', 4326), 'Pune', 'Maharashtra', 'India', '411033', '+91-9876543214', 'contact@adityabirla.in', 450, 45, 150, 'private', 'REG12349')
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id, name;
        """
        
        try:
            result = await db.execute(text(hospitals_sql))
            await db.commit()
            hospital_rows = result.fetchall()
            print(f"✅ Added/Updated {len(hospital_rows)} Pune hospitals\n")
        except Exception as e:
            print(f"Note: {e}")
            # If conflict resolution doesn't work, just fetch existing
            result = await db.execute(text("SELECT id, name FROM hospitals WHERE city = 'Pune' LIMIT 5"))
            hospital_rows = result.fetchall()
        
        if not hospital_rows:
            print("❌ No hospitals found. Creating manually...")
            return
        
        # Get first user ID (or create one)
        user_result = await db.execute(text("SELECT id FROM users LIMIT 1"))
        user_row = user_result.first()
        
        if not user_row:
            print("Creating a test user...")
            await db.execute(text("""
                INSERT INTO users (email, full_name, hashed_password, role, is_verified)
                VALUES ('test@symptomap.com', 'Test User', '$2b$12$test', 'admin', true)
            """))
            await db.commit()
            user_result = await db.execute(text("SELECT id FROM users LIMIT 1"))
            user_row = user_result.first()
        
        user_id = user_row[0]
        
        # Step 2: Add outbreaks with different severities
        outbreaks_data = [
            # RED ZONES (Severe)
            (hospital_rows[0][0], "Dengue", 125, "severe", 2),
            (hospital_rows[2][0], "Typhoid", 85, "severe", 5),
            
            # YELLOW ZONES (Moderate)  
            (hospital_rows[1][0], "Viral Fever", 45, "moderate", 3),
            (hospital_rows[3][0], "Flu", 38, "moderate", 7),
            
            # GREEN ZONES (Mild)
            (hospital_rows[4][0], "Common Cold", 18, "mild", 4),
        ]
        
        for hospital_id, disease, patients, severity, days_ago in outbreaks_data:
            date_started = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            outbreak_sql = text("""
                INSERT INTO outbreaks 
                (hospital_id, reported_by, disease_type, patient_count, date_started, date_reported, severity, verified, 
                 age_distribution, gender_distribution, symptoms, notes, location)
                SELECT 
                    :hospital_id,
                    :user_id,
                    :disease,
                    :patients,
                    :date_started,
                    NOW(),
                    :severity,
                    true,
                    '{"0-18": 25, "19-40": 40, "41-60": 25, "60+": 10}'::jsonb,
                    '{"male": 52, "female": 48}'::jsonb,
                    '["Fever", "Fatigue", "Headache"]'::jsonb,
                    :notes,
                    h.location
                FROM hospitals h
                WHERE h.id = :hospital_id
            """)
            
            await db.execute(outbreak_sql, {
                "hospital_id": hospital_id,
                "user_id": user_id,
                "disease": disease,
                "patients": patients,
                "date_started": date_started,
                "severity": severity,
                "notes": f"{severity.upper()} outbreak - {disease}"
            })
            
            severity_emoji = {
                "severe": "🔴",
                "moderate": "🟡",
                "mild": "🟢"
            }
            hospital_name = next(h[1] for h in hospital_rows if h[0] == hospital_id)
            print(f"{severity_emoji[severity]} {severity.upper():8} | {hospital_name:35} | {disease:15} | {patients:3} patients")
        
        await db.commit()
        print(f"\n✅ Added {len(outbreaks_data)} outbreak records to Pune hospitals")
        print("\n" + "="*80)
        print("🎉 Dummy data added successfully!")
        print("="*80)
        print("\n📍 View the map at http://localhost:5173/")
        print("   You should see:")
        print("   - 🔴 2 RED zones (severe outbreaks - Ruby Hall & KEM)")
        print("   - 🟡 2 YELLOW zones (moderate outbreaks - Sahyadri & Jehangir)")
        print("   - 🟢 1 GREEN zone (mild outbreak - Aditya Birla)")
        print("\n")


if __name__ == "__main__":
    asyncio.run(add_pune_data())
