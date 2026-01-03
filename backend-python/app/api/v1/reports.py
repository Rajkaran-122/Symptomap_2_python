"""
Report Generation API
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone, timedelta
from typing import Optional
import json
import io
import csv
import sqlite3

from app.core.database import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/outbreak-summary")
async def generate_outbreak_summary_report(
    format: str = "json",  # json, csv
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Generate outbreak summary report"""
    
    # Get outbreak statistics
    sql = """
        SELECT 
            o.disease_type,
            o.severity,
            COUNT(*) as outbreak_count,
            SUM(o.patient_count) as total_patients,
            h.city,
            h.state
        FROM outbreaks o
        JOIN hospitals h ON o.hospital_id = h.id
        WHERE o.date_reported >= :start_date
        GROUP BY o.disease_type, o.severity, h.city, h.state
        ORDER BY total_patients DESC
    """
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    result = await db.execute(text(sql), {"start_date": start_date})
    rows = result.fetchall()
    
    data = []
    for row in rows:
        data.append({
            "disease_type": row[0],
            "severity": row[1],
            "outbreak_count": row[2],
            "total_patients": row[3],
            "city": row[4],
            "state": row[5]
        })
    
    if format == "csv":
        # Generate CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["disease_type", "severity", "outbreak_count", "total_patients", "city", "state"])
        writer.writeheader()
        writer.writerows(data)
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=outbreak_report_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    # Return JSON by default
    return {
        "report_type": "outbreak_summary",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": days,
        "total_outbreaks": len(data),
        "total_patients": sum(d["total_patients"] for d in data),
        "data": data
    }


@router.get("/alert-summary")
async def generate_alert_summary_report(
    format: str = "json",
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Generate alert summary report"""
    
    sql = """
        SELECT 
            severity,
            zone_name,
            COUNT(*) as alert_count,
            sent_at
        FROM alerts
        WHERE sent_at >= :start_date
        GROUP BY severity, zone_name, sent_at
        ORDER BY sent_at DESC
    """
    
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    result = await db.execute(text(sql), {"start_date": start_date})
    rows = result.fetchall()
    
    data = []
    for row in rows:
        data.append({
            "severity": row[0],
            "zone_name": row[1],
            "alert_count": row[2],
            "sent_at": row[3]
        })
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["severity", "zone_name", "alert_count", "sent_at"])
        writer.writeheader()
        writer.writerows(data)
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=alert_report_{datetime.now().strftime('%Y%m%d')}.csv"}
        )
    
    return {
        "report_type": "alert_summary",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "period_days": days,
        "total_alerts": len(data),
        "data": data
    }


@router.get("/comprehensive")
async def generate_comprehensive_report(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
):
    """Generate comprehensive system report from doctor submissions"""
    
    try:
        from app.core.config import get_sqlite_db_path
        
        conn = sqlite3.connect(get_sqlite_db_path())
        cursor = conn.cursor()
        
        # Get outbreak stats from doctor_outbreaks (approved only)
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN severity = 'severe' THEN 1 ELSE 0 END) as severe,
                SUM(CASE WHEN severity = 'moderate' THEN 1 ELSE 0 END) as moderate,
                SUM(CASE WHEN severity = 'mild' THEN 1 ELSE 0 END) as mild,
                COALESCE(SUM(patient_count), 0) as total_patients,
                COUNT(DISTINCT location_name) as hospitals
            FROM doctor_outbreaks
            WHERE status = 'approved'
        ''')
        row = cursor.fetchone()
        
        total_outbreaks = row[0] if row else 0
        total_severe = row[1] if row else 0
        total_moderate = row[2] if row else 0
        total_mild = row[3] if row else 0
        total_patients = row[4] if row else 0
        total_hospitals = row[5] if row else 0
        
        # Get alert stats from doctor_alerts
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN alert_type = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN alert_type = 'warning' THEN 1 ELSE 0 END) as warning
            FROM doctor_alerts
            WHERE status = 'active'
        ''')
        alert_row = cursor.fetchone()
        
        total_alerts = alert_row[0] if alert_row else 0
        total_critical = alert_row[1] if alert_row else 0
        total_warning = alert_row[2] if alert_row else 0
        
        conn.close()
        
        return {
            "report_type": "comprehensive",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period_days": days,
            "summary": {
                "outbreaks": {
                    "total": total_outbreaks,
                    "severe": total_severe,
                    "moderate": total_moderate,
                    "mild": total_mild,
                    "total_patients": total_patients
                },
                "alerts": {
                    "total": total_alerts,
                    "critical": total_critical,
                    "warning": total_warning
                },
                "hospitals": {
                    "affected": total_hospitals
                }
            }
        }
    
    except Exception as e:
        # Return fallback empty report to prevent 500 errors
        print(f"Error generating comprehensive report: {e}")
        import traceback
        traceback.print_exc()
        return {
            "report_type": "comprehensive",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period_days": days,
            "summary": {
                "outbreaks": {"total": 0, "severe": 0, "moderate": 0, "mild": 0, "total_patients": 0},
                "alerts": {"total": 0, "critical": 0, "warning": 0},
                "hospitals": {"affected": 0}
            },
            "error": f"Report generation error: {str(e)}"
        }

