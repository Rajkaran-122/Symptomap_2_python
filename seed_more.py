
import sqlite3
import uuid
import random
import json
from datetime import datetime, timedelta

DB_PATH = "backend-python/symptomap.db"

def seed_more_alerts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get cols for alerts
    cursor.execute("PRAGMA table_info(alerts)")
    alerts_info = cursor.fetchall()
    alerts_cols = [r[1] for r in alerts_info]

    # Get admin
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    admin = cursor.fetchone()
    admin_id = admin[0] if admin else str(uuid.uuid4())

    regions = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad"]
    diseases = ["Viral Fever", "Dengue", "Malaria", "COVID-19", "Flu", "Cholera"]
    
    def get_defaults(table_info):
        defaults = {}
        for row in table_info:
            name = row[1]
            typ = row[2].upper()
            notnull = row[3]
            dflt = row[4]
            if notnull and dflt is None:
                if "VARCHAR" in typ or "TEXT" in typ or "CHAR" in typ:
                    defaults[name] = ""
                elif "INT" in typ or "BOOL" in typ:
                    defaults[name] = 0
                elif "JSON" in typ:
                    defaults[name] = "{}"
                elif "DATETIME" in typ:
                    defaults[name] = datetime.utcnow().isoformat()
        return defaults

    alert_defaults = get_defaults(alerts_info)

    def safe_insert(table, cols, defaults, data):
        final_data = defaults.copy()
        final_data.update(data)
        to_insert = {k: v for k, v in final_data.items() if k in cols}
        columns = to_insert.keys()
        placeholders = [":" + col for col in columns]
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, to_insert)

    print("Seeding 9 more alerts to reach 20...")
    for i in range(9):
        safe_insert("alerts", alerts_cols, alert_defaults, {
            "id": str(uuid.uuid4()).replace("-", ""),
            "alert_type": "automated_outbreak",
            "severity": random.choice(["warning", "critical"]),
            "title": f"Regional Alert: {random.choice(diseases)} Spike",
            "message": f"Detection of increased {random.choice(diseases)} activity in {random.choice(regions)}.",
            "zone_name": random.choice(regions),
            "recipients_count": random.randint(100, 500),
            "sent_at": datetime.utcnow().isoformat(),
            "created_by": admin_id
        })
    
    conn.commit()
    conn.close()
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_more_alerts()
