
import sqlite3
import uuid
import random
import json
from datetime import datetime, timedelta

# Path to DB
DB_PATH = "backend-python/symptomap.db"

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get admin user
    cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
    admin = cursor.fetchone()
    admin_id = admin[0] if admin else str(uuid.uuid4())

    regions = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad"]
    diseases = ["Viral Fever", "Dengue", "Malaria", "COVID-19", "Flu", "Cholera"]
    severities = ["info", "warning", "critical", "emergency"]

    # Helper for dynamic insert
    def dynamic_insert(table, data):
        columns = data.keys()
        placeholders = [":" + col for col in columns]
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, data)

    print(f"Seeding 20 broadcasts...")
    for i in range(20):
        region = random.choice(regions) if random.random() > 0.3 else None
        dynamic_insert("broadcasts", {
            "id": str(uuid.uuid4()),
            "title": f"Health Alert {i+1}: {random.choice(diseases)} Update",
            "content": f"This is a sample broadcast message for {region if region else 'Global'} regarding {random.choice(diseases)} precautions and awareness.",
            "severity": random.choice(severities),
            "region": region,
            "channels": json.dumps(["app", "email"]),
            "created_by": admin_id,
            "is_active": 1,
            "is_automated": random.randint(0, 1),
            "created_at": (datetime.utcnow() - timedelta(days=random.randint(0, 5))).isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=random.randint(1, 10))).isoformat()
        })

    print(f"Seeding 10 alerts...")
    for i in range(10):
        dynamic_insert("alerts", {
            "id": str(uuid.uuid4()).replace("-", ""), # Some IDs are CHAR(32) without hyphens
            "alert_type": "outbreak_detection",
            "severity": random.choice(["warning", "critical"]),
            "title": f"New Outbreak Alert in {random.choice(regions)}",
            "message": f"A sudden increase in {random.choice(diseases)} cases has been detected.",
            "zone_name": random.choice(regions),
            "recipients_count": random.randint(50, 500),
            "delivery_status": json.dumps({"email": "sent", "sms": "pending"}),
            "sent_at": (datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat(),
            "created_by": admin_id
        })

    conn.commit()
    conn.close()
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed_data()
