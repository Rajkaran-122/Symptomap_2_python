"""
Comprehensive data seeding for prediction model training and real-time functionality.
Seeds historical outbreak data directly into the main outbreaks table.
"""
import requests
import json
from datetime import datetime, timedelta
import random

API_URL = "https://symptomap-2-python-1.onrender.com"

# Historical outbreak data for ML training - 100+ records with varied patterns
HISTORICAL_OUTBREAKS = []

# Disease types with their typical patterns
DISEASES = [
    ("Dengue", "vector_borne", ["critical", "moderate", "moderate", "mild"]),
    ("Malaria", "vector_borne", ["critical", "moderate", "moderate", "mild"]),
    ("Chikungunya", "vector_borne", ["moderate", "moderate", "mild"]),
    ("COVID-19", "respiratory", ["critical", "moderate", "moderate", "mild"]),
    ("H1N1", "respiratory", ["critical", "moderate", "mild"]),
    ("Typhoid", "water_borne", ["critical", "moderate", "moderate"]),
    ("Cholera", "water_borne", ["critical", "critical", "moderate"]),
    ("Hepatitis A", "water_borne", ["moderate", "moderate", "mild"]),
    ("Viral Fever", "seasonal", ["moderate", "mild", "mild"]),
    ("Leptospirosis", "flood_related", ["critical", "moderate"]),
    ("Japanese Encephalitis", "encephalitis", ["critical", "critical"]),
    ("Measles", "vaccine_preventable", ["critical", "moderate"]),
    ("Tuberculosis", "chronic", ["moderate", "moderate"]),
]

# Major Indian cities with coordinates
CITIES = [
    {"city": "New Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707},
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462},
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376},
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126},
    {"city": "Chandigarh", "state": "Chandigarh", "lat": 30.7333, "lng": 76.7794},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366},
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577},
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673},
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185},
]

def generate_historical_data():
    """Generate 150 historical outbreak records for ML training"""
    outbreaks = []
    
    for i in range(150):
        disease_info = random.choice(DISEASES)
        disease_name = disease_info[0]
        disease_type = disease_info[1]
        severities = disease_info[2]
        
        city_info = random.choice(CITIES)
        
        # Generate realistic patient counts based on severity
        severity = random.choice(severities)
        if severity == "critical":
            patient_count = random.randint(200, 600)
        elif severity == "moderate":
            patient_count = random.randint(50, 200)
        else:
            patient_count = random.randint(10, 50)
        
        # Add some coordinate variation for clustering
        lat_var = random.uniform(-0.05, 0.05)
        lng_var = random.uniform(-0.05, 0.05)
        
        # Historical dates spanning last 6 months
        days_ago = random.randint(1, 180)
        date_reported = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        outbreak = {
            "disease_type": disease_name,
            "patient_count": patient_count,
            "severity": severity,
            "latitude": round(city_info["lat"] + lat_var, 6),
            "longitude": round(city_info["lng"] + lng_var, 6),
            "location_name": f"{city_info['city']} Zone {random.randint(1, 10)}",
            "city": city_info["city"],
            "state": city_info["state"],
            "date_reported": date_reported,
            "description": f"{disease_name} outbreak - {patient_count} cases reported in {city_info['city']}",
            "status": "approved"  # Historical data is already approved
        }
        outbreaks.append(outbreak)
    
    return outbreaks

def seed_historical_data():
    """Seed historical outbreak data directly to the main outbreaks table"""
    print("Generating 150 historical outbreak records...")
    outbreaks = generate_historical_data()
    
    # Use the seed endpoint to insert directly
    print(f"Seeding {len(outbreaks)} historical outbreaks for ML training...")
    
    response = requests.post(
        f"{API_URL}/seed-historical-outbreaks",
        json={"outbreaks": outbreaks},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"✅ Successfully seeded historical data: {response.json()}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        # Try alternative approach - submit via doctor station
        fallback_seed(outbreaks[:50])  # Seed first 50 via doctor API

def fallback_seed(outbreaks):
    """Fallback: Submit outbreaks via doctor API"""
    print("\n📋 Using fallback method - submitting via Doctor API...")
    
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return
    
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    success = 0
    for i, outbreak in enumerate(outbreaks):
        resp = requests.post(f"{API_URL}/api/v1/doctor/outbreak", headers=headers, json=outbreak)
        if resp.status_code == 200:
            success += 1
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{len(outbreaks)} ({success} successful)")
    
    print(f"✅ Submitted {success}/{len(outbreaks)} outbreaks")
    
    # Auto-approve them
    print("\n🔄 Auto-approving submitted outbreaks...")
    pending_resp = requests.get(f"{API_URL}/api/v1/admin/pending", headers=headers)
    if pending_resp.status_code == 200:
        pending = pending_resp.json()
        approved = 0
        for outbreak in pending:
            outbreak_id = outbreak.get("id")
            approve_resp = requests.post(f"{API_URL}/api/v1/admin/approve/{outbreak_id}", headers=headers)
            if approve_resp.status_code == 200:
                approved += 1
        print(f"✅ Approved {approved} outbreaks")

def check_stats():
    """Check current stats"""
    print("\n--- Current Status ---")
    
    # Check alerts
    resp = requests.get(f"{API_URL}/api/v1/alerts/")
    if resp.status_code == 200:
        alerts = resp.json()
        print(f"📋 Alerts: {len(alerts)}")
    
    # Check outbreaks via dashboard endpoint
    resp = requests.get(f"{API_URL}/api/v1/dashboard/stats")
    if resp.status_code == 200:
        stats = resp.json()
        print(f"📊 Dashboard Stats: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    # Seed historical data
    seed_historical_data()
    
    # Check final stats
    check_stats()
