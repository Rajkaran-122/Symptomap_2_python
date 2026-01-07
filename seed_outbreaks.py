"""
Seed 50 outbreaks across India for the Approval workflow
- 30 pending (for approval queue)
- 20 approved (to show on dashboard map)
"""
import requests
import json

API_URL = "https://symptomap-2-python-1.onrender.com"

# Comprehensive outbreak data across India
OUTBREAKS = [
    # Delhi (Critical)
    {"disease_type": "Dengue", "patient_count": 450, "severity": "critical", "latitude": 28.6139, "longitude": 77.2090, "location_name": "Saket", "city": "New Delhi", "state": "Delhi", "description": "Severe dengue outbreak in residential areas"},
    {"disease_type": "Dengue", "patient_count": 380, "severity": "critical", "latitude": 28.6280, "longitude": 77.2189, "location_name": "Lajpat Nagar", "city": "New Delhi", "state": "Delhi", "description": "Mosquito breeding sites found near markets"},
    {"disease_type": "Chikungunya", "patient_count": 220, "severity": "moderate", "latitude": 28.5921, "longitude": 77.0460, "location_name": "Dwarka", "city": "New Delhi", "state": "Delhi", "description": "Chikungunya cases rising post-monsoon"},
    
    # Mumbai (Critical)
    {"disease_type": "Malaria", "patient_count": 520, "severity": "critical", "latitude": 19.0760, "longitude": 72.8777, "location_name": "Dharavi", "city": "Mumbai", "state": "Maharashtra", "description": "Malaria outbreak in slum area"},
    {"disease_type": "Cholera", "patient_count": 180, "severity": "critical", "latitude": 19.0176, "longitude": 72.8562, "location_name": "Bandra", "city": "Mumbai", "state": "Maharashtra", "description": "Contaminated water supply identified"},
    {"disease_type": "Typhoid", "patient_count": 150, "severity": "moderate", "latitude": 19.1136, "longitude": 72.8697, "location_name": "Andheri", "city": "Mumbai", "state": "Maharashtra", "description": "Typhoid cases from street food vendors"},
    
    # Bangalore (Moderate)
    {"disease_type": "COVID-19", "patient_count": 340, "severity": "moderate", "latitude": 12.9716, "longitude": 77.5946, "location_name": "Koramangala", "city": "Bangalore", "state": "Karnataka", "description": "New COVID variant cluster in tech hub"},
    {"disease_type": "Viral Fever", "patient_count": 280, "severity": "moderate", "latitude": 12.9352, "longitude": 77.6245, "location_name": "Whitefield", "city": "Bangalore", "state": "Karnataka", "description": "Seasonal viral fever surge"},
    {"disease_type": "H1N1", "patient_count": 95, "severity": "moderate", "latitude": 13.0358, "longitude": 77.5970, "location_name": "Yelahanka", "city": "Bangalore", "state": "Karnataka", "description": "Swine flu cases in northern areas"},
    
    # Chennai (Critical)
    {"disease_type": "Typhoid", "patient_count": 410, "severity": "critical", "latitude": 13.0827, "longitude": 80.2707, "location_name": "T. Nagar", "city": "Chennai", "state": "Tamil Nadu", "description": "Water contamination causing typhoid spike"},
    {"disease_type": "Dengue", "patient_count": 320, "severity": "critical", "latitude": 13.0569, "longitude": 80.2425, "location_name": "Anna Nagar", "city": "Chennai", "state": "Tamil Nadu", "description": "Dengue outbreak after heavy rains"},
    {"disease_type": "Leptospirosis", "patient_count": 85, "severity": "moderate", "latitude": 13.1067, "longitude": 80.2206, "location_name": "Perambur", "city": "Chennai", "state": "Tamil Nadu", "description": "Flood-related leptospirosis cases"},
    
    # Kolkata (Moderate)
    {"disease_type": "Malaria", "patient_count": 290, "severity": "moderate", "latitude": 22.5726, "longitude": 88.3639, "location_name": "Salt Lake", "city": "Kolkata", "state": "West Bengal", "description": "Malaria surge in eastern areas"},
    {"disease_type": "Dengue", "patient_count": 240, "severity": "moderate", "latitude": 22.5448, "longitude": 88.3426, "location_name": "Park Street", "city": "Kolkata", "state": "West Bengal", "description": "Dengue cases in commercial district"},
    {"disease_type": "Hepatitis A", "patient_count": 110, "severity": "moderate", "latitude": 22.6243, "longitude": 88.4025, "location_name": "Rajarhat", "city": "Kolkata", "state": "West Bengal", "description": "Hepatitis from contaminated food"},
    
    # Hyderabad (Moderate)  
    {"disease_type": "Chikungunya", "patient_count": 260, "severity": "moderate", "latitude": 17.3850, "longitude": 78.4867, "location_name": "Hitech City", "city": "Hyderabad", "state": "Telangana", "description": "Chikungunya in IT corridor"},
    {"disease_type": "Dengue", "patient_count": 200, "severity": "moderate", "latitude": 17.4156, "longitude": 78.4347, "location_name": "Secunderabad", "city": "Hyderabad", "state": "Telangana", "description": "Dengue spread in cantonment area"},
    {"disease_type": "Viral Fever", "patient_count": 175, "severity": "mild", "latitude": 17.3616, "longitude": 78.4747, "location_name": "Gachibowli", "city": "Hyderabad", "state": "Telangana", "description": "Seasonal viral infection"},
    
    # Pune (Moderate)
    {"disease_type": "Swine Flu", "patient_count": 185, "severity": "moderate", "latitude": 18.5204, "longitude": 73.8567, "location_name": "Koregaon Park", "city": "Pune", "state": "Maharashtra", "description": "H1N1 cluster identified"},
    {"disease_type": "Dengue", "patient_count": 165, "severity": "moderate", "latitude": 18.5018, "longitude": 73.8636, "location_name": "Camp", "city": "Pune", "state": "Maharashtra", "description": "Dengue in cantonment areas"},
    
    # Ahmedabad (Moderate)
    {"disease_type": "Cholera", "patient_count": 145, "severity": "moderate", "latitude": 23.0225, "longitude": 72.5714, "location_name": "Maninagar", "city": "Ahmedabad", "state": "Gujarat", "description": "Water-borne disease outbreak"},
    {"disease_type": "Typhoid", "patient_count": 120, "severity": "moderate", "latitude": 23.0500, "longitude": 72.5300, "location_name": "Navrangpura", "city": "Ahmedabad", "state": "Gujarat", "description": "Typhoid cases from contaminated well"},
    
    # Jaipur (Mild)
    {"disease_type": "Viral Fever", "patient_count": 195, "severity": "mild", "latitude": 26.9124, "longitude": 75.7873, "location_name": "Malviya Nagar", "city": "Jaipur", "state": "Rajasthan", "description": "Seasonal fever outbreak"},
    {"disease_type": "Dengue", "patient_count": 140, "severity": "moderate", "latitude": 26.8911, "longitude": 75.8019, "location_name": "Vaishali Nagar", "city": "Jaipur", "state": "Rajasthan", "description": "Dengue in residential colony"},
    
    # Lucknow (Moderate)
    {"disease_type": "Encephalitis", "patient_count": 95, "severity": "critical", "latitude": 26.8467, "longitude": 80.9462, "location_name": "Gomti Nagar", "city": "Lucknow", "state": "Uttar Pradesh", "description": "Japanese encephalitis cases"},
    {"disease_type": "Viral Fever", "patient_count": 210, "severity": "moderate", "latitude": 26.8393, "longitude": 80.9231, "location_name": "Hazratganj", "city": "Lucknow", "state": "Uttar Pradesh", "description": "Viral infection surge"},
    
    # Patna (Critical)
    {"disease_type": "Measles", "patient_count": 380, "severity": "critical", "latitude": 25.5941, "longitude": 85.1376, "location_name": "Patna City", "city": "Patna", "state": "Bihar", "description": "Measles outbreak in children"},
    {"disease_type": "Cholera", "patient_count": 220, "severity": "critical", "latitude": 25.6093, "longitude": 85.1235, "location_name": "Kankarbagh", "city": "Patna", "state": "Bihar", "description": "Cholera from flood waters"},
    
    # Indore (Moderate)
    {"disease_type": "Dengue", "patient_count": 175, "severity": "moderate", "latitude": 22.7196, "longitude": 75.8577, "location_name": "Vijay Nagar", "city": "Indore", "state": "Madhya Pradesh", "description": "Dengue cases post-monsoon"},
    
    # Bhopal (Moderate)
    {"disease_type": "Malaria", "patient_count": 135, "severity": "moderate", "latitude": 23.2599, "longitude": 77.4126, "location_name": "MP Nagar", "city": "Bhopal", "state": "Madhya Pradesh", "description": "Malaria near lake areas"},
    
    # Chandigarh (Mild)
    {"disease_type": "COVID-19", "patient_count": 85, "severity": "mild", "latitude": 30.7333, "longitude": 76.7794, "location_name": "Sector 17", "city": "Chandigarh", "state": "Chandigarh", "description": "Minor COVID cluster"},
    
    # Surat (Moderate)
    {"disease_type": "Plague", "patient_count": 45, "severity": "critical", "latitude": 21.1702, "longitude": 72.8311, "location_name": "Katargam", "city": "Surat", "state": "Gujarat", "description": "Suspected plague case under investigation"},
    
    # Nagpur (Moderate)
    {"disease_type": "Dengue", "patient_count": 155, "severity": "moderate", "latitude": 21.1458, "longitude": 79.0882, "location_name": "Dharampeth", "city": "Nagpur", "state": "Maharashtra", "description": "Dengue in central Nagpur"},
    
    # Visakhapatnam (Mild)
    {"disease_type": "Viral Fever", "patient_count": 125, "severity": "mild", "latitude": 17.6868, "longitude": 83.2185, "location_name": "MVP Colony", "city": "Visakhapatnam", "state": "Andhra Pradesh", "description": "Seasonal viral infection"},
    
    # Coimbatore (Mild)
    {"disease_type": "Dengue", "patient_count": 110, "severity": "mild", "latitude": 11.0168, "longitude": 76.9558, "location_name": "RS Puram", "city": "Coimbatore", "state": "Tamil Nadu", "description": "Dengue in residential areas"},
    
    # Kochi (Moderate)
    {"disease_type": "Leptospirosis", "patient_count": 75, "severity": "moderate", "latitude": 9.9312, "longitude": 76.2673, "location_name": "Ernakulam", "city": "Kochi", "state": "Kerala", "description": "Post-flood leptospirosis"},
    {"disease_type": "Dengue", "patient_count": 95, "severity": "moderate", "latitude": 9.9816, "longitude": 76.2999, "location_name": "Kakkanad", "city": "Kochi", "state": "Kerala", "description": "Dengue in IT park area"},
    
    # Thiruvananthapuram (Mild)
    {"disease_type": "Chikungunya", "patient_count": 85, "severity": "mild", "latitude": 8.5241, "longitude": 76.9366, "location_name": "Technopark", "city": "Thiruvananthapuram", "state": "Kerala", "description": "Chikungunya cases in tech hub"},
    
    # Guwahati (Moderate)
    {"disease_type": "Malaria", "patient_count": 165, "severity": "moderate", "latitude": 26.1445, "longitude": 91.7362, "location_name": "Guwahati Central", "city": "Guwahati", "state": "Assam", "description": "Malaria in low-lying areas"},
    {"disease_type": "Encephalitis", "patient_count": 55, "severity": "critical", "latitude": 26.1158, "longitude": 91.7086, "location_name": "Dispur", "city": "Guwahati", "state": "Assam", "description": "Acute encephalitis syndrome"},
    
    # Ranchi (Moderate)
    {"disease_type": "Malaria", "patient_count": 140, "severity": "moderate", "latitude": 23.3441, "longitude": 85.3096, "location_name": "Doranda", "city": "Ranchi", "state": "Jharkhand", "description": "Malaria in tribal areas"},
    
    # Dehradun (Mild)
    {"disease_type": "Typhoid", "patient_count": 95, "severity": "mild", "latitude": 30.3165, "longitude": 78.0322, "location_name": "Rajpur Road", "city": "Dehradun", "state": "Uttarakhand", "description": "Typhoid from tourist hotels"},
    
    # Varanasi (Moderate)
    {"disease_type": "Cholera", "patient_count": 125, "severity": "moderate", "latitude": 25.3176, "longitude": 82.9739, "location_name": "Dashashwamedh", "city": "Varanasi", "state": "Uttar Pradesh", "description": "Water-borne disease near ghats"},
    
    # Agra (Mild)
    {"disease_type": "Dengue", "patient_count": 105, "severity": "mild", "latitude": 27.1767, "longitude": 78.0081, "location_name": "Taj Nagari", "city": "Agra", "state": "Uttar Pradesh", "description": "Dengue in residential areas"},
    
    # Shimla (Mild)
    {"disease_type": "Viral Fever", "patient_count": 65, "severity": "mild", "latitude": 31.1048, "longitude": 77.1734, "location_name": "Mall Road", "city": "Shimla", "state": "Himachal Pradesh", "description": "Tourist-related viral spread"},
    
    # Raipur (Moderate)
    {"disease_type": "Malaria", "patient_count": 185, "severity": "moderate", "latitude": 21.2514, "longitude": 81.6296, "location_name": "Civil Lines", "city": "Raipur", "state": "Chhattisgarh", "description": "Malaria in forested periphery"},
    
    # Bhubaneswar (Moderate)
    {"disease_type": "Dengue", "patient_count": 145, "severity": "moderate", "latitude": 20.2961, "longitude": 85.8245, "location_name": "Saheed Nagar", "city": "Bhubaneswar", "state": "Odisha", "description": "Dengue outbreak post-cyclone"},
    
    # Jodhpur (Mild)
    {"disease_type": "Viral Fever", "patient_count": 95, "severity": "mild", "latitude": 26.2389, "longitude": 73.0243, "location_name": "Paota", "city": "Jodhpur", "state": "Rajasthan", "description": "Seasonal fever in desert region"},
    
    # Mysore (Mild)
    {"disease_type": "Chikungunya", "patient_count": 75, "severity": "mild", "latitude": 12.2958, "longitude": 76.6394, "location_name": "Vijayanagar", "city": "Mysore", "state": "Karnataka", "description": "Minor chikungunya cluster"},
]

def seed_outbreaks():
    """Seed 50 outbreaks to the doctor_outbreaks table"""
    print(f"Seeding {len(OUTBREAKS)} outbreaks to production...")
    
    # First, get doctor token by logging in
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.text}")
        return
    
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    success_count = 0
    for i, outbreak in enumerate(OUTBREAKS):
        # Submit as doctor outbreak
        resp = requests.post(f"{API_URL}/api/v1/doctor/outbreak", headers=headers, json=outbreak)
        if resp.status_code == 200:
            success_count += 1
            print(f"✅ [{i+1}/{len(OUTBREAKS)}] Submitted: {outbreak['disease_type']} in {outbreak['city']}")
        else:
            print(f"❌ [{i+1}/{len(OUTBREAKS)}] Failed: {resp.text}")
    
    print(f"\n✅ Successfully submitted {success_count}/{len(OUTBREAKS)} outbreaks")
    return success_count

def check_pending():
    """Check pending approvals"""
    # Login to get admin token
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = requests.get(f"{API_URL}/api/v1/admin/pending", headers=headers)
    if resp.status_code == 200:
        pending = resp.json()
        print(f"\n📋 Pending approvals: {len(pending)}")
        return pending
    else:
        print(f"Failed to get pending: {resp.text}")
        return []

def approve_outbreaks(count=20):
    """Approve first N outbreaks so they appear on dashboard"""
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Get pending list
    pending = check_pending()
    
    approved = 0
    for outbreak in pending[:count]:
        outbreak_id = outbreak.get("id")
        if outbreak_id:
            resp = requests.post(f"{API_URL}/api/v1/admin/approve/{outbreak_id}", headers=headers)
            if resp.status_code == 200:
                approved += 1
                print(f"✅ Approved outbreak #{outbreak_id}")
            else:
                print(f"❌ Failed to approve #{outbreak_id}: {resp.text}")
    
    print(f"\n✅ Approved {approved} outbreaks for dashboard display")

if __name__ == "__main__":
    # Step 1: Seed 50 outbreaks
    seed_outbreaks()
    
    # Step 2: Check pending
    check_pending()
    
    # Step 3: Approve 20 to show on map
    approve_outbreaks(20)
    
    # Final check
    print("\n--- Final Status ---")
    check_pending()
