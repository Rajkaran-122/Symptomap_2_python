"""
Public API endpoint to get all outbreaks including approved doctor submissions
Combines data from both doctor_outbreaks (approved only) and regular outbreaks tables
"""

from fastapi import APIRouter
from typing import List, Dict
import sqlite3
import os
from datetime import datetime, timezone

router = APIRouter(prefix="/outbreaks", tags=["Public Outbreaks"])


def get_db_connection():
    """Get SQLite database connection"""
    # Use correct path relative to app location
    # db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'symptomap.db') # OLD
    db_path = r'c:\Users\digital metro\Documents\sympto-pulse-map-main\backend-python\symptomap.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/all")
async def get_all_outbreaks():
    """
    Get all outbreaks from both APPROVED doctor submissions and regular database
    
    Returns combined list of outbreaks for dashboard display
    Only includes doctor submissions that have been approved by admin
    """
    
    outbreaks = []
    alerts = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
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


@router.get("/pending-count")
async def get_pending_count():
    """Get count of pending submissions for notification badge"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM doctor_outbreaks WHERE status = 'pending' OR status IS NULL")
        row = cursor.fetchone()
        count = row[0] if row else 0
        conn.close()
        return {"pending_count": count}
    except:
        return {"pending_count": 0}

