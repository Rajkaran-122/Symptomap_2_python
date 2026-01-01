
import sqlite3
import os
import random
from datetime import datetime

# Database path
db_path = 'backend-python/symptomap.db'

def seed_data():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Test data - Diverse locations in India with different severities
    outbreaks = [
        {
            "disease_type": "Dengue",
            "patient_count": 550,
            "severity": "Critical",
            "location_name": "Connaught Place",
            "city": "New Delhi",
            "state": "Delhi",
            "latitude": 28.6304,
            "longitude": 77.2177,
            "description": "Massive outbreak in central Delhi.",
            "status": "approved"
        },
        {
            "disease_type": "Malaria",
            "patient_count": 80,
            "severity": "Moderate",
            "location_name": "Andheri East",
            "city": "Mumbai",
            "state": "Maharashtra",
            "latitude": 19.1136,
            "longitude": 72.8697,
            "description": "Moderate spread near metro station.",
            "status": "approved"
        },
        {
            "disease_type": "Viral Fever",
            "patient_count": 15,
            "severity": "Low",
            "location_name": "Koramangala",
            "city": "Bengaluru",
            "state": "Karnataka",
            "latitude": 12.9260,
            "longitude": 77.6229,
            "description": "Seasonal viral fever cases reported.",
            "status": "approved"
        },
         {
            "disease_type": "Cholera",
            "patient_count": 250,
            "severity": "High",
            "location_name": "T Nagar",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "latitude": 13.0418,
            "longitude": 80.2341,
            "description": "Contaminated water source suspicion.",
            "status": "approved"
        },
        {
            "disease_type": "Typhoid",
            "patient_count": 45,
            "severity": "Moderate",
            "location_name": "Park Street",
            "city": "Kolkata",
            "state": "West Bengal",
            "latitude": 22.555,
            "longitude": 88.351,
            "description": "Cluster of cases from food stalls.",
            "status": "approved"
        }
    ]

    print("Seeding approved outbreaks...")
    try:
        for data in outbreaks:
            # We insert only columns we are sure exist based on the READ query
            cursor.execute('''
                INSERT INTO doctor_outbreaks (
                    disease_type, patient_count, severity, 
                    latitude, longitude, location_name, city, state,
                    description, status, date_reported
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['disease_type'], data['patient_count'], data['severity'],
                data['latitude'], data['longitude'], data['location_name'], data['city'], data['state'],
                data['description'], data['status'], datetime.now().strftime("%Y-%m-%d")
            ))
        
        conn.commit()
        print(f"Successfully added {len(outbreaks)} approved outbreaks.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        
    conn.close()

if __name__ == "__main__":
    seed_data()
