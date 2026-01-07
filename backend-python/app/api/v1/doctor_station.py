"""
Doctor Station API Endpoints
Allows doctors to manually submit outbreak data and alerts
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional
from app.api.v1.auth_doctor import verify_token
from app.websocket.manager import manager
import sqlite3
import json

router = APIRouter(prefix="/doctor", tags=["Doctor Station"])


# Pydantic models
class OutbreakSubmission(BaseModel):
    disease_type: str
    patient_count: int
    severity: str  # mild, moderate, severe
    latitude: float
    longitude: float
    location_name: str
    city: str
    state: str
    description: Optional[str] = ""
    date_reported: Optional[str] = None


class AlertSubmission(BaseModel):
    alert_type: str  # warning, critical, info
    title: str
    message: str
    latitude: float
    longitude: float
    affected_area: str
    expiry_hours: int = 24


class SubmissionResponse(BaseModel):
    success: bool
    message: str
    id: Optional[int] = None


# Database helper
def get_db_connection():
    """Get SQLite database connection"""
    from app.core.config import get_sqlite_db_path
    path = get_sqlite_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


@router.post("/outbreak", response_model=SubmissionResponse)
async def submit_outbreak(
    outbreak: OutbreakSubmission,
    payload: dict = Depends(verify_token)
):
    """
    Submit new outbreak report
    
    Requires authentication. Adds outbreak to database.
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_outbreaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                disease_type TEXT NOT NULL,
                patient_count INTEGER NOT NULL,
                severity TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                location_name TEXT,
                city TEXT,
                state TEXT,
                description TEXT,
                date_reported TEXT,
                submitted_by TEXT,
                created_at TEXT
            )
        ''')
        
        # Insert outbreak
        date_reported = outbreak.date_reported or datetime.now(timezone.utc).isoformat()
        
        cursor.execute('''
            INSERT INTO doctor_outbreaks 
            (disease_type, patient_count, severity, latitude, longitude,
             location_name, city, state, description, date_reported, submitted_by, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            outbreak.disease_type,
            outbreak.patient_count,
            outbreak.severity,
            outbreak.latitude,
            outbreak.longitude,
            outbreak.location_name,
            outbreak.city,
            outbreak.state,
            outbreak.description,
            date_reported,
            payload.get("sub", "doctor"),
            datetime.now(timezone.utc).isoformat(),
            'pending'  # New submissions require admin approval
        ))
        
        outbreak_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # BROADCAST TO ALL CONNECTED CLIENTS (non-blocking)
        try:
            await manager.broadcast({
                "type": "NEW_OUTBREAK",
                "data": {
                    "id": outbreak_id,
                    "disease": outbreak.disease_type,
                    "cases": outbreak.patient_count,
                    "severity": outbreak.severity,
                    "location": {
                        "name": outbreak.location_name,
                        "city": outbreak.city,
                        "state": outbreak.state,
                        "latitude": outbreak.latitude,
                        "longitude": outbreak.longitude
                    },
                    "description": outbreak.description,
                    "date_reported": date_reported
                }
            })
        except Exception as ws_err:
            print(f"WebSocket broadcast warning (non-fatal): {ws_err}")
        
        return SubmissionResponse(
            success=True,
            message=f"Outbreak report submitted successfully",
            id=outbreak_id
        )
    
    except Exception as e:
        import traceback
        print(f"ERROR in submit_outbreak: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to submit outbreak: {str(e)}")


@router.post("/alert", response_model=SubmissionResponse)
async def submit_alert(
    alert: AlertSubmission,
    payload: dict = Depends(verify_token)
):
    """
    Submit new alert
    
    Requires authentication. Creates new alert in database.
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctor_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                affected_area TEXT,
                expiry_date TEXT,
                submitted_by TEXT,
                created_at TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Calculate expiry
        from datetime import timedelta
        expiry_date = (datetime.now(timezone.utc) + timedelta(hours=alert.expiry_hours)).isoformat()
        
        # Insert alert
        cursor.execute('''
            INSERT INTO doctor_alerts 
            (alert_type, title, message, latitude, longitude, affected_area,
             expiry_date, submitted_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.alert_type,
            alert.title,
            alert.message,
            alert.latitude,
            alert.longitude,
            alert.affected_area,
            expiry_date,
            payload.get("sub", "doctor"),
            datetime.now(timezone.utc).isoformat()
        ))
        
        alert_id = cursor.lastrowid
        conn.commit()
        
        # Also insert into main alerts table for Alert Management Page visibility
        try:
            import uuid
            import json
            
            # Map valid severity from alert_type

            severity = alert.alert_type.lower()
            if severity not in ['critical', 'warning', 'info']:
                severity = 'info'
                
            alert_uuid = str(uuid.uuid4())
            recipients_json = json.dumps({"emails": ["admin@symptomap.com"]}) # Default recipient
            delivery_status_json = json.dumps({"email": "pending"})
            acknowledged_json = json.dumps([])
            
            # Ensure alerts table exists (it should, but just in case)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    prediction_id TEXT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    zone_name TEXT,
                    recipients TEXT,
                    sent_at TEXT,
                    delivery_status TEXT,
                    acknowledged_by TEXT,
                    expires_at TEXT
                )
            ''')
            
            cursor.execute('''
                INSERT INTO alerts (id, alert_type, severity, title, message, zone_name, 
                                   recipients, delivery_status, acknowledged_by, sent_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                alert_uuid,
                alert.alert_type,
                severity,
                alert.title,
                alert.message,
                alert.affected_area,
                recipients_json,
                delivery_status_json,
                acknowledged_json,
                datetime.now(timezone.utc).isoformat()
            ))
            conn.commit()
            print(f"DEBUG: Successfully synced alert {alert_uuid} to main 'alerts' table")
        except Exception as sync_err:
            print(f"⚠️ Failed to sync alert to main table: {sync_err}")

        conn.close()
        
        # BROADCAST TO ALL CONNECTED CLIENTS (non-blocking)
        try:
            await manager.broadcast({
                "type": "NEW_ALERT",
                "data": {
                    "id": alert_id,
                    "alert_type": alert.alert_type,
                    "title": alert.title,
                    "message": alert.message,
                    "location": {
                        "latitude": alert.latitude,
                        "longitude": alert.longitude,
                        "area": alert.affected_area
                    },
                    "expiry": expiry_date
                }
            })
        except Exception as ws_err:
            print(f"WebSocket broadcast warning (non-fatal): {ws_err}")
        
        return SubmissionResponse(
            success=True,
            message=f"Alert created successfully",
            id=alert_id
        )
    
    except Exception as e:
        import traceback
        print(f"ERROR in submit_alert: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")


@router.get("/submissions")
async def get_submissions(
    limit: int = 50,
    payload: dict = Depends(verify_token)
):
    """
    Get list of doctor submissions
    
    Returns recent outbreak reports and alerts submitted by doctors
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get outbreaks
        cursor.execute('''
            SELECT * FROM doctor_outbreaks 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        outbreaks = []
        for row in cursor.fetchall():
            outbreaks.append(dict(row))
        
        # Get alerts
        cursor.execute('''
            SELECT * FROM doctor_alerts 
            WHERE status = 'active'
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append(dict(row))
        
        conn.close()
        
        return {
            "outbreaks": outbreaks,
            "alerts": alerts,
            "total_outbreaks": len(outbreaks),
            "total_alerts": len(alerts)
        }
    
    except Exception as e:
        # If tables don't exist yet, return empty
        return {
            "outbreaks": [],
            "alerts": [],
            "total_outbreaks": 0,
            "total_alerts": 0
        }


@router.get("/stats")
async def get_doctor_stats(payload: dict = Depends(verify_token)):
    """
    Get statistics for doctor dashboard
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count outbreaks - FIX: Store fetchone() result before accessing
        cursor.execute('SELECT COUNT(*) as count FROM doctor_outbreaks')
        outbreak_row = cursor.fetchone()
        outbreak_count = outbreak_row['count'] if outbreak_row else 0
        
        # Count alerts - FIX: Store fetchone() result before accessing
        cursor.execute('SELECT COUNT(*) as count FROM doctor_alerts WHERE status = "active"')
        alert_row = cursor.fetchone()
        alert_count = alert_row['count'] if alert_row else 0
        
        conn.close()
        
        print(f"DEBUG: Outbreak count: {outbreak_count}, Alert count: {alert_count}")  # Debug logging
        
        return {
            "total_submissions": outbreak_count + alert_count,
            "outbreak_reports": outbreak_count,
            "active_alerts": alert_count
        }
    
    except Exception as e:
        print(f"ERROR in get_doctor_stats: {e}")  # Error logging
        return {
            "total_submissions": 0,
            "outbreak_reports": 0,
            "active_alerts": 0
        }
