"""
Manually add outbreak data to the database
"""
import sqlite3
from datetime import datetime, timezone

# Connect to database
conn = sqlite3.connect('symptomap.db')
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctor_outbreaks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disease_type TEXT NOT NULL,
        patient_count INTEGER NOT NULL,
        severity TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        location_name TEXT,
        city TEXT,
        state TEXT,
        description TEXT,
        date_reported TEXT,
        submitted_by TEXT,
        created_at TEXT
    )
''')

# Sample outbreak data to insert
outbreaks = [
    {
        'disease_type': 'Dengue',
        'patient_count': 45,
        'severity': 'moderate',
        'latitude': 26.9124,
        'longitude': 75.7873,
        'location_name': 'SMS Hospital',
        'city': 'Jaipur',
        'state': 'Rajasthan',
        'description': 'Reported cases of dengue in surrounding areas',
        'date_reported': datetime.now(timezone.utc).isoformat(),
        'submitted_by': 'doctor',
        'created_at': datetime.now(timezone.utc).isoformat()
    },
    {
        'disease_type': 'Malaria',
        'patient_count': 23,
        'severity': 'moderate',
        'latitude': 28.7041,
        'longitude': 77.1025,
        'location_name': 'AIIMS Delhi',
        'city': 'Delhi',
        'state': 'Delhi',
        'description': 'Malaria cases detected in monsoon season',
        'date_reported': datetime.now(timezone.utc).isoformat(),
        'submitted_by': 'doctor',
        'created_at': datetime.now(timezone.utc).isoformat()
    },
    {
        'disease_type': 'COVID-19',
        'patient_count': 67,
        'severity': 'severe',
        'latitude': 19.0760,
        'longitude': 72.8777,
        'location_name': 'KEM Hospital',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'description': 'New COVID-19 variant detected, cases increasing',
        'date_reported': datetime.now(timezone.utc).isoformat(),
        'submitted_by': 'doctor',
        'created_at': datetime.now(timezone.utc).isoformat()
    },
    {
        'disease_type': 'Influenza',
        'patient_count': 34,
        'severity': 'mild',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'location_name': 'Bangalore Medical College',
        'city': 'Bangalore',
        'state': 'Karnataka',
        'description': 'Seasonal flu outbreak in schools',
        'date_reported': datetime.now(timezone.utc).isoformat(),
        'submitted_by': 'doctor',
        'created_at': datetime.now(timezone.utc).isoformat()
    },
    {
        'disease_type': 'Typhoid',
        'patient_count': 28,
        'severity': 'moderate',
        'latitude': 13.0827,
        'longitude': 80.2707,
        'location_name': 'Apollo Hospital',
        'city': 'Chennai',
        'state': 'Tamil Nadu',
        'description': 'Water-borne disease outbreak',
        'date_reported': datetime.now(timezone.utc).isoformat(),
        'submitted_by': 'doctor',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
]

# Insert outbreaks
for outbreak in outbreaks:
    cursor.execute('''
        INSERT INTO doctor_outbreaks 
        (disease_type, patient_count, severity, latitude, longitude,
         location_name, city, state, description, date_reported, submitted_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        outbreak['disease_type'],
        outbreak['patient_count'],
        outbreak['severity'],
        outbreak['latitude'],
        outbreak['longitude'],
        outbreak['location_name'],
        outbreak['city'],
        outbreak['state'],
        outbreak['description'],
        outbreak['date_reported'],
        outbreak['submitted_by'],
        outbreak['created_at']
    ))
    print(f"✓ Added {outbreak['disease_type']} outbreak in {outbreak['city']} ({outbreak['patient_count']} cases)")

conn.commit()

# Verify data was inserted
cursor.execute('SELECT COUNT(*) FROM doctor_outbreaks')
count = cursor.fetchone()[0]
print(f"\n✅ Total outbreaks in database: {count}")

# Show all outbreaks
cursor.execute('SELECT disease_type, city, patient_count, severity FROM doctor_outbreaks ORDER BY id DESC')
print("\n📊 Current Outbreaks:")
for row in cursor.fetchall():
    print(f"   - {row[0]} in {row[1]}: {row[2]} cases ({row[3]})")

conn.close()
print("\n✅ Database updated successfully!")
