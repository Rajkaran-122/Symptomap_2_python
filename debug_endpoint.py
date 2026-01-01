import sys
import os
import asyncio
import sqlite3
from datetime import datetime, timezone

# Mimic app imports if needed, or just copy function logic
# Logic from public_outbreaks.py

def get_db_connection():
    db_path = r'c:\Users\digital metro\Documents\sympto-pulse-map-main\backend-python\symptomap.db'
    print(f"Connecting to {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

async def get_all_outbreaks():
    outbreaks = []
    alerts = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Querying doctor_outbreaks...")
        # Get APPROVED doctor submissions only
        try:
            cursor.execute("SELECT * FROM doctor_outbreaks")
            all_rows = cursor.fetchall()
            print(f"Total rows in table: {len(all_rows)}")
            if len(all_rows) > 0:
                print(f"First row status: '{all_rows[0]['status']}'")

            cursor.execute('''
                SELECT 
                    id, disease_type, patient_count, severity, latitude, longitude, 
                    location_name, city, state, description, date_reported, created_at, status
                FROM doctor_outbreaks
                WHERE LOWER(status) = 'approved'
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            print(f"Approved rows found: {len(rows)}")
            
            for row in rows:
                try:
                    outbreak_data = {
                        "id": f"doc_{row['id']}",
                        "disease": str(row['disease_type']),
                        "cases": int(row['patient_count']),
                        # ... minimal mapping ...
                        "status": "approved"
                    }
                    outbreaks.append(outbreak_data)
                except Exception as row_error:
                    print(f"Error row: {row_error}")
                    continue
                    
        except Exception as e:
            print(f"Error query: {e}")
            import traceback
            traceback.print_exc()

        conn.close()
        
    except Exception as e:
        print(f"DB Error: {e}")
        
    # Check return construction
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        print(f"Time: {now_iso}")
    except Exception as e:
        print(f"Time error: {e}")

    return {"count": len(outbreaks)}

if __name__ == "__main__":
    asyncio.run(get_all_outbreaks())
