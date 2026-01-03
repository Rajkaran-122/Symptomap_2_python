"""
Comprehensive India-wide Database Seeder
Populates doctor_outbreaks with data from all major Indian states
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

# Comprehensive list of Indian cities with coordinates
INDIAN_CITIES = [
    # Rajasthan
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125},
    {"city": "Ajmer", "state": "Rajasthan", "lat": 26.4499, "lng": 74.6399},
    
    # Maharashtra
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lng": 73.7898},
    
    # Delhi NCR
    {"city": "New Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"city": "Gurgaon", "state": "Haryana", "lat": 28.4595, "lng": 77.0266},
    {"city": "Noida", "state": "Uttar Pradesh", "lat": 28.5355, "lng": 77.3910},
    {"city": "Faridabad", "state": "Haryana", "lat": 28.4089, "lng": 77.3178},
    
    # Karnataka
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"city": "Mysore", "state": "Karnataka", "lat": 12.2958, "lng": 76.6394},
    {"city": "Mangalore", "state": "Karnataka", "lat": 12.9141, "lng": 74.8560},
    
    # Tamil Nadu
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558},
    {"city": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lng": 78.1198},
    
    # Gujarat
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311},
    {"city": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lng": 73.1812},
    {"city": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lng": 70.8022},
    
    # West Bengal
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    {"city": "Howrah", "state": "West Bengal", "lat": 22.5958, "lng": 88.2636},
    {"city": "Siliguri", "state": "West Bengal", "lat": 26.7271, "lng": 88.6393},
    
    # Telangana
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    {"city": "Warangal", "state": "Telangana", "lat": 17.9784, "lng": 79.5941},
    {"city": "Nizamabad", "state": "Telangana", "lat": 18.6725, "lng": 78.0941},
    
    # Andhra Pradesh
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
    {"city": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480},
    {"city": "Tirupati", "state": "Andhra Pradesh", "lat": 13.6288, "lng": 79.4192},
    
    # Kerala
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366},
    {"city": "Kozhikode", "state": "Kerala", "lat": 11.2588, "lng": 75.7804},
    
    # Uttar Pradesh
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"city": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739},
    {"city": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lng": 78.0081},
    {"city": "Prayagraj", "state": "Uttar Pradesh", "lat": 25.4358, "lng": 81.8463},
    
    # Madhya Pradesh
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
    {"city": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2183, "lng": 78.1828},
    {"city": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lng": 79.9864},
    
    # Bihar
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376},
    {"city": "Gaya", "state": "Bihar", "lat": 24.7914, "lng": 85.0002},
    {"city": "Muzaffarpur", "state": "Bihar", "lat": 26.1209, "lng": 85.3647},
    
    # Odisha
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245},
    {"city": "Cuttack", "state": "Odisha", "lat": 20.4625, "lng": 85.8830},
    {"city": "Rourkela", "state": "Odisha", "lat": 22.2604, "lng": 84.8536},
    
    # Punjab
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794},
    {"city": "Ludhiana", "state": "Punjab", "lat": 30.9010, "lng": 75.8573},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723},
    {"city": "Jalandhar", "state": "Punjab", "lat": 31.3260, "lng": 75.5762},
    
    # Jharkhand
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096},
    {"city": "Jamshedpur", "state": "Jharkhand", "lat": 22.8046, "lng": 86.2029},
    {"city": "Dhanbad", "state": "Jharkhand", "lat": 23.7957, "lng": 86.4304},
    
    # Chhattisgarh
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296},
    {"city": "Bhilai", "state": "Chhattisgarh", "lat": 21.2167, "lng": 81.4333},
    {"city": "Bilaspur", "state": "Chhattisgarh", "lat": 22.0797, "lng": 82.1391},
    
    # Assam
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362},
    {"city": "Silchar", "state": "Assam", "lat": 24.8333, "lng": 92.8000},
    {"city": "Dibrugarh", "state": "Assam", "lat": 27.4728, "lng": 94.9120},
    
    # Uttarakhand
    {"city": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lng": 78.0322},
    {"city": "Haridwar", "state": "Uttarakhand", "lat": 29.9457, "lng": 78.1642},
    {"city": "Rishikesh", "state": "Uttarakhand", "lat": 30.0869, "lng": 78.2676},
    
    # Himachal Pradesh
    {"city": "Shimla", "state": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734},
    {"city": "Dharamshala", "state": "Himachal Pradesh", "lat": 32.2190, "lng": 76.3234},
    {"city": "Manali", "state": "Himachal Pradesh", "lat": 32.2432, "lng": 77.1892},
    
    # Jammu & Kashmir
    {"city": "Srinagar", "state": "Jammu & Kashmir", "lat": 34.0837, "lng": 74.7973},
    {"city": "Jammu", "state": "Jammu & Kashmir", "lat": 32.7266, "lng": 74.8570},
    
    # Goa
    {"city": "Panaji", "state": "Goa", "lat": 15.4909, "lng": 73.8278},
    {"city": "Margao", "state": "Goa", "lat": 15.2832, "lng": 73.9862},
    
    # Northeast
    {"city": "Imphal", "state": "Manipur", "lat": 24.8170, "lng": 93.9368},
    {"city": "Shillong", "state": "Meghalaya", "lat": 25.5788, "lng": 91.8933},
    {"city": "Aizawl", "state": "Mizoram", "lat": 23.7271, "lng": 92.7176},
    {"city": "Kohima", "state": "Nagaland", "lat": 25.6751, "lng": 94.1086},
    {"city": "Agartala", "state": "Tripura", "lat": 23.8315, "lng": 91.2868},
    {"city": "Itanagar", "state": "Arunachal Pradesh", "lat": 27.0844, "lng": 93.6053},
    {"city": "Gangtok", "state": "Sikkim", "lat": 27.3389, "lng": 88.6065},
]

DISEASES = [
    "Viral Fever",
    "Dengue",
    "Malaria",
    "COVID-19",
    "Typhoid",
    "Cholera",
    "Influenza",
    "Chikungunya",
    "Tuberculosis",
    "Hepatitis A",
    "Gastroenteritis",
    "Respiratory Infection"
]

SEVERITIES = ["mild", "moderate", "severe"]
HOSPITALS = [
    "Government Hospital",
    "District Hospital", 
    "Medical College Hospital",
    "Primary Health Center",
    "Civil Hospital",
    "City Hospital",
    "General Hospital",
    "Referral Hospital"
]

def seed_comprehensive_data():
    """Seed database with comprehensive India-wide outbreak data"""
    
    db_path = 'backend-python/symptomap.db'
    
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ensure table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctor_outbreaks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_type TEXT,
            patient_count INTEGER,
            severity TEXT,
            latitude REAL,
            longitude REAL,
            location_name TEXT,
            city TEXT,
            state TEXT,
            description TEXT,
            date_reported TEXT,
            submitted_by TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'approved'
        )
    ''')
    
    # Clear existing data for fresh seed
    cursor.execute("DELETE FROM doctor_outbreaks")
    print("🗑️ Cleared existing data...")
    
    records = []
    
    # Generate 2-4 outbreaks per city
    for city_data in INDIAN_CITIES:
        num_outbreaks = random.randint(2, 4)
        
        for _ in range(num_outbreaks):
            disease = random.choice(DISEASES)
            severity = random.choices(SEVERITIES, weights=[0.5, 0.35, 0.15])[0]
            patient_count = random.randint(5, 150) if severity == "severe" else random.randint(1, 50)
            
            # Slight coordinate variation for different hospital locations
            lat = city_data["lat"] + random.uniform(-0.05, 0.05)
            lng = city_data["lng"] + random.uniform(-0.05, 0.05)
            
            hospital = f"{random.choice(HOSPITALS)}, {city_data['city']}"
            
            # Random date within last 30 days
            days_ago = random.randint(0, 30)
            date_reported = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            created_at = datetime.now().isoformat()
            
            description = f"{disease} outbreak reported at {hospital}. {patient_count} patients affected. Severity: {severity}."
            
            # 70% approved, 20% pending, 10% rejected
            status = random.choices(["approved", "pending", "rejected"], weights=[0.7, 0.2, 0.1])[0]
            
            records.append((
                disease,
                patient_count,
                severity,
                lat,
                lng,
                hospital,
                city_data["city"],
                city_data["state"],
                description,
                date_reported,
                f"Dr. {random.choice(['Sharma', 'Patel', 'Singh', 'Kumar', 'Reddy', 'Gupta', 'Verma', 'Yadav'])}",
                created_at,
                status
            ))
    
    # Insert all records
    cursor.executemany('''
        INSERT INTO doctor_outbreaks 
        (disease_type, patient_count, severity, latitude, longitude, location_name, city, state, description, date_reported, submitted_by, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    
    conn.commit()
    
    # Count by status
    cursor.execute("SELECT status, count(*) FROM doctor_outbreaks GROUP BY status")
    status_counts = cursor.fetchall()
    
    # Count by state
    cursor.execute("SELECT state, count(*) FROM doctor_outbreaks GROUP BY state ORDER BY count(*) DESC LIMIT 10")
    state_counts = cursor.fetchall()
    
    conn.close()
    
    print(f"\n✅ Successfully seeded {len(records)} outbreak records!")
    print(f"\n📊 Status Distribution:")
    for status, count in status_counts:
        print(f"   {status}: {count}")
    
    print(f"\n🗺️ Top States:")
    for state, count in state_counts:
        print(f"   {state}: {count} outbreaks")
    
    print(f"\n🏥 Covered {len(INDIAN_CITIES)} cities across India including Jaipur, Rajasthan")

if __name__ == "__main__":
    seed_comprehensive_data()
