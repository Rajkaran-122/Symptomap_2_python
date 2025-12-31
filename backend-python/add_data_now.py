"""
Create outbreak data directly via the POST /outbreaks/ endpoint
"""
import requests
from datetime import datetime, timedelta, timezone

API_BASE = "http://localhost:8000/api/v1"

# Sample outbreaks for testing
OUTBREAKS = [
    {
        "hospital_name": "Lilavati Hospital Mumbai",
        "disease_type": "Dengue",
        "patient_count": 145,
        "severity": "severe",
        "location": {"lat": 19.0760, "lng": 72.8777}
    },
    {
        "hospital_name": "KEM Hospital Mumbai",
        "disease_type": "Malaria",
        "patient_count": 95,
        "severity": "severe",
        "location": {"lat": 19.0033, "lng": 72.8400}
    },
    {
        "hospital_name": "Ruby Hall Clinic Pune",
        "disease_type": "Viral Fever",
        "patient_count": 52,
        "severity": "moderate",
        "location": {"lat": 18.5204, "lng": 73.8567}
    },
    {
        "hospital_name": "Jehangir Hospital Pune",
        "disease_type": "Flu",
        "patient_count": 28,
        "severity": "mild",
        "location": {"lat": 18.5275, "lng": 73.8570}
    },
    {
        "hospital_name": "AIIMS Delhi",
        "disease_type": "Covid-19",
        "patient_count": 68,
        "severity": "moderate",
        "location": {"lat": 28.5672, "lng": 77.2100}
    },
]

print("\n🔧 Adding Outbreak Data via POST API...\n")

severity_icons = {"severe": "🔴", "moderate": "🟡", "mild": "🟢"}
added = 0

for outbreak in OUTBREAKS:
    try:
        # Calculate date_started (3 days ago)
        date_started = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
        
        payload = {
            "hospital_name": outbreak["hospital_name"],
            "disease_type": outbreak["disease_type"],
            "patient_count": outbreak["patient_count"],
            "severity": outbreak["severity"],
            "location": outbreak["location"],
            "date_started": date_started,
            "symptoms": ["Fever", "Fatigue", "Body Ache"],
            "notes": f"{outbreak['severity'].upper()} outbreak"
        }
        
        response = requests.post(
            f"{API_BASE}/outbreaks/",
            json=payload,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            icon = severity_icons[outbreak["severity"]]
            print(f"{icon} SUCCESS | {outbreak['hospital_name']:35} | {outbreak['disease_type']:15} | {outbreak['patient_count']:3} patients")
            added += 1
        else:
            print(f"❌ FAILED  | {outbreak['hospital_name']:35} | Status: {response.status_code}")
            if response.status_code != 500:
                print(f"   Error: {response.text[:150]}")
                
    except Exception as e:
        print(f"❌ ERROR   | {outbreak['hospital_name']:35} | {str(e)[:50]}")

print(f"\n✅ Successfully added {added}/{len(OUTBREAKS)} outbreaks")

if added > 0:
    print("\n" + "="*80)
    print("🎉 Outbreak data added successfully!")
    print("="*80)
    print(f"\n📍 Refresh http://localhost:5173/ to see the data!")
    print(f"   Dashboard should now show {added} outbreaks instead of 0")
    print(f"   Map should display colored markers:")
    print(f"   - 🔴 RED zones (severe)")
    print(f"   - 🟡 YELLOW zones (moderate)")
    print(f"   - 🟢 GREEN zones (mild)\n")
else:
    print("\n⚠️  No outbreaks were added successfully.\n")
