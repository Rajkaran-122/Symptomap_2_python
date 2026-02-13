"""
Alert routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.outbreak import Alert, Prediction
from app.models.user import User
from app.api.v1.auth import get_current_user
from app.services.alert_service import AlertService


router = APIRouter(prefix="/alerts", tags=["Alerts"])


class SendAlertRequest(BaseModel):
    prediction_id: Optional[str] = None
    alert_type: str
    severity: str  # info, warning, critical
    title: str
    message: str
    zone_name: str
    recipient_emails: List[str]


@router.post("/send")
async def send_alert(
    request: SendAlertRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send alert to recipients (admin/public health official only)"""
    
    if current_user.role not in ["admin", "public_health_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and public health officials can send alerts"
        )
    
    # Get prediction details if provided
    prediction_data = None
    if request.prediction_id:
        result = await db.execute(
            select(Prediction).where(Prediction.id == request.prediction_id)
        )
        prediction = result.scalar_one_or_none()
        if prediction:
            prediction_data = {
                "disease": prediction.disease_type,
                "predicted_cases": prediction.predicted_cases,
                "risk_level": prediction.risk_level
            }
    
    # Prepare alert data for email
    alert_data = {
        "title": request.title,
        "message": request.message,
        "zone_name": request.zone_name,
        "severity": request.severity,
        "disease": prediction_data.get("disease") if prediction_data else "Unknown",
        "predicted_cases": prediction_data.get("predicted_cases") if prediction_data else "N/A",
        "risk_level": prediction_data.get("risk_level") if prediction_data else "N/A",
        "dashboard_link": "http://localhost:3000/dashboard"  # TODO: Make configurable
    }
    
   # Send alert
    alert_service = AlertService()
    delivery_result = await alert_service.send_outbreak_alert(
        recipients=request.recipient_emails,
        alert_data=alert_data
    )
    
    # Save alert to database
    alert = Alert(
        prediction_id=request.prediction_id,
        alert_type=request.alert_type,
        severity=request.severity,
        title=request.title,
        message=request.message,
        zone_name=request.zone_name,
        recipients={"emails": request.recipient_emails},
        delivery_status={"email": delivery_result["status"]},
        acknowledged_by=[]
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return {
        "alert_id": str(alert.id),
        "delivery_status": delivery_result,
        "recipients_count": len(request.recipient_emails),
        "message": "Alert sent successfully"
    }


@router.get("/")
async def list_alerts(
    severity: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List alerts with filters - using raw SQL"""
    from sqlalchemy import text
    import json as json_lib
    
    # Use raw SQL to avoid ORM mapping issues
    print(f"DEBUG: Fetching alerts list from DB...")
    sql = """
        SELECT id, alert_type, severity, title, zone_name, sent_at, 
               recipients, delivery_status, acknowledged_by
        FROM alerts
    """
    
    if severity:
        sql += f" WHERE severity = :severity"
        sql += " ORDER BY sent_at DESC LIMIT :limit"
        result = await db.execute(text(sql), {"severity": severity, "limit": limit})
    else:
        sql += " ORDER BY sent_at DESC LIMIT :limit"
        result = await db.execute(text(sql), {"limit": limit})
    
    rows = result.fetchall()
    
    alerts_list = []
    for row in rows:
        try:
            recipients_data = json_lib.loads(row[6]) if row[6] else {"emails": []}
        except:
            recipients_data = {"emails": []}
            
        try:
            acknowledged_data = json_lib.loads(row[8]) if row[8] else []
        except:
            acknowledged_data = []

        try:
            delivery_status = json_lib.loads(row[7]) if row[7] else {"email": "sent"}
        except:
            delivery_status = {"email": "sent"}
        
        alerts_list.append({
            "id": str(row[0]),
            "alert_type": row[1],
            "severity": row[2],
            "title": row[3],
            "zone_name": row[4],
            "sent_at": row[5],
            "recipients_count": len(recipients_data.get("emails", [])) if isinstance(recipients_data, dict) else 0,
            "delivery_status": delivery_status,
            "acknowledged_count": len(acknowledged_data) if isinstance(acknowledged_data, list) else 0
        })
    
    return alerts_list


@router.get("/{alert_id}")
async def get_alert_detail(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get single alert details for View modal"""
    from sqlalchemy import text
    import json as json_lib
    
    sql = """
        SELECT id, alert_type, severity, title, message, zone_name, sent_at, 
               recipients, delivery_status, acknowledged_by
        FROM alerts
        WHERE id = :alert_id
    """
    
    result = await db.execute(text(sql), {"alert_id": alert_id})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    try:
        recipients_data = json_lib.loads(row[7]) if row[7] else {"emails": []}
    except:
        recipients_data = {"emails": []}
        
    try:
        acknowledged_data = json_lib.loads(row[9]) if row[9] else []
    except:
        acknowledged_data = []

    try:
        delivery_status = json_lib.loads(row[8]) if row[8] else {"email": "sent"}
    except:
        delivery_status = {"email": "sent"}
    
    return {
        "id": str(row[0]),
        "alert_type": row[1],
        "severity": row[2],
        "title": row[3],
        "message": row[4],
        "zone_name": row[5],
        "sent_at": row[6],
        "recipients": recipients_data.get("emails", []) if isinstance(recipients_data, dict) else [],
        "delivery_status": delivery_status,
        "acknowledged_by": acknowledged_data
    }


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an alert"""
    
    result = await db.execute(
        select(Alert).where(Alert.id == alert_id)
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Add acknowledgment
    if alert.acknowledged_by is None:
        alert.acknowledged_by = []
    
    alert.acknowledged_by.append({
        "user_id": str(current_user.id),
        "user_name": current_user.full_name,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    await db.commit()
    
    return {
        "message": "Alert acknowledged successfully",
        "alert_id": str(alert.id),
        "acknowledged_by": current_user.full_name
    }


@router.post("/{alert_id}/acknowledge-public")
async def acknowledge_alert_public(
    alert_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge an alert - public endpoint (no auth required)"""
    from sqlalchemy import text
    import json as json_lib
    
    # Get current acknowledgments
    sql = "SELECT acknowledged_by FROM alerts WHERE id = :alert_id"
    result = await db.execute(text(sql), {"alert_id": alert_id})
    row = result.fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    try:
        acknowledged_list = json_lib.loads(row[0]) if row[0] else []
    except:
        acknowledged_list = []
    
    # Add new acknowledgment
    acknowledged_list.append({
        "user_id": "dashboard_user",
        "user_name": "Dashboard User",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Update in database
    update_sql = "UPDATE alerts SET acknowledged_by = :acknowledged WHERE id = :alert_id"
    await db.execute(text(update_sql), {
        "acknowledged": json_lib.dumps(acknowledged_list),
        "alert_id": alert_id
    })
    await db.commit()
    
    return {
        "message": "Alert acknowledged successfully",
        "alert_id": alert_id,
        "acknowledged": True
    }


@router.post("/generate")
async def generate_auto_alerts(
    db: AsyncSession = Depends(get_db)
):
    """
    Auto-generate alerts based on current outbreak data and predictions
    Can be called manually or via scheduled task
    """
    from app.services.alert_generator import run_auto_alert_generation
    
    try:
        result = await run_auto_alert_generation(db)
        return {
            "success": True,
            "message": f"Generated {result['total_generated']} new alerts",
            "alerts": result
        }
    except Exception as e:
        import traceback
        print(f"Error generating alerts: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"Error: {str(e)}",
            "alerts": {"outbreak_alerts": [], "growth_alerts": [], "total_generated": 0}
        }


@router.get("/active")
async def get_active_alerts(
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get currently active alerts"""
    from sqlalchemy import text
    import json as json_lib
    
    sql = """
        SELECT id, alert_type, severity, title, zone_name, sent_at, message
        FROM alerts
        WHERE (acknowledged_by IS NULL OR acknowledged_by = '[]')
        ORDER BY sent_at DESC
        LIMIT :limit
    """
    
    result = await db.execute(text(sql), {"limit": limit})
    rows = result.fetchall()
    
    return [
        {
            "id": str(row[0]),
            "alert_type": row[1],
            "severity": row[2],
            "title": row[3],
            "zone_name": row[4],
            "sent_at": row[5],
            "message": row[6]
        }
        for row in rows
    ]
