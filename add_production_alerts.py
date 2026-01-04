"""
Add alerts to production for Alert Management page
"""

import urllib.request
import json
import random
from datetime import datetime

# Production API URL
API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

# Alerts matching what the user sees locally
ALERTS = [
    {
        "alert_type": "critical",
        "title": "Critical Dengue Outbreak Alert - Delhi",
        "message": "Severe dengue outbreak detected in Delhi NCR region. All healthcare workers are advised to take immediate precautions and report any suspected cases.",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "affected_area": "Delhi",
        "expiry_hours": 72
    },
    {
        "alert_type": "critical",
        "title": "Emergency: Vector Control Teams Deployed",
        "message": "Emergency vector control teams have been deployed to Delhi severe zones. Residents are advised to use mosquito repellents and report standing water.",
        "latitude": 28.6500,
        "longitude": 77.2300,
        "affected_area": "Delhi - Severe Zone",
        "expiry_hours": 48
    },
    {
        "alert_type": "critical",
        "title": "Critical Dengue Outbreak - Immediate Action Required",
        "message": "Hospital capacity reaching critical levels. Additional resources being mobilized. Public advised to avoid outdoor activities during peak mosquito hours.",
        "latitude": 28.5800,
        "longitude": 77.1900,
        "affected_area": "Delhi - Severe Zone",
        "expiry_hours": 24
    },
    {
        "alert_type": "warning",
        "title": "Moderate Viral Fever Cases - Pune",
        "message": "Increasing viral fever cases reported in Pune. Citizens advised to maintain good hygiene and stay hydrated.",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "affected_area": "Pune",
        "expiry_hours": 48
    },
    {
        "alert_type": "critical",
        "title": "Critical Alert: AIIMS Delhi Capacity Critical",
        "message": "AIIMS Delhi reaching 95% capacity due to dengue cases. Patients advised to visit nearby hospitals for non-emergency cases.",
        "latitude": 28.5672,
        "longitude": 77.2100,
        "affected_area": "Delhi - Severe Zone",
        "expiry_hours": 24
    },
    {
        "alert_type": "warning",
        "title": "COVID-19 Monitoring Alert - Bangalore",
        "message": "Slight increase in COVID-19 cases in Bangalore tech corridors. Mask advisory in effect for crowded areas.",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "affected_area": "Bangalore",
        "expiry_hours": 72
    },
    {
        "alert_type": "warning",
        "title": "Moderate Viral Fever Outbreak in Pune",
        "message": "Moderate viral fever cases rising in Pune. Health department conducting awareness camps.",
        "latitude": 18.5300,
        "longitude": 73.8400,
        "affected_area": "Pune - Moderate Zone",
        "expiry_hours": 48
    },
    {
        "alert_type": "info",
        "title": "Flu Season Advisory - Uttarakhand",
        "message": "Seasonal flu increase expected in Uttarakhand. Residents advised to get flu vaccinations.",
        "latitude": 30.0668,
        "longitude": 79.0193,
        "affected_area": "Uttarakhand",
        "expiry_hours": 168
    },
    {
        "alert_type": "warning",
        "title": "COVID-19 Cases Rising in Bangalore",
        "message": "Continued rise in COVID-19 cases in Bangalore. Enhanced testing at key locations.",
        "latitude": 12.9800,
        "longitude": 77.6000,
        "affected_area": "Bangalore - Moderate Zone",
        "expiry_hours": 72
    },
    {
        "alert_type": "info",
        "title": "Disease Surveillance Update - Multi-Zone",
        "message": "Weekly disease surveillance report available. Overall situation stable with no major outbreaks.",
        "latitude": 20.5937,
        "longitude": 78.9629,
        "affected_area": "All Zones",
        "expiry_hours": 168
    },
    {
        "alert_type": "info",
        "title": "Seasonal Flu Outbreak - Uttarakhand",
        "message": "Mild seasonal flu outbreak in Uttarakhand hill regions. Health centers stocked with medications.",
        "latitude": 30.1000,
        "longitude": 79.1000,
        "affected_area": "Uttarakhand - Mild Zone",
        "expiry_hours": 120
    },
    # Additional alerts for more cities
    {
        "alert_type": "critical",
        "title": "Malaria Outbreak Alert - Mumbai",
        "message": "Rising malaria cases in Mumbai slum areas. Fumigation drives underway.",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "affected_area": "Mumbai - Critical Zone",
        "expiry_hours": 48
    },
    {
        "alert_type": "warning",
        "title": "Typhoid Cases Increasing - Kolkata",
        "message": "Typhoid cases increasing due to water contamination in Kolkata. Boil water before drinking.",
        "latitude": 22.5726,
        "longitude": 88.3639,
        "affected_area": "Kolkata",
        "expiry_hours": 72
    },
    {
        "alert_type": "warning",
        "title": "Dengue Alert - Chennai",
        "message": "Dengue cases rising after monsoon in Chennai. Clear stagnant water from surroundings.",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "affected_area": "Chennai",
        "expiry_hours": 48
    },
    {
        "alert_type": "info",
        "title": "Health Camp Announcement - Jaipur",
        "message": "Free health check-up camp in Jaipur SMS Hospital on Jan 5th. All residents welcome.",
        "latitude": 26.9124,
        "longitude": 75.7873,
        "affected_area": "Jaipur",
        "expiry_hours": 120
    }
]

def get_doctor_token():
    """Login and get doctor token"""
    url = f"{API_URL}/doctor/login"
    data = json.dumps({"password": "Doctor@SymptoMap2025"}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode())
        return result.get('access_token')
    except Exception as e:
        print(f"Login error: {e}")
        return None

def submit_alert(token, alert_data):
    """Submit a single alert via API"""
    url = f"{API_URL}/doctor/alert"
    
    data = json.dumps(alert_data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        return True
    except urllib.request.HTTPError as e:
        print(f"Error: {e.code} - {e.read().decode()[:100]}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("🔐 Getting doctor token...")
    token = get_doctor_token()
    
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Token obtained")
    
    print(f"\n🚨 Adding {len(ALERTS)} alerts to production...\n")
    
    success_count = 0
    for i, alert in enumerate(ALERTS):
        if submit_alert(token, alert):
            success_count += 1
            alert_type_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["alert_type"], "⚪")
            print(f"  ✅ [{i+1}/{len(ALERTS)}] {alert_type_emoji} {alert['title'][:50]}...")
        else:
            print(f"  ❌ [{i+1}/{len(ALERTS)}] Failed - {alert['title'][:30]}...")
    
    print(f"\n🎉 Successfully added {success_count}/{len(ALERTS)} alerts!")
    print(f"\n📋 Visit Alert Management:")
    print(f"   https://symptomap-2-python.vercel.app/admin/alerts")

if __name__ == "__main__":
    main()
