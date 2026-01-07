"""
Comprehensive data seeding for Symptomap:
1. Seed 20+ alerts to Alert Management
2. Seed historical outbreak data for prediction training
3. Add outbreaks to main database for ML predictions
"""
import requests
import json
from datetime import datetime, timezone, timedelta

API_URL = "https://symptomap-2-python-1.onrender.com"

# ============== ALERTS DATA ==============
ALERTS = [
    {"severity": "critical", "title": "Critical Dengue Outbreak Alert - Delhi", "zone_name": "Delhi", "message": "Severe dengue outbreak detected. All healthcare workers advised to take immediate precautions.", "type": "email", "recipients": ["admin@symptomap.com", "heath@delhi.gov.in", "doctor@example.com"]},
    {"severity": "critical", "title": "Emergency: Vector Control Teams Deployed", "zone_name": "Delhi - NCR", "message": "Emergency vector control teams deployed. Residents advised to use mosquito repellents.", "type": "email", "recipients": ["delhi@health.gov.in"]},
    {"severity": "critical", "title": "Hospital Capacity Critical - Mumbai", "zone_name": "Mumbai", "message": "Hospital capacity reaching critical levels. Public advised to avoid outdoor activities.", "type": "email", "recipients": ["mumbai@health.gov.in"]},
    {"severity": "warning", "title": "Moderate Viral Fever Cases - Pune", "zone_name": "Pune", "message": "Increasing viral fever cases reported. Citizens advised to maintain good hygiene.", "type": "email", "recipients": ["pune@health.gov.in"]},
    {"severity": "critical", "title": "AIIMS Delhi Capacity Alert", "zone_name": "Delhi", "message": "AIIMS Delhi reaching 95% capacity. Patients advised to visit nearby hospitals.", "type": "email", "recipients": ["aiims@health.gov.in"]},
    {"severity": "warning", "title": "COVID-19 Monitoring - Bangalore", "zone_name": "Bangalore", "message": "Slight increase in COVID-19 cases in tech corridors. Mask advisory in effect.", "type": "email", "recipients": ["blr@health.gov.in"]},
    {"severity": "warning", "title": "Viral Fever Outbreak - Pune", "zone_name": "Pune", "message": "Moderate viral fever cases rising. Health department conducting awareness camps.", "type": "email", "recipients": ["pune@nha.gov.in"]},
    {"severity": "info", "title": "Flu Season Advisory - Uttarakhand", "zone_name": "Uttarakhand", "message": "Seasonal flu increase expected. Residents advised to get flu vaccinations.", "type": "email", "recipients": ["uk@health.gov.in"]},
    {"severity": "warning", "title": "COVID-19 Rising - Bangalore", "zone_name": "Bangalore", "message": "Continued rise in COVID-19 cases. Enhanced testing at key locations.", "type": "email", "recipients": ["karnataka@nha.gov.in"]},
    {"severity": "info", "title": "Disease Surveillance Update", "zone_name": "National", "message": "Weekly disease surveillance report available. Overall situation stable.", "type": "email", "recipients": ["national@nha.gov.in"]},
    {"severity": "critical", "title": "Cholera Outbreak - Mumbai Slums", "zone_name": "Mumbai", "message": "Cholera outbreak confirmed in Dharavi area. Immediate water sanitation measures deployed.", "type": "email", "recipients": ["mumbai@health.gov.in", "bmc@gov.in"]},
    {"severity": "warning", "title": "Malaria Cases Surge - Kolkata", "zone_name": "Kolkata", "message": "Malaria cases increasing post-monsoon. Anti-malarial drugs distributed.", "type": "email", "recipients": ["kolkata@health.gov.in"]},
    {"severity": "critical", "title": "Typhoid Emergency - Chennai", "zone_name": "Chennai", "message": "Typhoid outbreak in north Chennai. Contaminated water source identified and sealed.", "type": "email", "recipients": ["chennai@health.gov.in"]},
    {"severity": "warning", "title": "Chikungunya Alert - Hyderabad", "zone_name": "Hyderabad", "message": "Rising chikungunya cases. Fumigation drives underway in affected areas.", "type": "email", "recipients": ["hyderabad@health.gov.in"]},
    {"severity": "info", "title": "Vaccination Drive - Rajasthan", "zone_name": "Rajasthan", "message": "State-wide polio vaccination drive scheduled. All children under 5 to be vaccinated.", "type": "email", "recipients": ["rajasthan@health.gov.in"]},
    {"severity": "warning", "title": "Hepatitis A Alert - Gujarat", "zone_name": "Ahmedabad", "message": "Hepatitis A cases reported in old city areas. Boil water advisory issued.", "type": "email", "recipients": ["ahmedabad@health.gov.in"]},
    {"severity": "critical", "title": "Measles Outbreak - Bihar", "zone_name": "Patna", "message": "Measles outbreak in rural areas. Emergency vaccination camps set up.", "type": "email", "recipients": ["bihar@health.gov.in"]},
    {"severity": "info", "title": "Health Camp - Kerala", "zone_name": "Kerala", "message": "Free health checkup camps organized across all districts.", "type": "email", "recipients": ["kerala@health.gov.in"]},
    {"severity": "warning", "title": "Leptospirosis Warning - Assam", "zone_name": "Guwahati", "message": "Post-flood leptospirosis cases rising. Prophylactic antibiotics distributed.", "type": "email", "recipients": ["assam@health.gov.in"]},
    {"severity": "critical", "title": "Japanese Encephalitis - UP", "zone_name": "Lucknow", "message": "JE cases in eastern UP. Mosquito control operations intensified.", "type": "email", "recipients": ["up@health.gov.in"]},
]

# ============== HISTORICAL OUTBREAK DATA FOR PREDICTIONS ==============
# Data spanning last 90 days for ML training
HISTORICAL_OUTBREAKS = []

# Major cities with realistic outbreak patterns
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
]

DISEASES = [
    {"name": "Dengue", "base_count": 150, "variance": 100, "severity_weights": [0.2, 0.5, 0.3]},
    {"name": "Malaria", "base_count": 100, "variance": 80, "severity_weights": [0.3, 0.5, 0.2]},
    {"name": "COVID-19", "base_count": 80, "variance": 50, "severity_weights": [0.4, 0.4, 0.2]},
    {"name": "Typhoid", "base_count": 60, "variance": 40, "severity_weights": [0.3, 0.5, 0.2]},
    {"name": "Chikungunya", "base_count": 70, "variance": 50, "severity_weights": [0.4, 0.4, 0.2]},
    {"name": "Viral Fever", "base_count": 200, "variance": 100, "severity_weights": [0.5, 0.4, 0.1]},
    {"name": "Cholera", "base_count": 40, "variance": 30, "severity_weights": [0.2, 0.4, 0.4]},
]

import random

def generate_historical_data():
    """Generate 90 days of historical outbreak data for predictions"""
    data = []
    severities = ["mild", "moderate", "critical"]
    
    for days_ago in range(90, 0, -1):
        date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
        
        # Each day, add 2-5 outbreaks across different cities
        num_outbreaks = random.randint(2, 5)
        for _ in range(num_outbreaks):
            city = random.choice(CITIES)
            disease = random.choice(DISEASES)
            
            # Calculate patient count with some variance
            patient_count = disease["base_count"] + random.randint(-disease["variance"], disease["variance"])
            patient_count = max(10, patient_count)  # Minimum 10 patients
            
            # Weighted severity selection
            severity = random.choices(severities, weights=disease["severity_weights"])[0]
            
            # Add some location variance
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            
            data.append({
                "disease_type": disease["name"],
                "patient_count": patient_count,
                "severity": severity,
                "latitude": city["lat"] + lat_offset,
                "longitude": city["lng"] + lng_offset,
                "location_name": f"{city['city']} Zone",
                "city": city["city"],
                "state": city["state"],
                "description": f"Historical {disease['name']} outbreak data for ML training",
                "date_reported": date,
                "status": "approved"  # Historical data is already approved
            })
    
    return data

def seed_alerts():
    """Seed alerts via the /seed-alerts endpoint"""
    print("=" * 50)
    print("STEP 1: Seeding Alerts")
    print("=" * 50)
    
    try:
        response = requests.post(f"{API_URL}/seed-alerts", timeout=60)
        result = response.json()
        print(f"Status: {result.get('status')}")
        print(f"Message: {result.get('message')}")
        return result.get('status') == 'success'
    except Exception as e:
        print(f"Error: {e}")
        return False

def seed_historical_outbreaks():
    """Seed historical outbreak data for prediction model training"""
    print("\n" + "=" * 50)
    print("STEP 2: Seeding Historical Outbreak Data (90 days)")
    print("=" * 50)
    
    # Login to get token
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return False
    
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Generate historical data
    historical_data = generate_historical_data()
    print(f"Generated {len(historical_data)} historical outbreak records")
    
    # Submit data in batches
    success_count = 0
    for i, outbreak in enumerate(historical_data):
        resp = requests.post(f"{API_URL}/api/v1/doctor/outbreak", headers=headers, json=outbreak)
        if resp.status_code == 200:
            success_count += 1
            if (i + 1) % 50 == 0:
                print(f"Progress: {i+1}/{len(historical_data)} submitted...")
        
    print(f"✅ Submitted {success_count}/{len(historical_data)} historical records")
    return success_count > 0

def seed_active_outbreaks():
    """Seed 50 active outbreaks for the current timeframe (Live Map)"""
    print("\n" + "=" * 50)
    print("STEP 2.5: Seeding 50 Active Outbreaks (Live Map)")
    print("=" * 50)
    
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    active_data = []
    severities = ["mild", "moderate", "critical"]
    
    print("Generating 50 active outbreaks...")
    for _ in range(50):
        city = random.choice(CITIES)
        disease = random.choice(DISEASES)
        
        # Random location offset within city
        lat_offset = random.uniform(-0.08, 0.08)
        lng_offset = random.uniform(-0.08, 0.08)
        
        active_data.append({
            "disease_type": disease["name"],
            "patient_count": random.randint(5, 50),
            "severity": random.choices(severities, weights=disease["severity_weights"])[0],
            "latitude": city["lat"] + lat_offset,
            "longitude": city["lng"] + lng_offset,
            "location_name": f"{city['city']} {random.choice(['North', 'South', 'East', 'West', 'Central'])}",
            "city": city["city"],
            "state": city["state"],
            "description": f"Active {disease['name']} outbreak reported by local clinic",
            "date_reported": datetime.now(timezone.utc).isoformat(),
            "status": "pending" 
        })
        
    success_count = 0
    for i, outbreak in enumerate(active_data):
        resp = requests.post(f"{API_URL}/api/v1/doctor/outbreak", headers=headers, json=outbreak)
        if resp.status_code == 200:
            success_count += 1
            if (i + 1) % 10 == 0:
                print(f"Status: {i+1}/50 seeded...")
                
    print(f"✅ Submitted {success_count}/50 active outbreaks")


def auto_approve_historical():
    """Auto-approve all historical data for predictions"""
    print("\n" + "=" * 50)
    print("STEP 3: Auto-approving Historical Data")
    print("=" * 50)
    
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get all pending
    resp = requests.get(f"{API_URL}/api/v1/admin/pending", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to get pending: {resp.text}")
        return
    
    pending = resp.json()
    print(f"Found {len(pending)} pending submissions")
    
    # Approve all
    approved = 0
    for item in pending:
        item_id = item.get("id")
        resp = requests.post(f"{API_URL}/api/v1/admin/approve/{item_id}", headers=headers)
        if resp.status_code == 200:
            approved += 1
            if approved % 50 == 0:
                print(f"Approved {approved} items...")
    
    print(f"✅ Approved {approved} items for dashboard/predictions")

def verify_data():
    """Verify all data is properly seeded"""
    print("\n" + "=" * 50)
    print("VERIFICATION")
    print("=" * 50)
    
    # Check alerts
    try:
        resp = requests.get(f"{API_URL}/api/v1/alerts/", timeout=30)
        alerts = resp.json()
        print(f"✅ Alerts: {len(alerts)}")
    except:
        print("❌ Could not verify alerts")
    
    # Check outbreaks
    try:
        resp = requests.get(f"{API_URL}/api/v1/outbreaks/", timeout=30)
        outbreaks = resp.json()
        print(f"✅ Outbreaks: {len(outbreaks)}")
    except:
        print("❌ Could not verify outbreaks")

if __name__ == "__main__":
    print("🚀 Comprehensive Data Seeding for Symptomap")
    print("=" * 50)
    
    # Step 1: Seed alerts
    seed_alerts()
    
    # Step 2: Seed historical data
    seed_historical_outbreaks()
    
    # Step 2.5: Seed active data
    seed_active_outbreaks()
    
    # Step 3: Approve for predictions
    auto_approve_historical()
    
    # Verify
    verify_data()
    
    print("\n✅ All data seeding complete!")
