
import sqlite3
import uuid
import random
import json
from datetime import datetime, timedelta

DB_PATH = "backend-python/symptomap.db"

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    def get_cols(table):
        cursor.execute(f"PRAGMA table_info({table})")
        return [row[1] for row in c.fetchall()]

    # Alternative check
    cursor.execute("SELECT * FROM alerts LIMIT 1")
    cols_alerts = [description[0] for description in cursor.description]
    print("REAL ALERTS COLS:", cols_alerts)

    cursor.execute("SELECT * FROM broadcasts LIMIT 1")
    cols_broadcasts = [description[0] for description in cursor.description]
    print("REAL BROADCASTS COLS:", cols_broadcasts)

    # Get admin
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    admin = cursor.fetchone()
    admin_id = admin[0] if admin else str(uuid.uuid4())

    regions = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad"]
    diseases = ["Viral Fever", "Dengue", "Malaria", "COVID-19", "Flu", "Cholera"]
    
    def safe_insert(table, cols, data):
        data_to_insert = {k: v for k, v in data.items() if k in cols}
        columns = data_to_insert.keys()
        placeholders = [":" + col for col in columns]
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, data_to_insert)

    print("Seeding...")
    for i in range(20):
        safe_insert("broadcasts", cols_broadcasts, {
            "id": str(uuid.uuid4()),
            "title": f"Health Alert {i+1}: {random.choice(diseases)} Update",
            "content": f"Update on {random.choice(diseases)} outbreak in regional zones.",
            "severity": random.choice(["info", "warning", "critical"]),
            "region": random.choice(regions),
            "channels": '["app"]',
            "created_by": admin_id,
            "is_active": 1,
            "created_at": datetime.utcnow().isoformat()
        })
    
    for i in range(10):
        safe_insert("alerts", cols_alerts, {
            "id": str(uuid.uuid4()).replace("-", ""),
            "alert_type": "manual",
            "severity": "warning",
            "title": f"Test Alert {i+1}",
            "message": "This is a test notification.",
            "zone_name": random.choice(regions),
            "recipients_count": 100,
            "sent_at": datetime.utcnow().isoformat(),
            "created_by": admin_id
        })
    
    conn.commit()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    seed()
