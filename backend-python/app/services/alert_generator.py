"""
Auto-Alert Generator Service
Analyzes predictions and generates alerts when thresholds are exceeded
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.outbreak import Outbreak, Hospital, Alert


# Alert thresholds
THRESHOLDS = {
    "CASES_CRITICAL": 500,   # > 500 cases = Critical
    "CASES_HIGH": 200,       # > 200 cases = High
    "GROWTH_RATE": 0.15,     # > 15% daily growth = Alert
}


async def analyze_and_generate_alerts(db: AsyncSession) -> List[Dict]:
    """
    Analyze current outbreak data and predictions to auto-generate alerts
    Returns list of created alerts
    """
    created_alerts = []
    now = datetime.now(timezone.utc)
    
    # Get recent outbreaks grouped by state
    seven_days_ago = now - timedelta(days=7)
    
    # Aggregate by state
    result = await db.execute(
        select(
            Hospital.state,
            func.sum(Outbreak.patient_count).label("total_cases"),
            func.count(Outbreak.id).label("outbreak_count"),
            func.max(Outbreak.severity).label("max_severity")
        )
        .join(Hospital, Outbreak.hospital_id == Hospital.id)
        .where(Outbreak.date_reported >= seven_days_ago)
        .group_by(Hospital.state)
    )
    state_stats = result.all()
    
    for state, total_cases, outbreak_count, max_severity in state_stats:
        if not state:
            continue
            
        # Check thresholds
        alert_type = None
        severity_level = None
        message = None
        
        if total_cases >= THRESHOLDS["CASES_CRITICAL"]:
            alert_type = "CRITICAL_OUTBREAK"
            severity_level = "critical"
            message = f"Critical outbreak level in {state}: {total_cases} cases across {outbreak_count} hospitals in the past 7 days"
        elif total_cases >= THRESHOLDS["CASES_HIGH"]:
            alert_type = "HIGH_OUTBREAK"
            severity_level = "warning"
            message = f"High outbreak activity in {state}: {total_cases} cases from {outbreak_count} hospitals"
        elif max_severity in ["severe", "critical"]:
            alert_type = "SEVERE_CASE"
            severity_level = "warning"
            message = f"Severe cases detected in {state}: {total_cases} total cases, requires monitoring"
        
        if alert_type:
            # Check if similar alert exists in last 24 hours
            existing = await db.execute(
                select(Alert).where(
                    Alert.alert_type == alert_type,
                    Alert.zone_name == state,
                    Alert.sent_at >= now - timedelta(hours=24)
                ).limit(1)
            )
            if existing.scalar_one_or_none():
                continue  # Skip duplicate alert
            
            # Create alert matching existing model structure
            alert = Alert(
                title=f"{alert_type.replace('_', ' ').title()} - {state}",
                message=message,
                alert_type=alert_type,
                severity=severity_level,
                zone_name=state,
                recipients={"auto_generated": True, "source": "prediction_engine"},
                delivery_status={"status": "generated"},
                acknowledged_by=[]
            )
            db.add(alert)
            created_alerts.append({
                "state": state,
                "type": alert_type,
                "cases": total_cases,
                "severity": severity_level
            })
    
    await db.commit()
    return created_alerts


async def check_growth_rate_alerts(db: AsyncSession) -> List[Dict]:
    """Check for rapid growth rate and generate alerts"""
    created_alerts = []
    now = datetime.now(timezone.utc)
    
    # Compare this week vs last week by state
    this_week_start = now - timedelta(days=7)
    last_week_start = now - timedelta(days=14)
    
    # This week
    result = await db.execute(
        select(
            Hospital.state,
            func.sum(Outbreak.patient_count).label("cases")
        )
        .join(Hospital, Outbreak.hospital_id == Hospital.id)
        .where(Outbreak.date_reported >= this_week_start)
        .group_by(Hospital.state)
    )
    this_week = {row[0]: row[1] for row in result.all() if row[0]}
    
    # Last week
    result = await db.execute(
        select(
            Hospital.state,
            func.sum(Outbreak.patient_count).label("cases")
        )
        .join(Hospital, Outbreak.hospital_id == Hospital.id)
        .where(
            Outbreak.date_reported >= last_week_start,
            Outbreak.date_reported < this_week_start
        )
        .group_by(Hospital.state)
    )
    last_week = {row[0]: row[1] for row in result.all() if row[0]}
    
    for state, this_cases in this_week.items():
        last_cases = last_week.get(state, 0)
        if last_cases > 0:
            growth_rate = (this_cases - last_cases) / last_cases
            if growth_rate >= THRESHOLDS["GROWTH_RATE"]:
                # Check for existing alert
                existing = await db.execute(
                    select(Alert).where(
                        Alert.alert_type == "RAPID_GROWTH",
                        Alert.zone_name == state,
                        Alert.sent_at >= now - timedelta(hours=24)
                    ).limit(1)
                )
                if existing.scalar_one_or_none():
                    continue
                
                alert = Alert(
                    title=f"Rapid Growth Alert - {state}",
                    message=f"Outbreak cases in {state} grew by {growth_rate*100:.1f}% ({last_cases} → {this_cases})",
                    alert_type="RAPID_GROWTH",
                    severity="warning" if growth_rate >= 0.25 else "info",
                    zone_name=state,
                    recipients={"auto_generated": True, "source": "prediction_engine"},
                    delivery_status={"growth_rate": round(growth_rate, 3)},
                    acknowledged_by=[]
                )
                db.add(alert)
                created_alerts.append({
                    "state": state,
                    "type": "RAPID_GROWTH",
                    "growth_rate": f"{growth_rate*100:.1f}%"
                })
    
    await db.commit()
    return created_alerts


async def run_auto_alert_generation(db: AsyncSession) -> Dict:
    """Main function to run all alert generation checks"""
    print("🔔 Running auto-alert generation...")
    
    outbreak_alerts = await analyze_and_generate_alerts(db)
    growth_alerts = await check_growth_rate_alerts(db)
    
    total = len(outbreak_alerts) + len(growth_alerts)
    print(f"✅ Generated {total} new alerts")
    
    return {
        "outbreak_alerts": outbreak_alerts,
        "growth_alerts": growth_alerts,
        "total_generated": total
    }
