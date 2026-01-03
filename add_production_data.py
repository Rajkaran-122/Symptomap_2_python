"""
Add outbreak data to production via Doctor Station API
Adds zones for Jaipur and other major Indian cities
"""

import urllib.request
import json
import random

# Production API URL
API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

# Cities with coordinates
CITIES = [
    # Rajasthan (Jaipur focus)
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873, "hospital": "SMS Hospital"},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.8500, "lng": 75.8200, "hospital": "Jaipur General Hospital"},
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9300, "lng": 75.7500, "hospital": "Sawai Man Singh Hospital"},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243, "hospital": "MDM Hospital"},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125, "hospital": "MB Hospital"},
    
    # Delhi NCR
    {"city": "New Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090, "hospital": "AIIMS Delhi"},
    {"city": "New Delhi", "state": "Delhi", "lat": 28.5700, "lng": 77.2300, "hospital": "Safdarjung Hospital"},
    {"city": "Gurgaon", "state": "Haryana", "lat": 28.4595, "lng": 77.0266, "hospital": "Medanta Hospital"},
    
    # Maharashtra
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777, "hospital": "KEM Hospital"},
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0200, "lng": 72.8500, "hospital": "Lilavati Hospital"},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567, "hospital": "Sassoon Hospital"},
    
    # Karnataka
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946, "hospital": "Victoria Hospital"},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9500, "lng": 77.6200, "hospital": "Bowring Hospital"},
    
    # Tamil Nadu
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707, "hospital": "Rajiv Gandhi GH"},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0500, "lng": 80.2400, "hospital": "Apollo Chennai"},
    
    # West Bengal
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639, "hospital": "SSKM Hospital"},
    
    # Telangana
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867, "hospital": "Gandhi Hospital"},
    
    # Gujarat
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714, "hospital": "Civil Hospital"},
    
    # Uttar Pradesh
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462, "hospital": "KGMU Hospital"},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739, "hospital": "BHU Hospital"},
    
    # Madhya Pradesh
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126, "hospital": "Hamidia Hospital"},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577, "hospital": "MY Hospital"},
    
    # Bihar
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376, "hospital": "PMCH Hospital"},
    
    # Kerala
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673, "hospital": "Medical College"},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366, "hospital": "MCH Hospital"},
]

DISEASES = ["Dengue", "Malaria", "Viral Fever", "Typhoid", "COVID-19", "Chikungunya", "Influenza", "Tuberculosis"]
SEVERITIES = ["mild", "moderate", "severe"]

def get_doctor_token():
    """Login and get doctor token"""
    url = f"{API_URL}/doctor/login"
    data = json.dumps({"password": "Doctor@SymptoMap2025"}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode())
        return result.get('access_token')
    except Exception as e:
        print(f"Login error: {e}")
        return None

def submit_outbreak(token, city_data, disease, severity, patient_count):
    """Submit a single outbreak via API"""
    url = f"{API_URL}/doctor/outbreak"
    
    payload = {
        "disease_type": disease,
        "patient_count": patient_count,
        "severity": severity,
        "latitude": city_data["lat"] + random.uniform(-0.02, 0.02),
        "longitude": city_data["lng"] + random.uniform(-0.02, 0.02),
        "location_name": city_data["hospital"],
        "city": city_data["city"],
        "state": city_data["state"],
        "description": f"{disease} outbreak reported at {city_data['hospital']}, {city_data['city']}"
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        return True
    except urllib.request.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode()[:100]}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("🔐 Getting doctor token...")
    token = get_doctor_token()
    
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Token obtained")
    
    success_count = 0
    total = len(CITIES)
    
    print(f"\n📍 Adding {total} outbreak zones across India...\n")
    
    for i, city_data in enumerate(CITIES):
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=[0.4, 0.4, 0.2])[0]
        patient_count = random.randint(10, 100) if severity == "severe" else random.randint(5, 50)
        
        if submit_outbreak(token, city_data, disease, severity, patient_count):
            success_count += 1
            print(f"  ✅ {city_data['city']}, {city_data['state']} - {disease} ({severity})")
        else:
            print(f"  ❌ {city_data['city']} - Failed")
    
    print(f"\n🎉 Successfully added {success_count}/{total} outbreak zones!")
    print(f"\n📍 Jaipur zones: 3")
    print(f"📍 Other major cities: {success_count - 3}")
    print(f"\n🔄 Refresh the dashboard to see the new zones!")

if __name__ == "__main__":
    main()
