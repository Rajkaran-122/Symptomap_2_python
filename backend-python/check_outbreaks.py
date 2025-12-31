"""
Check what's in the database for outbreaks
"""
import sqlite3
import json

DB_PATH = "symptomap.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n📊 OUTBREAK DATA CHECK\n")

# Get all outbreaks with details
cursor.execute("""
    SELECT o.id, o.disease_type, o.patient_count, o.severity, 
           o.location, h.name as hospital_name
    FROM outbreaks o
    JOIN hospitals h ON o.hospital_id = h.id
    LIMIT 5
""")

rows = cursor.fetchall()

print(f"Total outbreaks: {len(rows)}\n")

for row in rows:
    print(f"ID: {row[0][:8]}...")
    print(f"  Disease: {row[1]}")
    print(f"  Patients: {row[2]}")
    print(f"  Severity: {row[3]}")
    print(f"  Location (raw): {row[4]}")
    print(f"  Hospital: {row[5]}")
    print()

# Check location data type
cursor.execute("SELECT typeof(location), location FROM outbreaks LIMIT 1")
result = cursor.fetchone()
if result:
    print(f"Location data type: {result[0]}")
    print(f"Location value: {result[1]}")

conn.close()
