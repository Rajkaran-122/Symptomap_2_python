"""
COMPREHENSIVE TEST DATA - Multiple Colored Zones Across India
This creates outbreaks in different cities with varying severity levels
"""

import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1/outbreaks/"

# Comprehensive outbreak data across India with different severity zones
OUTBREAKS = [
    # RED ZONES (Severe - 90+ patients)
    {
        "hospital_name": "Lilavati Hospital Mumbai",
        "disease_type": "Dengue",
        "patient_count": 145,
        "severity": "severe",
        "location": {"lat": 19.0760, "lng": 72.8777},
        "date_started": (datetime.now() - timedelta(days=3)).isoformat(),
        "zone": "🔴 RED"
    },
    {
        "hospital_name": "KEM Hospital Mumbai",
        "disease_type": "Malaria",
        "patient_count": 95,
        "severity": "severe",
        "location": {"lat": 19.0033, "lng": 72.8400},
        "date_started": (datetime.now() - timedelta(days=5)).isoformat(),
        "zone": "🔴 RED"
    },
    {
        "hospital_name": "AIIMS Delhi",
        "disease_type": "Covid-19",
        "patient_count": 120,
        "severity": "severe",
        "location": {"lat": 28.5672, "lng": 77.2100},
        "date_started": (datetime.now() - timedelta(days=4)).isoformat(),
        "zone": "🔴 RED"
    },
    {
        "hospital_name": "Fortis Bangalore",
        "disease_type": "Typhoid",
        "patient_count": 105,
        "severity": "severe",
        "location": {"lat": 12.9716, "lng": 77.5946},
        "date_started": (datetime.now() - timedelta(days=6)).isoformat(),
        "zone": "🔴 RED"
    },
    
    # YELLOW ZONES (Moderate - 30-89 patients)
    {
        "hospital_name": "Ruby Hall Clinic Pune",
        "disease_type": "Viral Fever",
        "patient_count": 52,
        "severity": "moderate",
        "location": {"lat": 18.5204, "lng": 73.8567},
        "date_started": (datetime.now() - timedelta(days=2)).isoformat(),
        "zone": "🟡 YELLOW"
    },
    {
        "hospital_name": "Apollo Hospital Chennai",
        "disease_type": "Influenza",
        "patient_count": 68,
        "severity": "moderate",
        "location": {"lat": 13.0827, "lng": 80.2707},
        "date_started": (datetime.now() - timedelta(days=3)).isoformat(),
        "zone": "🟡 YELLOW"
    },
    {
        "hospital_name": "Medanta Gurgaon",
        "disease_type": "Gastroenteritis",
        "patient_count": 45,
        "severity": "moderate",
        "location": {"lat": 28.4595, "lng": 77.0266},
        "date_started": (datetime.now() - timedelta(days=1)).isoformat(),
        "zone": "🟡 YELLOW"
    },
    {
        "hospital_name": "Tata Memorial Mumbai",
        "disease_type": "Respiratory Infection",
        "patient_count": 38,
        "severity": "moderate",
        "location": {"lat": 19.0144, "lng": 72.8479},
        "date_started": (datetime.now() - timedelta(days=2)).isoformat(),
        "zone": "🟡 YELLOW"
    },
    
    # GREEN ZONES (Mild - <30 patients)
    {
        "hospital_name": "Jehangir Hospital Pune",
        "disease_type": "Flu",
        "patient_count": 28,
        "severity": "mild",
        "location": {"lat": 18.5275, "lng": 73.8570},
        "date_started": (datetime.now() - timedelta(days=4)).isoformat(),
        "zone": "🟢 GREEN"
    },
    {
        "hospital_name": "AMRI Hospital Kolkata",
        "disease_type": "Common Cold",
        "patient_count": 22,
        "severity": "mild",
        "location": {"lat": 22.5726, "lng": 88.3639},
        "date_started": (datetime.now() - timedelta(days=1)).isoformat(),
        "zone": "🟢 GREEN"
    },
    {
        "hospital_name": "Manipal Hospital Bangalore",
        "disease_type": "Seasonal Allergies",
        "patient_count": 15,
        "severity": "mild",
        "location": {"lat": 12.9141, "lng": 77.6101},
        "date_started": (datetime.now() - timedelta(days=2)).isoformat(),
        "zone": "🟢 GREEN"
    },
]

print("\n" + "="*80)
print("🏥 SYMPTOMAP - COMPREHENSIVE MULTI-ZONE DATA INSERTION")
print("="*80)
print(f"\nAdding {len(OUTBREAKS)} outbreaks across India...")
print("\nZone Distribution:")
print("  🔴 RED Zones (Severe):    4 outbreaks")
print("  🟡 YELLOW Zones (Moderate): 4 outbreaks") 
print("  🟢 GREEN Zones (Mild):    3 outbreaks")
print("\nCities Covered:")
print("  - Mumbai (3 outbreaks)")
print("  - Delhi/Gurgaon (2 outbreaks)")
print("  - Pune (2 outbreaks)")
print("  - Bangalore (2 outbreaks)")
print("  - Chennai (1 outbreak)")
print("  - Kolkata (1 outbreak)")
print("\n" + "="*80 + "\n")

added = 0
failed = 0
results_by_zone = {"🔴 RED": 0, "🟡 YELLOW": 0, "🟢 GREEN": 0}

for outbreak in OUTBREAKS:
    zone_type = outbreak.pop("zone")  # Remove zone from payload
    
    try:
        response = requests.post(API_URL, json=outbreak, timeout=10)
        
        if response.status_code in [200, 201]:
            print(f"{zone_type:10} | {outbreak['hospital_name']:35} | {outbreak['disease_type']:20} | {outbreak['patient_count']:3} patients | {outbreak['severity']:8}")
            added += 1
            results_by_zone[zone_type] += 1
        else:
            print(f"❌ FAILED  | {outbreak['hospital_name']:35} | Status: {response.status_code}")
            if response.status_code == 401:
                print(f"   → Server needs restart (authentication required)")
            else:
                print(f"   → {response.text[:80]}")
            failed += 1
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: Cannot connect to backend at {API_URL}")
        print("   → Make sure backend is running")
        break
    except Exception as e:
        print(f"❌ ERROR   | {outbreak['hospital_name']:35} | {str(e)[:50]}")
        failed += 1

print("\n" + "="*80)
if added == len(OUTBREAKS):
    print("🎉 SUCCESS! All outbreaks added to database!")
    print("="*80)
    print("\n📊 ZONE BREAKDOWN:")
    print(f"  🔴 RED Zones: {results_by_zone['🔴 RED']} severe outbreaks")
    print(f"  🟡 YELLOW Zones: {results_by_zone['🟡 YELLOW']} moderate outbreaks")
    print(f"  🟢 GREEN Zones: {results_by_zone['🟢 GREEN']} mild outbreaks")
    print(f"\n  Total: {added} outbreak zones across India")
    
    print("\n🗺️  MAP VISUALIZATION:")
    print("  Open http://localhost:5173/ to see:")
    print("  - 4 RED circles (Mumbai x2, Delhi, Bangalore)")
    print("  - 4 YELLOW circles (Pune, Chennai, Gurgaon, Mumbai)")
    print("  - 3 GREEN circles (Pune, Kolkata, Bangalore)")
    print("  - Map auto-zooms to show all zones across India")
    
    print("\n📈 DASHBOARD STATS:")
    print(f"  - Active Outbreaks: {added}")
    print(f"  - Hospitals: {added}+")
    print(f"  - Coverage: 6 Cities, 5 States")
    print(f"  - Total Patients: {sum(o['patient_count'] for o in OUTBREAKS)}")
    print(f"  - High Risk Zones: {results_by_zone['🔴 RED']}")
    
    print("\n✅ VERIFICATION:")
    print("  1. Dashboard: http://localhost:5173/")
    print("  2. Analytics: http://localhost:5173/analytics - See disease distribution")
    print("  3. Admin: http://localhost:5173/admin - List of all outbreaks")
    print("\n")
    
elif added > 0:
    print(f"⚠️  PARTIAL SUCCESS: Added {added}/{len(OUTBREAKS)} outbreaks")
    print("="*80)
    print(f"\n✅ {added} outbreaks added successfully")
    print(f"❌ {failed} outbreaks failed")
    if results_by_zone['🔴 RED'] > 0:
        print(f"\n🔴 RED Zones: {results_by_zone['🔴 RED']} added")
    if results_by_zone['🟡 YELLOW'] > 0:
        print(f"🟡 YELLOW Zones: {results_by_zone['🟡 YELLOW']} added")
    if results_by_zone['🟢 GREEN'] > 0:
        print(f"🟢 GREEN Zones: {results_by_zone['🟢 GREEN']} added")
    print("\nRefresh http://localhost:5173/ to see the data!")
    print("\n")
else:
    print("❌ FAILED: No outbreaks were added")
    print("="*80)
    print("\n🔧 TROUBLESHOOTING:")
    print("   1. Server status:")
    print("      → Check: http://localhost:8000/docs")
    print("\n   2. If 401 errors, restart backend:")
    print("      → Press Ctrl+C in uvicorn terminal")
    print("      → Run: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\n   3. Then run this script again:")
    print("      → python add_comprehensive_data.py")
    print("\n")

# Verify database
print("="*80)
print("🔍 VERIFYING DATABASE...")
print("="*80)
try:
    response = requests.get("http://localhost:8000/api/v1/outbreaks/")
    if response.status_code == 200:
        db_outbreaks = response.json()
        print(f"\n✅ Database verification successful!")
        print(f"   Total outbreaks in database: {len(db_outbreaks)}")
        
        if len(db_outbreaks) > 0:
            print(f"\n   Latest outbreak:")
            latest = db_outbreaks[0]
            print(f"   - Hospital: {latest.get('hospital', {}).get('name', 'N/A')}")
            print(f"   - Disease: {latest.get('disease_type', 'N/A')}")
            print(f"   - Patients: {latest.get('patient_count', 0)}")
            print(f"   - Severity: {latest.get('severity', 'N/A')}")
    else:
        print(f"\n❌ Database verification failed (Status: {response.status_code})")
except Exception as e:
    print(f"\n❌ Cannot verify database: {e}")

print("\n" + "="*80 + "\n")
