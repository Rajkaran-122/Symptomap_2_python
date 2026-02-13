import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symptomap.db")
print(f"DB Path: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='doctor_outbreaks';")
    if not cursor.fetchone():
        print("❌ Table 'doctor_outbreaks' NOT FOUND")
        conn.close()
        exit(1)

    print("✅ Table 'doctor_outbreaks' FOUND")

    # 2. Count Total
    cursor.execute("SELECT count(*) FROM doctor_outbreaks")
    total = cursor.fetchone()[0]
    print(f"Total Outbreaks: {total}")

    # 3. Count Approved
    cursor.execute("SELECT count(*) FROM doctor_outbreaks WHERE status='approved'")
    approved = cursor.fetchone()[0]
    print(f"Approved Outbreaks: {approved}")
    
    # 4. Count Alerts
    cursor.execute("SELECT count(*) FROM doctor_alerts")
    alerts = cursor.fetchone()[0]
    print(f"Total Alerts: {alerts}")
    
    if total >= 2000 and approved >= 500:
        print("\nSUCCESS: Data Verification Passed")
    else:
        print("\nFAILURE: Insufficient Data")

    conn.close()

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
