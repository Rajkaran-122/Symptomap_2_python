"""
Test alerts API
"""
import requests

print("\n🔍 Testing Alerts API...\n")

try:
    response = requests.get("http://localhost:8000/api/v1/alerts/", timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS! Returned {len(data)} alerts\n")
        
        if len(data) > 0:
            print("Alerts Summary:")
            for alert in data:
                severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(alert["severity"], "⚪")
                print(f"  {severity_icon} {alert['severity']:8} | {alert['zone_name']:15} | {alert['title'][:50]}")
            
            # Stats
            critical = sum(1 for a in data if a["severity"] == "critical")
            warnings = sum(1 for a in data if a["severity"] == "warning")
            info = sum(1 for a in data if a["severity"] == "info")
            total_recipients = sum(a.get("recipients_count", 0) for a in data)
            
            print(f"\n📊 Statistics:")
            print(f"   Total Alerts: {len(data)}")
            print(f"   Critical: {critical}")
            print(f"   Warnings: {warnings}")
            print(f"   Info: {info}")
            print(f"   Total Recipients: {total_recipients}")
            print(f"\n✨ Alert Management is WORKING!")
            print(f"\n📍 View at: http://localhost:3000/alerts\n")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")
