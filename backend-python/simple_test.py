"""
Simple API test
"""
import requests

print("\n✅ Testing GET /outbreaks/...")
try:
    response = requests.get("http://localhost:8000/api/v1/outbreaks/", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS! Returned {len(data)} outbreaks")
        
        if len(data) > 0:
            print(f"\nFirst outbreak:")
            outbreak = data[0]
            print(f"  Hospital: {outbreak.get('hospital', {}).get('name', 'N/A')}")
            print(f"  Disease: {outbreak.get('disease_type', 'N/A')}")
            print(f"  Patients: {outbreak.get('patient_count', 0)}")
            print(f"  Severity: {outbreak.get('severity', 'N/A')}")
            location = outbreak.get('hospital', {}).get('location', {})
            print(f"  Location: ({location.get('lat', 0)}, {location.get('lng', 0)})")
            
        print(f"\n✨ API IS WORKING! Dashboard should show {len(data)} outbreaks\n")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
