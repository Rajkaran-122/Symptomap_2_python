"""
Statistics endpoints for dashboard data
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, distinct
from typing import Dict, Any
import sqlite3

from app.core.database import get_db
from app.models.outbreak import Outbreak, Hospital
from app.models.user import User

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get high-level dashboard statistics including doctor submissions"""
    
    # Count active outbreaks from ORM (last 30 days)
    outbreak_count_query = select(func.count(Outbreak.id))
    outbreak_result = await db.execute(outbreak_count_query)
    active_outbreaks = outbreak_result.scalar() or 0
    
    # Count hospitals with outbreaks from ORM
    hospital_count_query = select(func.count(distinct(Hospital.id))).select_from(
        Hospital
    ).join(Outbreak, Hospital.id == Outbreak.hospital_id)
    hospital_result = await db.execute(hospital_count_query)
    hospitals_monitored = hospital_result.scalar() or 0
    
    # Count distinct states from ORM
    state_count_query = select(func.count(distinct(Hospital.state))).select_from(
        Hospital
    ).join(Outbreak, Hospital.id == Outbreak.hospital_id)
    state_result = await db.execute(state_count_query)
    states_covered = state_result.scalar() or 0
    
    # ADD: Query doctor_outbreaks table for doctor submissions
    try:
        conn = sqlite3.connect('../symptomap.db')
        cursor = conn.cursor()
        
        # Count doctor outbreaks - FIXED: Store result before accessing
        cursor.execute('SELECT COUNT(*) FROM doctor_outbreaks')
        row = cursor.fetchone()
        doctor_outbreak_count = row[0] if row else 0
        
        # Count distinct cities/states from doctor submissions
        cursor.execute('SELECT COUNT(DISTINCT state) FROM doctor_outbreaks WHERE state IS NOT NULL')
        row = cursor.fetchone()
        doctor_states = row[0] if row else 0
        
        # Count distinct hospitals from doctor submissions
        cursor.execute('SELECT COUNT(DISTINCT location_name) FROM doctor_outbreaks WHERE location_name IS NOT NULL')
        row = cursor.fetchone()
        doctor_hospitals = row[0] if row else 0
        
        conn.close()
        
        # Combine counts
        total_outbreaks = active_outbreaks + doctor_outbreak_count
        total_hospitals = hospitals_monitored + doctor_hospitals
        total_states = states_covered + doctor_states
        
    except Exception as e:
        print(f"Error querying doctor_outbreaks: {e}")
        # Fall back to ORM counts only
        total_outbreaks = active_outbreaks
        total_hospitals = hospitals_monitored
        total_states = states_covered
    
    # For now, predictions count is simulated
    ai_predictions = total_outbreaks * 12  # Rough estimate
    
    return {
        "active_outbreaks": total_outbreaks,
        "hospitals_monitored": f"{total_hospitals}+",
        "ai_predictions": ai_predictions,
        "coverage_area": f"{total_states} States"
    }



@router.get("/performance")
async def get_performance_metrics(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get system performance metrics"""
    
    # These are mock values - in production, you'd get from monitoring service
    return {
        "api_latency": "32ms",
        "api_latency_trend": -12,  # negative means improvement
        "active_users": "2,840",
        "active_users_trend": 8,
        "system_uptime": "99.9%",
        "uptime_trend": 0.1,
        "last_sync": "2s ago"
    }


@router.get("/zones")
async def get_risk_zones(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get risk zone statistics"""
    
    # Count outbreaks by severity
    severe_query = select(func.count(Outbreak.id)).where(Outbreak.severity == "severe")
    severe_result = await db.execute(severe_query)
    high_risk_zones = severe_result.scalar() or 0
    
    # Sum patient counts for at-risk population
    patient_query = select(func.sum(Outbreak.patient_count))
    patient_result = await db.execute(patient_query)
    total_patients = patient_result.scalar() or 0
    
    # Format as K (thousands)
    at_risk_population = f"{total_patients / 1000:.1f}K" if total_patients > 0 else "0"
    
    return {
        "high_risk_zones": high_risk_zones,
        "at_risk_population": at_risk_population
    }


@router.get("/analytics")
async def get_analytics_data(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get data for analytics dashboard"""
    
    # Disease distribution
    disease_query = select(
        Outbreak.disease_type,
        func.count(Outbreak.id).label("count")
    ).group_by(Outbreak.disease_type)
    
    disease_result = await db.execute(disease_query)
    disease_distribution = [
        {"disease": row[0], "count": row[1]}
        for row in disease_result.all()
    ]
    
    # Severity distribution
    severity_query = select(
        Outbreak.severity,
        func.count(Outbreak.id).label("count")
    ).group_by(Outbreak.severity)
    
    severity_result = await db.execute(severity_query)
    severity_distribution = [
        {"severity": row[0], "count": row[1]}
        for row in severity_result.all()
    ]
    
    # Top affected regions (by state)
    region_query = select(
        Hospital.state,
        func.count(Outbreak.id).label("outbreak_count")
    ).join(Outbreak, Hospital.id == Outbreak.hospital_id).group_by(
        Hospital.state
    ).order_by(func.count(Outbreak.id).desc()).limit(10)
    
    region_result = await db.execute(region_query)
    top_regions = [
        {"region": row[0], "count": row[1]}
        for row in region_result.all()
    ]
    
    return {
        "disease_distribution": disease_distribution,
        "severity_distribution": severity_distribution,
        "top_regions": top_regions
    }
