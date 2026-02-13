
import sqlite3
import uuid
import random
import json
from datetime import datetime, timedelta

DB_PATH = "backend-python/symptomap.db"

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get cols and info
    cursor.execute("PRAGMA table_info(alerts)")
    alerts_info = cursor.fetchall()
    alerts_cols = [r[1] for r in alerts_info]
    
    cursor.execute("PRAGMA table_info(broadcasts)")
    broadcasts_info = cursor.fetchall()
    broadcasts_cols = [r[1] for r in broadcasts_info]

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
    broadcast_defaults = get_defaults(broadcasts_info)

    def safe_insert(table, cols, defaults, data):
        final_data = defaults.copy()
        final_data.update(data)
        # Only keep keys that actually exist in the table
        to_insert = {k: v for k, v in final_data.items() if k in cols}
        columns = to_insert.keys()
        placeholders = [":" + col for col in columns]
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, to_insert)

    print("Seeding...")
    for i in range(20):
        safe_insert("broadcasts", broadcasts_cols, broadcast_defaults, {
            "id": str(uuid.uuid4()),
            "title": f"Health Alert {i+1}: {random.choice(diseases)} Update",
            "content": f"Critical update on {random.choice(diseases)} prevention.",
            "severity": random.choice(["info", "warning", "critical"]),
            "region": random.choice(regions),
            "channels": '["app"]',
            "created_by": admin_id,
            "is_active": 1,
            "is_automated": 0
        })
    
    for i in range(10):
        safe_insert("alerts", alerts_cols, alert_defaults, {
            "id": str(uuid.uuid4()).replace("-", ""),
            "alert_type": "manual_seed",
            "severity": "warning",
            "title": f"Outbreak Alert {i+1}",
            "message": f"Increase in {random.choice(diseases)} cases reported.",
            "zone_name": random.choice(regions),
            "recipients_count": random.randint(100, 1000),
            "acknowledged_count": 0,
            "delivery_status": '{"email": "sent"}',
            "created_by": admin_id
        })
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    seed()
