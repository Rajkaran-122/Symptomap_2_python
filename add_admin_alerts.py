"""
Add alerts to production via /api/v1/alerts/send endpoint
Requires admin user authentication
"""

import urllib.request
import json
from datetime import datetime

API_URL = "https://symptomap-2-python-1.onrender.com/api/v1"

# Alert data matching local
ALERTS = [
    {"severity": "critical", "title": "Critical Dengue Outbreak Alert - Delhi", "zone_name": "Delhi", "message": "Severe dengue outbreak detected. All healthcare workers advised to take immediate precautions.", "alert_type": "email", "recipient_emails": ["admin@symptomap.com", "heath@delhi.gov.in", "doctor@example.com"]},
    {"severity": "critical", "title": "Emergency: Vector Control Teams Deployed", "zone_name": "Delhi - Severe Zone", "message": "Emergency vector control teams deployed. Residents advised to use mosquito repellents.", "alert_type": "email", "recipient_emails": []},
    {"severity": "critical", "title": "Critical Dengue Outbreak - Immediate Action Required", "zone_name": "Delhi - Severe Zone", "message": "Hospital capacity reaching critical levels. Public advised to avoid outdoor activities during peak mosquito hours.", "alert_type": "email", "recipient_emails": []},
    {"severity": "warning", "title": "Moderate Viral Fever Cases - Pune", "zone_name": "Pune", "message": "Increasing viral fever cases reported. Citizens advised to maintain good hygiene.", "alert_type": "email", "recipient_emails": ["pune@health.gov.in", "docs@pune.com"]},
    {"severity": "critical", "title": "Critical Alert: AIIMS Delhi Capacity Critical", "zone_name": "Delhi - Severe Zone", "message": "AIIMS Delhi reaching 95% capacity. Patients advised to visit nearby hospitals for non-emergency cases.", "alert_type": "email", "recipient_emails": []},
    {"severity": "warning", "title": "COVID-19 Monitoring Alert - Bangalore", "zone_name": "Bangalore", "message": "Slight increase in COVID-19 cases in Bangalore tech corridors. Mask advisory in effect.", "alert_type": "email", "recipient_emails": ["blr@health.gov.in", "admin@blr.gov.in"]},
    {"severity": "warning", "title": "Moderate Viral Fever Outbreak in Pune", "zone_name": "Pune - Moderate Zone", "message": "Moderate viral fever cases rising. Health department conducting awareness camps.", "alert_type": "email", "recipient_emails": []},
    {"severity": "info", "title": "Flu Season Advisory - Uttarakhand", "zone_name": "Uttarakhand", "message": "Seasonal flu increase expected. Residents advised to get flu vaccinations.", "alert_type": "email", "recipient_emails": ["uk@health.gov.in", "uttarakhand@nha.gov.in"]},
    {"severity": "warning", "title": "COVID-19 Cases Rising in Bangalore", "zone_name": "Bangalore - Moderate Zone", "message": "Continued rise in COVID-19 cases. Enhanced testing at key locations.", "alert_type": "email", "recipient_emails": []},
    {"severity": "info", "title": "Disease Surveillance Update - Multi-Zone", "zone_name": "All Zones", "message": "Weekly disease surveillance report available. Overall situation stable.", "alert_type": "email", "recipient_emails": ["national@nha.gov.in", "surveillance@health.gov.in"]},
    {"severity": "info", "title": "Seasonal Flu Outbreak - Uttarakhand", "zone_name": "Uttarakhand - Mild Zone", "message": "Mild seasonal flu outbreak in hill regions. Health centers stocked with medications.", "alert_type": "email", "recipient_emails": []},
]

def get_admin_token():
    """Login with admin credentials"""
    url = f"{API_URL}/auth/login"
    data = json.dumps({
        "email": "admin@symptomap.com",
        "password": "Admin@123"
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        result = json.loads(response.read().decode())
        return result.get('access_token')
    except urllib.request.HTTPError as e:
        print(f"Admin login error: {e.code}")
        error_body = e.read().decode()
        print(f"Error: {error_body[:200]}")
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def send_alert(token, alert_data):
    """Send alert via API"""
    url = f"{API_URL}/alerts/send"
    
    data = json.dumps(alert_data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', f'Bearer {token}')
    
    try:
        response = urllib.request.urlopen(req, timeout=30)
        return True, ""
    except urllib.request.HTTPError as e:
        error = e.read().decode()[:100]
        return False, error
    except Exception as e:
        return False, str(e)

def main():
    print("🔐 Getting admin token...")
    token = get_admin_token()
    
    if not token:
        print("❌ Failed to get admin token. Trying to check existing alerts...")
        # Just check what's on production
        try:
            req = urllib.request.Request(f"{API_URL}/alerts/")
            data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
            print(f"\n📋 Current alerts on production: {len(data)}")
            for i, a in enumerate(data[:5]):
                print(f"  {i+1}. [{a.get('severity')}] {a.get('title', 'untitled')[:40]}")
        except Exception as e:
            print(f"Error fetching alerts: {e}")
        return
    
    print(f"✅ Admin token obtained")
    
    print(f"\n🚨 Sending {len(ALERTS)} alerts...\n")
    
    success_count = 0
    for i, alert in enumerate(ALERTS):
        success, error = send_alert(token, alert)
        emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(alert["severity"], "⚪")
        
        if success:
            success_count += 1
            print(f"  ✅ [{i+1}/{len(ALERTS)}] {emoji} {alert['title'][:45]}...")
        else:
            print(f"  ❌ [{i+1}/{len(ALERTS)}] {emoji} {alert['title'][:30]}... - {error[:50]}")
    
    print(f"\n🎉 Sent {success_count}/{len(ALERTS)} alerts!")
    print(f"\n📋 Visit Alert Management:")
    print(f"   https://symptomap-2-python.vercel.app/admin/alerts")

if __name__ == "__main__":
    main()
