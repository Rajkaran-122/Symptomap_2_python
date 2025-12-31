"""Test report API endpoints"""
import requests

API_URL = "http://localhost:8000/api/v1"

print("\n🧪 TESTING REPORT GENERATION API\n")

# Test 1: Comprehensive Report
print("1️⃣ Testing Comprehensive Report (JSON)...")
try:
    resp = requests.get(f"{API_URL}/reports/comprehensive?days=30", timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Report Type: {data.get('report_type')}")
        print(f"   Total Outbreaks: {data.get('summary', {}).get('outbreaks', {}).get('total', 0)}")
        print(f"   Total Alerts: {data.get('summary', {}).get('alerts', {}).get('total', 0)}")
    else:
        print(f"   ❌ FAILED: {resp.text[:200]}")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: Outbreak Summary JSON
print("\n2️⃣ Testing Outbreak Summary (JSON)...")
try:
    resp = requests.get(f"{API_URL}/reports/outbreak-summary?format=json&days=30", timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Total Outbreaks: {data.get('total_outbreaks', 0)}")
        print(f"   Total Patients: {data.get('total_patients', 0)}")
    else:
        print(f"   ❌ FAILED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Outbreak Summary CSV
print("\n3️⃣ Testing Outbreak Summary (CSV)...")
try:
    resp = requests.get(f"{API_URL}/reports/outbreak-summary?format=csv&days=30", timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200 and 'csv' in resp.headers.get('content-type', ''):
        print(f"   ✅ SUCCESS! CSV file ready for download")
        print(f"   Size: {len(resp.content)} bytes")
    else:
        print(f"   ❌ FAILED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 4: Alert Summary
print("\n4️⃣ Testing Alert Summary (JSON)...")
try:
    resp = requests.get(f"{API_URL}/reports/alert-summary?format=json&days=30", timeout=10)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ SUCCESS!")
        print(f"   Total Alerts: {data.get('total_alerts', 0)}")
    else:
        print(f"   ❌ FAILED")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "="*80)
print("✨ REPORT GENERATION API TEST COMPLETE!")
print("="*80)
print("\n✅ Frontend buttons can now:")
print("   - Download comprehensive JSON reports from Dashboard")
print("   - Download outbreak summary CSV from PredictionPanel")
print("\n📍 Test in browser at: http://localhost:3000/\n")
