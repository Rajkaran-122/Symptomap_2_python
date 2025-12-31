"""
Add remaining Pune outbreaks via API
Uses direct HTTP POST to the outbreak endpoint
"""

import requests
from datetime import datetime, timedelta, timezone

API_BASE = "http://localhost:8000/api/v1"

# Remaining outbreaks to add
OUTBREAKS = [
    {
        "hospital_name": "KEM Hospital Pune",
        "disease_type": "Dengue",
        "patient_count": 85,
        "severity": "severe",
        "location": {"lat": 18.5314, "lng": 73.8446}
    },
    {
        "hospital_name": "Sahyadri Hospital Pune",
        "disease_type": "Viral Fever",
        "patient_count": 45,
        "severity": "moderate",
        "location": {"lat": 18.5679, "lng": 73.9143}
    },
    {
        "hospital_name": "Jehangir Hospital Pune",
        "disease_type": "Flu",
        "patient_count": 38,
        "severity": "moderate",
        "location": {"lat": 18.5275, "lng": 73.8570}
    },
    {
        "hospital_name": "Aditya Birla Hospital Pune",
        "disease_type": "Flu",
        "patient_count": 18,
        "severity": "mild",
        "location": {"lat": 18.5362, "lng": 73.8988}
    },
]

def add_outbreaks():
    """Add outbreaks via API"""
    print("\n📍 Adding 4 Pune Outbreaks via API...\n")
    
    # Try to get token (if auth is required)
    # For now, we'll try without auth first
    
    severity_icons = {
        "severe": "🔴",
        "moderate": "🟡",
        "mild": "🟢"
    }
    
    added = 0
    for outbreak in OUTBREAKS:
        try:
            # Calculate date_started (2-7 days ago)
            days_ago = 3
            date_started = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
            
            payload = {
                "hospital_name": outbreak["hospital_name"],
                "disease_type": outbreak["disease_type"],
                "patient_count": outbreak["patient_count"],
                "severity": outbreak["severity"],
                "location": outbreak["location"],
                "date_started": date_started
            }
            
            # Try without auth first
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
                print(f"   Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ ERROR   | {outbreak['hospital_name']:35} | {str(e)[:50]}")
    
    print(f"\n✅ Successfully added {added}/{len(OUTBREAKS)} outbreaks")
    
    if added > 0:
        print("\n" + "="*80)
        print("🎉 Pune outbreak data added!")
        print("="*80)
        print(f"\n📍 View the map at http://localhost:5173/")
        print("   Total outbreaks now visible:")
        print("   - 🔴 RED zones (severe)")
        print("   - 🟡 YELLOW zones (moderate)")
        print("   - 🟢 GREEN zones (mild)")
        print("\n")
    else:
        print("\n⚠️  No outbreaks were added. You may need to add them manually via Doctor Station.")
        print("   Go to: http://localhost:5173/admin")

if __name__ == "__main__":
    add_outbreaks()
