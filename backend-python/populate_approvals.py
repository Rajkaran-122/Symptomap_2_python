import sqlite3
import random
import uuid
from datetime import datetime, timedelta
import os
import sys

# Add current dir to path to find app module
sys.path.append(os.getcwd())

from app.core.config import get_sqlite_db_path

def populate_approvals():
    print("Generating 500 Pending Approvals...")
    
    db_path = get_sqlite_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure table exists (it should, but just in case)
    # The SQLAlchemy model defines it, assuming Alembic/app startup created it.
    # If not, this insert might fail if table missing. 
    # But user is running the app, so it should exist.
    
    diseases = ["Dengue", "Malaria", "Typhoid", "Influenza", "Cholera", "Viral Fever", "Hepatitis A", "COVID-19", "Chikungunya"]
    severities = ["mild", "moderate", "severe"]
    
    cities = [
        {"name": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
        {"name": "Delhi", "state": "Delhi", "lat": 28.7041, "lon": 77.1025},
        {"name": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
        {"name": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
        {"name": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
        {"name": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867},
        {"name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
        {"name": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
        {"name": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873},
        {"name": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462}
    ]
    
    hospitals = ["City General Hospital", "Apollo Clinic", "Fortis Hospital", "Community Health Center", "Max Super Speciality", "Sunrise Hospital", "Care Plus Clinic"]
    
    first_names = ["Raj", "Amit", "Priya", "Sneha", "Vikram", "Anjali", "Rohan", "Suresh", "Anita", "Deepak", "Sanjay", "Neha", "Rahul", "Pooja"]
    last_names = ["Sharma", "Verma", "Gupta", "Patel", "Singh", "Kumar", "Reddy", "Nair", "Iyer", "Khan", "Joshi", "Mehta", "Das"]

    new_records = []
    
    for _ in range(500):
        city_data = random.choice(cities)
        
        # Add some random variance to location
        lat = city_data["lat"] + random.uniform(-0.05, 0.05)
        lon = city_data["lon"] + random.uniform(-0.05, 0.05)
        
        hospital_name = f"{random.choice(hospitals)} - {city_data['name']}"
        doctor_name = f"Dr. {random.choice(first_names)} {random.choice(last_names)}"
        
        disease = random.choice(diseases)
        severity = random.choice(severities)
        patients = random.randint(1, 15)
        if severity == "severe":
            patients = random.randint(1, 5)
        elif severity == "mild":
            patients = random.randint(5, 30)
            
        date_reported = datetime.now() - timedelta(hours=random.randint(1, 72))
        
        # Insert tuple
        # id is auto-increment usually in sqlite if defined as Integer Primary Key, 
        # but SQLAlchemy model assumes it handles it. 
        # Let's see if we need to provide it. Usually sqlite handles NULL for PK.
        
        new_records.append((
            disease,
            patients,
            severity,
            lat,
            lon,
            hospital_name,
            city_data["name"],
            city_data["state"],
            f"Suspected {disease} outbreak reported at {hospital_name}.",
            date_reported.isoformat(),
            doctor_name,
            date_reported.isoformat(),
            'pending'
        ))

    print(f"Inserting {len(new_records)} records...")
    
    curr = cursor.execute("INSERT INTO doctor_outbreaks (disease_type, patient_count, severity, latitude, longitude, location_name, city, state, description, date_reported, submitted_by, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", list(new_records[0]))
    
    # Bulk insert
    cursor.executemany("INSERT INTO doctor_outbreaks (disease_type, patient_count, severity, latitude, longitude, location_name, city, state, description, date_reported, submitted_by, created_at, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", new_records)
    
    conn.commit()
    print("Done!")
    
    # Verify count
    cursor.execute("SELECT COUNT(*) FROM doctor_outbreaks WHERE status='pending'")
    count = cursor.fetchone()[0]
    print(f"Total Pending Approvals: {count}")
    
    conn.close()

if __name__ == "__main__":
    populate_approvals()
