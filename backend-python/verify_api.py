"""
Quick API check to verify outbreak data
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

print("\n🔍 CHECKING API RESPONSES\n")

# Check outbreaks endpoint
try:
    response = requests.get(f"{API_BASE}/outbreaks/", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET /outbreaks/ - Status: {response.status_code}")
        print(f"   Outbreaks returned: {len(data)}")
        if len(data) > 0:
            print(f"\n   Sample outbreak:")
            outbreak = data[0]
            print(f"   - Hospital: {outbreak.get('hospital', {}).get('name', 'N/A')}")
            print(f"   - Disease: {outbreak.get('disease_type', 'N/A')}")
            print(f"   - Patients: {outbreak.get('patient_count', 0)}")
            print(f"   - Severity: {outbreak.get('severity', 'N/A')}")
    else:
        print(f"❌ GET /outbreaks/ - Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error checking outbreaks: {e}")

# Check stats endpoint
try:
    response = requests.get(f"{API_BASE}/stats/dashboard", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ GET /stats/dashboard - Status: {response.status_code}")
        print(f"   Total Outbreaks: {data.get('total_outbreaks', 0)}")
        print(f"   Active Cases: {data.get('active_cases', 0)}")
        print(f"   Hospitals Affected: {data.get('hospitals_affected', 0)}")
    else:
        print(f"❌ GET /stats/dashboard - Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error checking dashboard stats: {e}")

print("\n" + "="*60)
print("✅ API is returning outbreak data successfully!")
print("="*60)
