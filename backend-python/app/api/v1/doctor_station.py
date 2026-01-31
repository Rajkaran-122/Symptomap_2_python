"""
Doctor Station API Endpoints
Allows doctors to manually submit outbreak data and alerts
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.doctor import DoctorOutbreak, DoctorAlert, DoctorOutbreak as DoctorOutbreakModel, DoctorAlert as DoctorAlertModel
from app.websocket.manager import manager
from app.utils.sanitizer import sanitize_html
from app.core.audit import log_audit_event
from datetime import datetime, timezone, timedelta
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
    
    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        return sanitize_html(v)


class AlertSubmission(BaseModel):
    alert_type: str  # warning, critical, info
    title: str
    message: str
    latitude: float
    longitude: float
    affected_area: str
    expiry_hours: int = 24
    
    @field_validator('title', 'message', 'affected_area')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        return sanitize_html(v)



class SubmissionResponse(BaseModel):
    success: bool
    message: str
    id: Optional[int] = None





@router.post("/outbreak", response_model=SubmissionResponse)
async def submit_outbreak(
    request: Request,
    outbreak: OutbreakSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit new outbreak report
    
    Requires authentication. Adds outbreak to database.
    """
    
    try:
        # Create outbreak record
        date_reported = None
        if outbreak.date_reported:
             try:
                 date_reported = datetime.fromisoformat(outbreak.date_reported.replace('Z', '+00:00'))
             except:
                 date_reported = datetime.now(timezone.utc)
        else:
             date_reported = datetime.now(timezone.utc)

        new_outbreak = DoctorOutbreakModel(
            disease_type=outbreak.disease_type,
            patient_count=outbreak.patient_count,
            severity=outbreak.severity,
            latitude=outbreak.latitude,
            longitude=outbreak.longitude,
            location_name=outbreak.location_name,
            city=outbreak.city,
            state=outbreak.state,
            description=outbreak.description,
            date_reported=date_reported,
            submitted_by=str(current_user.id),
            status='pending'
        )
        
        db.add(new_outbreak)
        await db.commit()
        await db.refresh(new_outbreak)
        
        outbreak_id = new_outbreak.id
        
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
                    "date_reported": date_reported.isoformat()
                }
            })
        except Exception as ws_err:
            print(f"WebSocket broadcast warning (non-fatal): {ws_err}")
            
        # AUDIT LOG
        log_audit_event(
            event="OUTBREAK_SUBMITTED",
            actor_id=str(current_user.id),
            actor_role=current_user.role,
            ip_address=request.client.host if request.client else "unknown",
            status="SUCCESS",
            metadata={"outbreak_id": outbreak_id, "disease": outbreak.disease_type, "severity": outbreak.severity}
        )
        
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
    request: Request,
    alert: AlertSubmission,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit new alert
    
    Requires authentication. Creates new alert in database.
    """
    
    try:
        # Calculate expiry
        expiry_date = datetime.now(timezone.utc) + timedelta(hours=alert.expiry_hours)
        
        new_alert = DoctorAlertModel(
            alert_type=alert.alert_type,
            title=alert.title,
            message=alert.message,
            latitude=alert.latitude,
            longitude=alert.longitude,
            affected_area=alert.affected_area,
            expiry_date=expiry_date,
            created_at=datetime.now(timezone.utc),
            status='active'
        )
        
        db.add(new_alert)
        await db.commit()
        await db.refresh(new_alert)
        
        alert_id = new_alert.id
        
        # Also insert into main alerts table for Alert Management Page visibility
        try:
            import uuid
            from app.models.outbreak import Alert
            
            # Map valid severity from alert_type
            severity = alert.alert_type.lower()
            if severity not in ['critical', 'warning', 'info']:
                severity = 'info'
            
            # Map alert_type to a valid severity for the main alerts table if needed
            # The Alert model expects severity to be one of info, warning, critical. 
            # alert_type in DoctorAlert is essentially severity.
                
            main_alert = Alert(
                id=uuid.uuid4(),
                alert_type=alert.alert_type, 
                severity=severity,
                title=alert.title,
                message=alert.message,
                zone_name=alert.affected_area,
                recipients=["admin@symptomap.com"], # JSONB list
                delivery_status={"email": "pending"},
                acknowledged_by=[],
                sent_at=datetime.now(timezone.utc)
            )
            
            db.add(main_alert)
            await db.commit()
            print(f"DEBUG: Successfully synced alert {main_alert.id} to main 'alerts' table")
        except Exception as sync_err:
            import traceback
            print(f"⚠️ Failed to sync alert to main table: {sync_err}")
            print(traceback.format_exc())

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
                    "expiry": expiry_date.isoformat()
                }
            })
        except Exception as ws_err:
            print(f"WebSocket broadcast warning (non-fatal): {ws_err}")
            
        # AUDIT LOG
        log_audit_event(
            event="ALERT_SUBMITTED",
            actor_id=str(current_user.id),
            actor_role=current_user.role,
            ip_address=request.client.host if request.client else "unknown",
            status="SUCCESS",
            metadata={"alert_id": alert_id, "type": alert.alert_type, "title": alert.title}
        )
        
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of doctor submissions
    
    Returns recent outbreak reports and alerts submitted by doctors
    """
    
    try:
        # Get outbreaks
        outbreaks_result = await db.execute(
            select(DoctorOutbreakModel)
            .order_by(desc(DoctorOutbreakModel.created_at))
            .limit(limit)
        )
        outbreaks = [o.__dict__ for o in outbreaks_result.scalars().all()]
        
        # Get alerts
        alerts_result = await db.execute(
            select(DoctorAlertModel)
            .where(DoctorAlertModel.status == 'active')
            .order_by(desc(DoctorAlertModel.created_at))
            .limit(limit)
        )
        alerts = [a.__dict__ for a in alerts_result.scalars().all()]
        
        return {
            "outbreaks": outbreaks,
            "alerts": alerts,
            "total_outbreaks": len(outbreaks),
            "total_alerts": len(alerts)
        }
    
    except Exception as e:
        import traceback
        print(f"ERROR in get_submissions: {traceback.format_exc()}")
        # If tables don't exist yet, return empty
        return {
            "outbreaks": [],
            "alerts": [],
            "total_outbreaks": 0,
            "total_alerts": 0
        }


@router.get("/stats")
async def get_doctor_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for doctor dashboard
    """
    
    try:
        # Count outbreaks
        outbreak_result = await db.execute(select(func.count()).select_from(DoctorOutbreakModel))
        outbreak_count = outbreak_result.scalar() or 0
        
        # Count alerts
        alert_result = await db.execute(
             select(func.count())
             .select_from(DoctorAlertModel)
             .where(DoctorAlertModel.status == 'active')
        )
        alert_count = alert_result.scalar() or 0
        
        print(f"DEBUG: Outbreak count: {outbreak_count}, Alert count: {alert_count}")
        
        return {
            "total_submissions": outbreak_count + alert_count,
            "outbreak_reports": outbreak_count,
            "active_alerts": alert_count
        }
    
    except Exception as e:
        print(f"ERROR in get_doctor_stats: {e}")
        return {
            "total_submissions": 0,
            "outbreak_reports": 0,
            "active_alerts": 0
        }
