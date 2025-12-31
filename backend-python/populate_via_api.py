"""
Simple script to populate outbreak data via API
"""
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

print("\n🔧 Populating Database via API...\n")

# Call the admin initialization endpoint
try:
    response = requests.post(f"{API_BASE}/admin/initialize-demo-data", timeout=30)
    
    if response.status_code in [200, 201]:
        data = response.json()
        print(f"✅ SUCCESS!")
        print(f"   Message: {data.get('message', 'N/A')}")
        print(f"   Outbreaks added: {data.get('outbreaks_added', 0)}")
        print(f"\n📊 Demo Data Summary:")
        for outbreak in data.get('outbreaks', []):
            severity_icon = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}.get(outbreak['severity'], "⚪")
            print(f"   {severity_icon} {outbreak['severity'].upper():8} | {outbreak['hospital']:35} | {outbreak['disease']:12} | {outbreak['patients']:3} patients")
        
        print(f"\n\n🎉 Database populated successfully!")
        print(f"📍 Open http://localhost:5173/ to see the data on the dashboard\n")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
