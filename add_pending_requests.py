"""
Add 50 pending approval requests to production
For testing the Approval Requests page
"""

import urllib.request
import json
import random
import time

# Production API URL
API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

# Extended cities list for 50 requests
CITIES = [
    # North India
    {"city": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lng": 75.7873, "hospital": "SMS Hospital"},
    {"city": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lng": 73.0243, "hospital": "MDM Hospital"},
    {"city": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lng": 73.7125, "hospital": "MB Hospital"},
    {"city": "Bikaner", "state": "Rajasthan", "lat": 28.0229, "lng": 73.3119, "hospital": "PBM Hospital"},
    {"city": "New Delhi", "state": "Delhi", "lat": 28.6139, "lng": 77.2090, "hospital": "AIIMS Delhi"},
    {"city": "Gurgaon", "state": "Haryana", "lat": 28.4595, "lng": 77.0266, "hospital": "Medanta Hospital"},
    {"city": "Chandigarh", "state": "Punjab", "lat": 30.7333, "lng": 76.7794, "hospital": "PGIMER"},
    {"city": "Amritsar", "state": "Punjab", "lat": 31.6340, "lng": 74.8723, "hospital": "Civil Hospital"},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462, "hospital": "KGMU Hospital"},
    {"city": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lng": 82.9739, "hospital": "BHU Hospital"},
    {"city": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lng": 78.0081, "hospital": "SN Medical College"},
    {"city": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lng": 80.3319, "hospital": "Hallett Hospital"},
    
    # West India
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lng": 72.8777, "hospital": "KEM Hospital"},
    {"city": "Pune", "state": "Maharashtra", "lat": 18.5204, "lng": 73.8567, "hospital": "Sassoon Hospital"},
    {"city": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lng": 79.0882, "hospital": "Mayo Hospital"},
    {"city": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lng": 73.7898, "hospital": "Civil Hospital Nashik"},
    {"city": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lng": 72.5714, "hospital": "Civil Hospital"},
    {"city": "Surat", "state": "Gujarat", "lat": 21.1702, "lng": 72.8311, "hospital": "New Civil Hospital"},
    {"city": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lng": 73.1812, "hospital": "SSG Hospital"},
    {"city": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lng": 70.8022, "hospital": "PDU Medical College"},
    
    # South India
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lng": 77.5946, "hospital": "Victoria Hospital"},
    {"city": "Mysore", "state": "Karnataka", "lat": 12.2958, "lng": 76.6394, "hospital": "K.R. Hospital"},
    {"city": "Mangalore", "state": "Karnataka", "lat": 12.9141, "lng": 74.8560, "hospital": "Wenlock Hospital"},
    {"city": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lng": 80.2707, "hospital": "Rajiv Gandhi GH"},
    {"city": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lng": 76.9558, "hospital": "Coimbatore Medical College"},
    {"city": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lng": 78.1198, "hospital": "GRH Madurai"},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lng": 78.4867, "hospital": "Gandhi Hospital"},
    {"city": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lng": 83.2185, "hospital": "KGH Hospital"},
    {"city": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lng": 80.6480, "hospital": "GGH Vijayawada"},
    {"city": "Kochi", "state": "Kerala", "lat": 9.9312, "lng": 76.2673, "hospital": "Medical College"},
    {"city": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lng": 76.9366, "hospital": "MCH Hospital"},
    {"city": "Kozhikode", "state": "Kerala", "lat": 11.2588, "lng": 75.7804, "hospital": "Calicut Medical College"},
    
    # East India
    {"city": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lng": 88.3639, "hospital": "SSKM Hospital"},
    {"city": "Howrah", "state": "West Bengal", "lat": 22.5958, "lng": 88.2636, "hospital": "Howrah General Hospital"},
    {"city": "Siliguri", "state": "West Bengal", "lat": 26.7271, "lng": 88.6393, "hospital": "North Bengal Medical College"},
    {"city": "Patna", "state": "Bihar", "lat": 25.5941, "lng": 85.1376, "hospital": "PMCH Hospital"},
    {"city": "Gaya", "state": "Bihar", "lat": 24.7914, "lng": 85.0002, "hospital": "ANMCH Gaya"},
    {"city": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lng": 85.3096, "hospital": "RIMS Ranchi"},
    {"city": "Jamshedpur", "state": "Jharkhand", "lat": 22.8046, "lng": 86.2029, "hospital": "MGM Hospital"},
    {"city": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lng": 85.8245, "hospital": "SCB Medical College"},
    {"city": "Cuttack", "state": "Odisha", "lat": 20.4625, "lng": 85.8828, "hospital": "SCB Medical College"},
    
    # Central India
    {"city": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lng": 77.4126, "hospital": "Hamidia Hospital"},
    {"city": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lng": 75.8577, "hospital": "MY Hospital"},
    {"city": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2183, "lng": 78.1828, "hospital": "JAH Hospital"},
    {"city": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lng": 79.9864, "hospital": "Netaji Subhash Hospital"},
    {"city": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lng": 81.6296, "hospital": "Dr BR Ambedkar Hospital"},
    
    # Northeast India
    {"city": "Guwahati", "state": "Assam", "lat": 26.1445, "lng": 91.7362, "hospital": "GMCH Hospital"},
    {"city": "Imphal", "state": "Manipur", "lat": 24.8170, "lng": 93.9368, "hospital": "RIMS Imphal"},
    {"city": "Shillong", "state": "Meghalaya", "lat": 25.5788, "lng": 91.8933, "hospital": "Civil Hospital Shillong"},
    {"city": "Agartala", "state": "Tripura", "lat": 23.8315, "lng": 91.2868, "hospital": "GBP Hospital"},
]

DISEASES = ["Dengue", "Malaria", "Viral Fever", "Typhoid", "COVID-19", "Chikungunya", "Influenza", "Tuberculosis", "Cholera", "Hepatitis A"]
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
    """Submit a single outbreak via API (will be pending)"""
    url = f"{API_URL}/doctor/outbreak"
    
    payload = {
        "disease_type": disease,
        "patient_count": patient_count,
        "severity": severity,
        "latitude": city_data["lat"] + random.uniform(-0.03, 0.03),
        "longitude": city_data["lng"] + random.uniform(-0.03, 0.03),
        "location_name": city_data["hospital"],
        "city": city_data["city"],
        "state": city_data["state"],
        "description": f"{disease} outbreak reported at {city_data['hospital']}, {city_data['city']}. Requires immediate attention."
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
    
    # Submit 50 pending requests
    print(f"\n📝 Submitting 50 pending approval requests...\n")
    
    success_count = 0
    
    for i in range(50):
        city_data = CITIES[i % len(CITIES)]
        disease = random.choice(DISEASES)
        severity = random.choices(SEVERITIES, weights=[0.3, 0.4, 0.3])[0]
        patient_count = random.randint(10, 150)
        
        if submit_outbreak(token, city_data, disease, severity, patient_count):
            success_count += 1
            print(f"  ✅ [{i+1}/50] {city_data['city']}, {city_data['state']} - {disease} ({severity}, {patient_count} patients)")
        else:
            print(f"  ❌ [{i+1}/50] {city_data['city']} - Failed")
        
        # Small delay to avoid database lock
        time.sleep(0.5)
    
    print(f"\n🎉 Successfully submitted {success_count}/50 pending requests!")
    print(f"\n📋 Visit to see pending approvals:")
    print(f"   https://symptomap-2-python.vercel.app/admin/approvals")

if __name__ == "__main__":
    main()
