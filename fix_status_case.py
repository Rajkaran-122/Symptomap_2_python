import sqlite3
import os

db_path = 'backend-python/symptomap.db'

def fix():
    if not os.path.exists(db_path):
        print("DB not found")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Check current statuses
        c.execute("SELECT status, count(*) FROM doctor_outbreaks GROUP BY status")
        print("Current statuses:", c.fetchall())
        
        # Update 'Approved' to 'approved'
        c.execute("UPDATE doctor_outbreaks SET status = 'approved' WHERE status = 'Approved'")
        print(f"Updated {c.rowcount} rows to 'approved'")
        
        # Check again
        c.execute("SELECT status, count(*) FROM doctor_outbreaks GROUP BY status")
        print("New statuses:", c.fetchall())
        
        conn.commit()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix()
