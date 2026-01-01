
import sqlite3
import random
from datetime import datetime, timedelta
import os

# Database path
DB_PATH = os.path.join('backend-python', 'symptomap.db')

def get_db():
    return sqlite3.connect(DB_PATH)

def generate_pending():
    conn = get_db()
    cursor = conn.cursor()
    
    # We do NOT clear existing approved data, we just ADD pending ones.
    print("🚀 Generating PENDING outbreak requests...")
    
    # Random cities/hospitals for pending requests
    pending_locs = [
        {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126, "h": "Gandhi Medical College"},
        {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577, "h": "MY Hospital"},
        {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376, "h": "AIIMS Patna"},
        {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096, "h": "RIMS"},
        {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366, "h": "Medical College Hospital"}
    ]
    
    diseases = ['Chickenpox', 'Typhoid', 'Measles', 'Unknown Viral', 'Dengue']
    
    for i in range(25): # Generate 25 pending requests
        loc = random.choice(pending_locs)
        # Random offset
        lat = loc['lat'] + random.uniform(-0.05, 0.05)
        lng = loc['lng'] + random.uniform(-0.05, 0.05)
        
        disease = random.choice(diseases)
        cases = random.randint(5, 50)
        severity = 'mild'
        if cases > 30: severity = 'moderate'
        
        # Insert with STATUS = 'pending'
        cursor.execute('''
            INSERT INTO doctor_outbreaks 
            (disease_type, patient_count, severity, latitude, longitude, location_name, city, state, description, date_reported, submitted_by, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            disease, cases, severity, lat, lng, 
            loc['h'], loc['city'], loc['state'], 
            f"Pending review: Suspected {disease} case cluster.", 
            (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(), 
            'dr_verification_test', 
            datetime.now().isoformat(), 
            'pending'
        ))

    conn.commit()
    conn.close()
    print(f"✅ Successfully added 25 PENDING requests.")
    print("👉 Go to /admin/approvals to review them.")

if __name__ == "__main__":
    generate_pending()
