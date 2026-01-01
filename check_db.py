import sqlite3
import os

db_path = 'backend-python/symptomap.db'

def check():
    if not os.path.exists(db_path):
        print("DB not found")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        c.execute("SELECT count(*) FROM outbreaks")
        print(f"Official Outbreaks: {c.fetchone()[0]}")
        
        c.execute("SELECT count(*) FROM doctor_outbreaks")
        print(f"Doctor Outbreaks: {c.fetchone()[0]}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check()
