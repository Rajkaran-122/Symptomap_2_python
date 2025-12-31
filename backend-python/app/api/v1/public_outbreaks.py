"""
Public API endpoint to get all outbreaks including doctor submissions
Combines data from both doctor_outbreaks and regular outbreaks tables
"""

from fastapi import APIRouter
from typing import List, Dict
import sqlite3
from datetime import datetime, timezone

router = APIRouter(prefix="/outbreaks", tags=["Public Outbreaks"])


def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect('../symptomap.db')
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/all")
async def get_all_outbreaks():
    """
    Get all outbreaks from both doctor submissions and regular database
    
    Returns combined list of outbreaks for dashboard display
    """
    
    outbreaks = []
    alerts = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get doctor submissions with better error handling
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
                    created_at
                FROM doctor_outbreaks
                ORDER BY created_at DESC
            ''')
            
            rows = cursor.fetchall()
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
                        "source": "Doctor Submission",
                        "status": "active"
                    }
                    outbreaks.append(outbreak_data)
                except Exception as row_error:
                    print(f"Error processing outbreak row: {row_error}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching doctor outbreaks: {e}")
        
        # Get doctor alerts with better error handling
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
    
    # Always return a valid response
    return {
        "outbreaks": outbreaks,
        "alerts": alerts,
        "total_outbreaks": len(outbreaks),
        "total_alerts": len(alerts),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
