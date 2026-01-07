"""
Add more pending outbreaks to the approval queue
"""
import requests

API_URL = "https://symptomap-2-python-1.onrender.com"

# Additional outbreaks to add to pending queue
MORE_OUTBREAKS = [
    {"disease_type": "Zika Virus", "patient_count": 45, "severity": "moderate", "latitude": 15.2993, "longitude": 74.1240, "location_name": "Panaji", "city": "Panaji", "state": "Goa", "description": "Zika cases in tourist area"},
    {"disease_type": "Nipah", "patient_count": 12, "severity": "critical", "latitude": 10.8505, "longitude": 76.2711, "location_name": "Malappuram", "city": "Kozhikode", "state": "Kerala", "description": "Suspected Nipah case - high alert"},
    {"disease_type": "Scrub Typhus", "patient_count": 65, "severity": "moderate", "latitude": 27.1767, "longitude": 88.1630, "location_name": "Darjeeling", "city": "Darjeeling", "state": "West Bengal", "description": "Scrub typhus in hill station"},
    {"disease_type": "Dengue", "patient_count": 180, "severity": "moderate", "latitude": 28.4595, "longitude": 77.0266, "location_name": "Sector 29", "city": "Gurgaon", "state": "Haryana", "description": "Dengue outbreak in corporate hub"},
    {"disease_type": "Japanese Encephalitis", "patient_count": 35, "severity": "critical", "latitude": 26.4499, "longitude": 80.3319, "location_name": "Kanpur", "city": "Kanpur", "state": "Uttar Pradesh", "description": "JE cases in children"},
    {"disease_type": "Rabies", "patient_count": 8, "severity": "critical", "latitude": 25.4358, "longitude": 81.8463, "location_name": "Allahabad", "city": "Prayagraj", "state": "Uttar Pradesh", "description": "Dog bite cases - rabies suspected"},
    {"disease_type": "Tuberculosis", "patient_count": 220, "severity": "moderate", "latitude": 22.3072, "longitude": 73.1812, "location_name": "Alkapuri", "city": "Vadodara", "state": "Gujarat", "description": "TB cluster in industrial area"},
    {"disease_type": "COVID-19", "patient_count": 95, "severity": "mild", "latitude": 19.2183, "longitude": 72.9781, "location_name": "Thane", "city": "Thane", "state": "Maharashtra", "description": "New COVID variant detected"},
    {"disease_type": "Hand Foot Mouth Disease", "patient_count": 145, "severity": "mild", "latitude": 13.0629, "longitude": 77.5937, "location_name": "Indiranagar", "city": "Bangalore", "state": "Karnataka", "description": "HFMD in school children"},
    {"disease_type": "Acute Diarrhea", "patient_count": 175, "severity": "moderate", "latitude": 28.9845, "longitude": 77.7064, "location_name": "Meerut", "city": "Meerut", "state": "Uttar Pradesh", "description": "Diarrhea from contaminated water"},
    {"disease_type": "Hepatitis E", "patient_count": 55, "severity": "moderate", "latitude": 23.8103, "longitude": 91.2787, "location_name": "Agartala", "city": "Agartala", "state": "Tripura", "description": "Hep E outbreak post-floods"},
    {"disease_type": "Kala Azar", "patient_count": 40, "severity": "critical", "latitude": 25.9644, "longitude": 85.1376, "location_name": "Muzaffarpur", "city": "Muzaffarpur", "state": "Bihar", "description": "Visceral leishmaniasis cases"},
]

def add_pending():
    """Add more pending outbreaks"""
    print(f"Adding {len(MORE_OUTBREAKS)} more outbreaks...")
    
    login_resp = requests.post(f"{API_URL}/api/v1/doctor/login", json={"password": "Doctor@SymptoMap2025"})
    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    for i, outbreak in enumerate(MORE_OUTBREAKS):
        resp = requests.post(f"{API_URL}/api/v1/doctor/outbreak", headers=headers, json=outbreak)
        if resp.status_code == 200:
            print(f"✅ [{i+1}/{len(MORE_OUTBREAKS)}] Added: {outbreak['disease_type']} in {outbreak['city']}")
        else:
            print(f"❌ Failed: {resp.text}")
    
    # Check pending count
    resp = requests.get(f"{API_URL}/api/v1/admin/pending", headers=headers)
    if resp.status_code == 200:
        print(f"\n📋 Total pending: {len(resp.json())}")

if __name__ == "__main__":
    add_pending()
