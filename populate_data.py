
import sqlite3
import random
import time
from datetime import datetime
import os

# Database path
DB_PATH = os.path.join('backend-python', 'symptomap.db')

def get_db():
    return sqlite3.connect(DB_PATH)

def generate_data():
    conn = get_db()
    cursor = conn.cursor()
    
    print("🧹 Cleaning up old demo data...")
    # Clear "demo" data
    cursor.execute("DELETE FROM doctor_outbreaks WHERE submitted_by LIKE 'demo%' OR submitted_by = 'doctor_demo'")

    print("🚀 Generating MULTI-HOSPITAL regional outbreaks...")
    
    # We define cities, and for each city, we add MULTIPLE hospitals
    cities = [
        # Maharashtra
        {
            "name": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777, 
            "hospitals": [
                {"name": "Lilavati Hospital", "cases": 120, "disease": "Malaria", "severity": "severe"},
                {"name": "Nanavati Hospital", "cases": 90, "disease": "Dengue", "severity": "moderate"},
                {"name": "KEM Hospital", "cases": 210, "disease": "Malaria", "severity": "severe"}
            ]
        },
        {
            "name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567,
            "hospitals": [
                {"name": "Ruby Hall Clinic", "cases": 45, "disease": "Flu", "severity": "moderate"},
                {"name": "Jehangir Hospital", "cases": 30, "disease": "Flu", "severity": "mild"}
            ]
        },
        
        # Delhi
        {
            "name": "New Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090,
            "hospitals": [
                {"name": "AIIMS", "cases": 400, "disease": "Dengue", "severity": "severe"},
                {"name": "Safdarjung Hospital", "cases": 250, "disease": "Dengue", "severity": "severe"},
                {"name": "Max Super Speciality", "cases": 100, "disease": "Chikungunya", "severity": "moderate"}
            ]
        },

        # Karnataka
        {
            "name": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946,
            "hospitals": [
                {"name": "Narayana Health", "cases": 150, "disease": "H1N1", "severity": "moderate"},
                {"name": "Fortis Hospital", "cases": 80, "disease": "Viral Fever", "severity": "moderate"}
            ]
        },
        
        # Rajasthan
        {
            "name": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873,
            "hospitals": [
                {"name": "SMS Hospital", "cases": 180, "disease": "Malaria", "severity": "severe"}
            ]
        },
         {
            "name": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125,
            "hospitals": [
                {"name": "Civil Hospital", "cases": 40, "disease": "Unknown", "severity": "mild"}
            ]
        },

        # Tamil Nadu
        {
            "name": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707,
            "hospitals": [
                {"name": "Apollo Hospital", "cases": 300, "disease": "Dengue", "severity": "severe"},
                {"name": "Stanley Medical", "cases": 150, "disease": "Dengue", "severity": "severe"}
            ]
        }
    ]
    
    count = 0
    for city in cities:
        # Vary coords slightly for realism if we weren't aggregating, 
        # but for aggregation test, same city coords is fine (or close to it)
        
        for hosp in city['hospitals']:
            # Small random offset so they aren't EXACTLY on top of each other if logic fails,
            # but close enough to belong to the city.
            lat = city['lat'] + random.uniform(-0.01, 0.01)
            lng = city['lng'] + random.uniform(-0.01, 0.01)
            
            cursor.execute('''
                INSERT INTO doctor_outbreaks 
                (disease_type, patient_count, severity, latitude, longitude, location_name, city, state, description, date_reported, submitted_by, created_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                hosp['disease'], hosp['cases'], hosp['severity'], lat, lng, 
                hosp['name'], city['name'], city['state'], 
                f"Report from {hosp['name']}", 
                datetime.now().isoformat(), 'demo_multi_hospital', datetime.now().isoformat(), 'approved'
            ))
            count += 1

    conn.commit()
    conn.close()
    print(f"✅ Successfully created {count} hospital records across {len(cities)} cities.")
    print("👉 Now update OutbreakMap.tsx to aggregate these into SINGLE zone circles per city!")

if __name__ == "__main__":
    generate_data()
