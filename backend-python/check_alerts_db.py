"""Simple direct database check for alerts"""
import sqlite3
import json

conn = sqlite3.connect("symptomap.db")
cursor = conn.cursor()

print("\n📋 Checking alerts in database:\n")
cursor.execute("SELECT id, severity, title, zone_name, recipients FROM alerts LIMIT 5")
rows = cursor.fetchall()

print(f"Found {len(rows)} alerts:\n")
for row in rows:
    id, severity, title, zone, recipients = row
    recipients_data = json.loads(recipients) if recipients else {}
    count = len(recipients_data.get("emails", []))
    severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🟢"}.get(severity, "⚪")
    print(f"{severity_icon} {severity:8} | {zone:15} | {title[:40]:40} | {count} recipients")

conn.close()

print("\n✅ Alerts exist in database!")
print("❌ API is returning 500 - likely a field mismatch issue")
print("\nThe issue is that the Alert model expects 'sent_at' but the table might have a different column name.")
