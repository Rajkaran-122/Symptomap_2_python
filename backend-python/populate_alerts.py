"""
Populate database with sample alerts
"""
import sqlite3
from datetime import datetime, timedelta, timezone
import json
import uuid

DB_PATH = "symptomap.db"

print("\n🔔 POPULATING SAMPLE ALERTS\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get user
cursor.execute("SELECT id FROM users LIMIT 1")
user_row = cursor.fetchone()
if not user_row:
    print("❌ No user found")
    exit(1)
user_id = user_row[0]

# Sample alerts for different zones
alerts_data = [
    {
        "title": "Critical Dengue Outbreak Alert - Delhi",
        "message": "Severe dengue outbreak detected in Delhi with 570+ confirmed cases across 5 hospitals. Immediate action recommended.",
        "zone_name": "Delhi",
        "severity": "critical",
        "alert_type": "outbreak",
        "recipients": ["health.delhi@gov.in", "who.india@who.int", "epidemic@health.gov.in"],
        "days_ago": 0
    },
    {
        "title": "Moderate Viral Fever Cases - Pune",
        "message": "Increased viral fever cases reported in Pune area. 246 patients under observation across 4 facilities.",
        "zone_name": "Pune",
        "severity": "warning",
        "alert_type": "outbreak",
        "recipients": ["health.pune@gov.in", "district.health@maharashtra.gov.in"],
        "days_ago": 1
    },
    {
        "title": "COVID-19 Monitoring Alert - Bangalore",
        "message": "Moderate rise in COVID-19 cases in Bangalore. 233 active cases requiring monitoring.",
        "zone_name": "Bangalore",
        "severity": "warning",
        "alert_type": "monitoring",
        "recipients": ["health.bangalore@gov.in", "karnataka.health@gov.in"],
        "days_ago": 2
    },
    {
        "title": "Flu Season Advisory - Uttarakhand",
        "message": "Mild seasonal flu outbreak in Dehradun region. Prevention measures advised for 85 reported cases.",
        "zone_name": "Uttarakhand",
        "severity": "info",
        "alert_type": "advisory",
        "recipients": ["health.dehradun@gov.in", "uttarakhand.health@gov.in"],
        "days_ago": 3
    },
    {
        "title": "Disease Surveillance Update - Multi-Zone",
        "message": "Weekly disease surveillance report: 1,134 total cases across 4 zones. Situation under control.",
        "zone_name": "All Zones",
        "severity": "info",
        "alert_type": "report",
        "recipients": ["central.health@gov.in", "surveillance@nicpr.res.in"],
        "days_ago": 5
    }
]

for alert in alerts_data:
    alert_id = str(uuid.uuid4())
    sent_at = (datetime.now(timezone.utc) - timedelta(days=alert["days_ago"])).isoformat()
    
    recipients_json = json.dumps({"emails": alert["recipients"]})
    delivery_status_json = json.dumps({"email": "sent"})
    acknowledged_by_json = json.dumps([]) if alert["severity"] != "info" else json.dumps([
        {
            "user_id": user_id,
            "user_name": "Admin User",
            "timestamp": sent_at
        }
    ])
    
    cursor.execute("""
        INSERT INTO alerts 
        (id, alert_type, severity, title, message, zone_name, recipients, 
         delivery_status, acknowledged_by, sent_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        alert_id,
        alert["alert_type"],
        alert["severity"],
        alert["title"],
        alert["message"],
        alert["zone_name"],
        recipients_json,
        delivery_status_json,
        acknowledged_by_json,
        sent_at
    ))
    
    severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}[alert["severity"]]
    print(f"{severity_icon} {alert['title'][:50]:50} | {len(alert['recipients'])} recipients")

conn.commit()
conn.close()

print(f"\n✅ Successfully added {len(alerts_data)} sample alerts!")
print("\n" + "="*80)
print("🔔 ALERT SYSTEM POPULATED!")
print("="*80)
print("\nAlert Summary:")
print(f"  Total Alerts: {len(alerts_data)}")
print(f"  Critical: {sum(1 for a in alerts_data if a['severity'] == 'critical')}")
print(f"  Warnings: {sum(1 for a in alerts_data if a['severity'] == 'warning')}")
print(f"  Info: {sum(1 for a in alerts_data if a['severity'] == 'info')}")
print(f"  Sent Today: {sum(1 for a in alerts_data if a['days_ago'] == 0)}")
print(f"\n📍 View at: http://localhost:3000/alerts\n")

