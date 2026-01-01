import sqlite3
import uuid
import datetime
import os

# Database path
db_path = 'backend-python/symptomap.db'

def seed_data():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Create Dummy Hospitals
        hospitals = [
            {
                "id": str(uuid.uuid4()),
                "name": "AIIMS Delhi",
                "address": "Ansari Nagar, New Delhi",
                "latitude": 28.5672,
                "longitude": 77.2100,
                "city": "New Delhi",
                "state": "Delhi"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "KEM Hospital",
                "address": "Parel, Mumbai",
                "latitude": 18.9930,
                "longitude": 72.8247,
                "city": "Mumbai",
                "state": "Maharashtra"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Doan Hospital",
                "address": "Indiranagar, Bangalore",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "city": "Bangalore",
                "state": "Karnataka"
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Apollo Chennai",
                "address": "Greams Road, Chennai",
                "latitude": 13.0827,
                "longitude": 80.2707,
                "city": "Chennai",
                "state": "Tamil Nadu"
            }
        ]

        print("Inserting Hospitals...")
        for h in hospitals:
            # Check if exists (optional, but good for re-running)
            cursor.execute("SELECT id FROM hospitals WHERE name = ?", (h['name'],))
            existing = cursor.fetchone()
            if not existing:
                cursor.execute('''
                    INSERT INTO hospitals (id, name, address, latitude, longitude, city, state, total_beds, available_beds, hospital_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 500, 100, 'Public')
                ''', (h['id'], h['name'], h['address'], h['latitude'], h['longitude'], h['city'], h['state']))
            else:
                h['id'] = existing[0] # Use existing ID

        # 2. Create Outbreaks linked to Hospitals
        # Data logic:
        # Delhi: Severe (> 300 cases)
        # Mumbai: Moderate (50-300 cases)
        # Bangalore: Mild (< 50 cases)
        outbreaks = [
            {
                "hospital_id": hospitals[0]['id'], # Delhi
                "disease_type": "Dengue",
                "patient_count": 1200,
                "severity": "Critical",
                "latitude": 28.5672,
                "longitude": 77.2100
            },
            {
                "hospital_id": hospitals[1]['id'], # Mumbai
                "disease_type": "Malaria",
                "patient_count": 150, # Moderate (Yellow)
                "severity": "Moderate",
                "latitude": 18.9930,
                "longitude": 72.8247
            },
            {
                "hospital_id": hospitals[2]['id'], # Bangalore
                "disease_type": "Flu",
                "patient_count": 45, # Mild (Green)
                "severity": "Mild",
                "latitude": 12.9716,
                "longitude": 77.5946
            },
            {
                "hospital_id": hospitals[3]['id'], # Chennai
                "disease_type": "Cholera",
                "patient_count": 320, # Severe (Red)
                "severity": "High",
                "latitude": 13.0827,
                "longitude": 80.2707
            }
        ]

        print("Inserting Outbreaks...")
        for o in outbreaks:
            outbreak_id = str(uuid.uuid4())
            now = datetime.datetime.now()
            cursor.execute('''
                INSERT INTO outbreaks (
                    id, hospital_id, disease_type, patient_count, severity, 
                    date_started, date_reported, latitude, longitude, verified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                outbreak_id, o['hospital_id'], o['disease_type'], o['patient_count'], o['severity'],
                now, now, o['latitude'], o['longitude']
            ))

        conn.commit()
        print(f"✅ Successfully seeded {len(outbreaks)} official outbreaks!")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    seed_data()
