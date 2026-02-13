import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symptomap.db")
print(f"DB Path: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables:")
    table_names = [t[0] for t in tables]
    for t in table_names:
        print(f"- {t}")
    
    if "doctor_outbreaks" in table_names:
        print("\n✅ doctor_outbreaks exists!")
    else:
        print("\n❌ doctor_outbreaks MISSING!")

    conn.close()
except Exception as e:
    print(f"Error: {e}")
