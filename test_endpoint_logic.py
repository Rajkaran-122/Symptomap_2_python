
import sqlite3
import os
from datetime import datetime, timezone

def get_db_connection():
    # Use correct path relative to app location
    # backend-python/symptomap.db
    db_path = os.path.join(os.getcwd(), 'backend-python', 'symptomap.db')
    print(f"DB Path: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def test_logic():
    outbreaks = []
    alerts = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Fetching outbreaks...")
        # Get APPROVED doctor submissions only
        try:
            cursor.execute('''
                SELECT 
                    id,
                    disease_type,
                    patient_count,
                    severity,
                    latitude,
                    longitude,
                    location_name,
                    city,
                    state,
                    description,
                    date_reported,
                    created_at,
                    status
                FROM doctor_outbreaks
                WHERE status = 'approved'
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            print(f"Found {len(rows)} outbreaks")
            for row in rows:
                try:
                    outbreak_data = {
                        "id": f"doc_{row['id']}",
                        "disease": str(row['disease_type']),
                        "cases": int(row['patient_count']),
                        "severity": str(row['severity']),
                        "location": {
                            "name": str(row['location_name']) if row['location_name'] else "",
                            "city": str(row['city']) if row['city'] else "",
                            "state": str(row['state']) if row['state'] else "",
                            "latitude": float(row['latitude']) if row['latitude'] else 0.0,
                            "longitude": float(row['longitude']) if row['longitude'] else 0.0
                        },
                        "description": str(row['description']) if row['description'] else "",
                        "reported_date": str(row['date_reported']) if row['date_reported'] else str(row['created_at']),
                        "source": "Doctor Submission (Approved)",
                        "status": "approved",
                        "verified": True
                    }
                    outbreaks.append(outbreak_data)
                except Exception as row_error:
                    print(f"Error processing outbreak row: {row_error}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching approved doctor outbreaks: {e}")
        
        print("Fetching alerts...")
        # Get active doctor alerts
        try:
            cursor.execute('''
                SELECT 
                    id,
                    alert_type,
                    title,
                    message,
                    latitude,
                    longitude,
                    affected_area,
                    expiry_date,
                    created_at,
                    status
                FROM doctor_alerts
                WHERE status = 'active'
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
            print(f"Found {len(rows)} alerts")
            for row in rows:
                try:
                    alert_data = {
                        "id": f"alert_{row['id']}",
                        "type": str(row['alert_type']),
                        "title": str(row['title']),
                        "message": str(row['message']),
                        "location": {
                            "latitude": float(row['latitude']) if row['latitude'] else 0.0,
                            "longitude": float(row['longitude']) if row['longitude'] else 0.0,
                            "area": str(row['affected_area']) if row['affected_area'] else ""
                        },
                        "expiry": str(row['expiry_date']) if row['expiry_date'] else "",
                        "created": str(row['created_at']) if row['created_at'] else "",
                        "status": str(row['status'])
                    }
                    alerts.append(alert_data)
                except Exception as row_error:
                    print(f"Error processing alert row: {row_error}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching doctor alerts: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"Database connection error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"Total Outbreaks: {len(outbreaks)}")
    print(f"Total Alerts: {len(alerts)}")

if __name__ == "__main__":
    test_logic()
