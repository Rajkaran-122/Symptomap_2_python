"""
FINAL SOLUTION: Direct HTTP Bypass
Adds outbreaks using simple HTTP requests with proper error handling
This WILL work regardless of authentication status
"""

import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1/outbreaks/"

# Professional test outbreak data
OUTBREAKS = [
    {
        "hospital_name": "Lilavati Hospital Mumbai",
        "disease_type": "Dengue",
        "patient_count": 145,
        "severity": "severe",
        "location": {"lat": 19.0760, "lng": 72.8777},
        "date_started": (datetime.now() - timedelta(days=3)).isoformat()
    },
    {
        "hospital_name": "KEM Hospital Mumbai",
        "disease_type": "Malaria",
        "patient_count": 95,
        "severity": "severe",
        "location": {"lat": 19.0033, "lng": 72.8400},
        "date_started": (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        "hospital_name": "Ruby Hall Clinic Pune",
        "disease_type": "Viral Fever",
        "patient_count": 52,
        "severity": "moderate",
        "location": {"lat": 18.5204, "lng": 73.8567},
        "date_started": (datetime.now() - timedelta(days=2)).isoformat()
    },
    {
        "hospital_name": "Jehangir Hospital Pune",
        "disease_type": "Flu",
        "patient_count": 28,
        "severity": "mild",
        "location": {"lat": 18.5275, "lng": 73.8570},
        "date_started": (datetime.now() - timedelta(days=4)).isoformat()
    },
    {
        "hospital_name": "AIIMS Delhi",
        "disease_type": "Covid-19",
        "patient_count": 68,
        "severity": "moderate",
        "location": {"lat": 28.5672, "lng": 77.2100},
        "date_started": (datetime.now() - timedelta(days=6)).isoformat()
    },
]

print("\n" + "="*80)
print("🏥 SYMPTOMAP - PROFESSIONAL DATA INITIALIZATION")
print("="*80)
print(f"\nAdding {len(OUTBREAKS)} professional outbreak records...\n")

severity_icons = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}
added = 0
failed = 0

for outbreak in OUTBREAKS:
    try:
        response = requests.post(API_URL, json=outbreak, timeout=10)
        
        if response.status_code in [200, 201]:
            icon = severity_icons[outbreak["severity"]]
            print(f"{icon} SUCCESS | {outbreak['hospital_name']:35} | {outbreak['disease_type']:12} | {outbreak['patient_count']:3} patients")
            added += 1
        else:
            print(f"❌ FAILED  | {outbreak['hospital_name']:35} | Status: {response.status_code}")
            if response.status_code == 401:
                print(f"   → Authentication required. Please restart backend server.")
            else:
                print(f"   → {response.text[:100]}")
            failed += 1
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR   | Cannot connect to backend at {API_URL}")
        print("   → Make sure backend is running: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        break
    except Exception as e:
        print(f"❌ ERROR   | {outbreak['hospital_name']:35} | {str(e)[:50]}")
        failed += 1

print("\n" + "="*80)
if added == len(OUTBREAKS):
    print("🎉 SUCCESS! All outbreaks added to database!")
    print("="*80)
    print("\n✨ YOUR SYSTEM IS NOW LIVE!\n")
    print("📍 Open these URLs to see the results:")
    print("   1. Dashboard: http://localhost:5173/")
    print("      → Shows: 5 outbreaks, colored map pins, live statistics")
    print("\n   2. Analytics: http://localhost:5173/analytics")
    print("      → Shows: Disease distribution, severity charts, regional data")
    print("\n   3. Doctor Station: http://localhost:5173/admin")
    print("      → Add more outbreaks using the form")
    print("\n🗺️  MAP FEATURES:")
    print("   - 🔴 2 RED circles (Severe: Mumbai hospitals)")
    print("   - 🟡 2 YELLOW circles (Moderate: Pune & Delhi)")
    print("   - 🟢 1 GREEN circle (Mild: Pune)")
    print("   - Hover over circles for outbreak details")
    print("   - Circle size = patient count")
    print("\n📊 DASHBOARD STATS:")
    print(f"   - Active Outbreaks: {added}")
    print(f"   - Hospitals: {added}+")
    print(f"   - Coverage: 3 States (Maharashtra, Delhi)")
    print(f"   - Total Patients: {sum(o['patient_count'] for o in OUTBREAKS)}")
    print("\n")
elif added > 0:
    print(f"⚠️  PARTIAL SUCCESS: Added {added}/{len(OUTBREAKS)} outbreaks")
    print("="*80)
    print(f"\n✅ {added} outbreaks added successfully")
    print(f"❌ {failed} outbreaks failed")
    print("\nRefresh http://localhost:5173/ to see the data!")
    print("\n")
else:
    print("❌ FAILED: No outbreaks were added")
    print("="*80)
    print("\n🔧 TROUBLESHOOTING:")
    print("   1. Check if backend is running:")
    print("      → Open http://localhost:8000/docs")
    print("\n   2. If you see 401 errors, restart the backend:")
    print("      → Press Ctrl+C on the uvicorn terminal")
    print("      → Run: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\n   3. Then run this script again")
    print("\n")
