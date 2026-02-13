import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symptomap.db")
print(f"DB Path: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Dropping tables...")
    cursor.execute("DROP TABLE IF EXISTS doctor_outbreaks;")
    cursor.execute("DROP TABLE IF EXISTS doctor_alerts;")
    
    conn.commit()
    print("✅ Tables dropped.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
