import sqlite3
import os

DB_PATH = 'backend-python/symptomap.db'

def approve_requests():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Count pending
        cursor.execute("SELECT count(*) FROM doctor_outbreaks WHERE status='pending'")
        pending_count = cursor.fetchone()[0]
        print(f"Pending requests before: {pending_count}")
        
        if pending_count == 0:
            print("No pending requests to approve.")
            return

        # Approve 5
        cursor.execute("""
            UPDATE doctor_outbreaks 
            SET status='approved' 
            WHERE id IN (
                SELECT id FROM doctor_outbreaks 
                WHERE status='pending' 
                LIMIT 5
            )
        """)
        approved_count = cursor.rowcount
        conn.commit()
        print(f"Successfully approved {approved_count} requests.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    approve_requests()
