"""
Auto-Alert Generator Service
Analyzes predictions and generates alerts when thresholds are exceeded
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from app.models.outbreak import Outbreak, Hospital, Alert
from app.models.broadcast import Broadcast
from app.models.doctor import DoctorOutbreak
import uuid


# Alert thresholds
THRESHOLDS = {
    "CASES_CRITICAL": 500,   # > 500 cases = Critical
    "CASES_HIGH": 200,       # > 200 cases = High
    "GROWTH_RATE": 0.15,     # > 15% daily growth = Alert
}


SEVERITY_RANK = {
    "critical": 4,
    "severe": 3,
    "moderate": 2,
    "mild": 1,
}
RANK_TO_SEVERITY = {rank: severity for severity, rank in SEVERITY_RANK.items()}


def _pick_max_severity(a: Optional[str], b: Optional[str]) -> Optional[str]:
    if not a:
        return b
    if not b:
        return a
    return a if SEVERITY_RANK.get(a, 0) >= SEVERITY_RANK.get(b, 0) else b


async def _get_combined_state_stats(
    db: AsyncSession,
    start_ts: datetime,
    end_ts: Optional[datetime] = None,
) -> Dict[str, Dict[str, Optional[float]]]:
    """Aggregate outbreak stats by state from ORM outbreaks + approved doctor submissions."""
    combined: Dict[str, Dict[str, Optional[float]]] = {}
    severity_rank_orm = case(
        (func.lower(Outbreak.severity) == "critical", SEVERITY_RANK["critical"]),
        (func.lower(Outbreak.severity) == "severe", SEVERITY_RANK["severe"]),
        (func.lower(Outbreak.severity) == "moderate", SEVERITY_RANK["moderate"]),
        (func.lower(Outbreak.severity) == "mild", SEVERITY_RANK["mild"]),
        else_=0,
    )
    severity_rank_doc = case(
        (func.lower(DoctorOutbreak.severity) == "critical", SEVERITY_RANK["critical"]),
        (func.lower(DoctorOutbreak.severity) == "severe", SEVERITY_RANK["severe"]),
        (func.lower(DoctorOutbreak.severity) == "moderate", SEVERITY_RANK["moderate"]),
        (func.lower(DoctorOutbreak.severity) == "mild", SEVERITY_RANK["mild"]),
        else_=0,
    )

    # ORM outbreaks joined through hospitals
    orm_query = (
        select(
            Hospital.state,
            func.sum(Outbreak.patient_count).label("total_cases"),
            func.count(Outbreak.id).label("outbreak_count"),
            func.max(severity_rank_orm).label("max_severity_rank"),
        )
        .join(Hospital, Outbreak.hospital_id == Hospital.id)
        .where(Outbreak.date_reported >= start_ts)
    )
    if end_ts is not None:
        orm_query = orm_query.where(Outbreak.date_reported < end_ts)
    orm_query = orm_query.group_by(Hospital.state)

    orm_result = await db.execute(orm_query)
    for state, total_cases, outbreak_count, max_severity_rank in orm_result.all():
        if not state:
            continue
        combined[state] = {
            "total_cases": int(total_cases or 0),
            "outbreak_count": int(outbreak_count or 0),
            "max_severity": RANK_TO_SEVERITY.get(int(max_severity_rank or 0)),
        }

    # Approved doctor submissions
    doc_query = (
        select(
            DoctorOutbreak.state,
            func.sum(DoctorOutbreak.patient_count).label("total_cases"),
            func.count(DoctorOutbreak.id).label("outbreak_count"),
            func.max(severity_rank_doc).label("max_severity_rank"),
        )
        .where(
            DoctorOutbreak.status == "approved",
            DoctorOutbreak.date_reported >= start_ts,
        )
    )
    if end_ts is not None:
        doc_query = doc_query.where(DoctorOutbreak.date_reported < end_ts)
    doc_query = doc_query.group_by(DoctorOutbreak.state)

    doc_result = await db.execute(doc_query)
    for state, total_cases, outbreak_count, max_severity_rank in doc_result.all():
        if not state:
            continue
        if state not in combined:
            combined[state] = {
                "total_cases": 0,
                "outbreak_count": 0,
                "max_severity": None,
            }

        combined[state]["total_cases"] = int(combined[state]["total_cases"] or 0) + int(total_cases or 0)
        combined[state]["outbreak_count"] = int(combined[state]["outbreak_count"] or 0) + int(outbreak_count or 0)
        combined[state]["max_severity"] = _pick_max_severity(
            combined[state].get("max_severity"),
            RANK_TO_SEVERITY.get(int(max_severity_rank or 0)),
        )

    return combined


async def analyze_and_generate_alerts(db: AsyncSession) -> List[Dict]:
    """
    Analyze current outbreak data and predictions to auto-generate alerts
    Returns list of created alerts
    """
    created_alerts = []
    now = datetime.now(timezone.utc)
    
    # Get recent outbreaks grouped by state (ORM + approved doctor submissions)
    seven_days_ago = now - timedelta(days=7)
    state_stats = await _get_combined_state_stats(db, seven_days_ago)
    print(f"DEBUG: Found {len(state_stats)} states with outbreaks")
    for st, vals in state_stats.items():
        print(f"DEBUG: State: {st}, Cases: {vals.get('total_cases')}")

    for state, vals in state_stats.items():
        total_cases = int(vals.get("total_cases") or 0)
        outbreak_count = int(vals.get("outbreak_count") or 0)
        max_severity = vals.get("max_severity")
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
            
            # Create Alert
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

            # Create corresponding Broadcast for public feed
            broadcast = Broadcast(
                id=uuid.uuid4(),
                title=f"Public Alert: {state}",
                content=message,
                severity=severity_level,
                region=state,
                channels=["in_app", "web"],
                is_active=True,
                is_automated=True,
                created_at=now,
                created_by=None # Systems default
            )
            db.add(broadcast)

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
    
    this_week_stats = await _get_combined_state_stats(db, this_week_start)
    last_week_stats = await _get_combined_state_stats(db, last_week_start, this_week_start)

    this_week = {state: int(vals.get("total_cases") or 0) for state, vals in this_week_stats.items()}
    last_week = {state: int(vals.get("total_cases") or 0) for state, vals in last_week_stats.items()}
    
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
                    message=f"Outbreak cases in {state} grew by {growth_rate*100:.1f}% ({last_cases} -> {this_cases})",
                    alert_type="RAPID_GROWTH",
                    severity="warning" if growth_rate >= 0.25 else "info",
                    zone_name=state,
                    recipients={"auto_generated": True, "source": "prediction_engine"},
                    delivery_status={"growth_rate": round(growth_rate, 3)},
                    acknowledged_by=[]
                )
                db.add(alert)

                # Create corresponding Broadcast
                broadcast = Broadcast(
                    id=uuid.uuid4(),
                    title=f"Health Update: {state}",
                    content=f"Rising cases detected in {state}. Growth rate: {growth_rate*100:.1f}%. Please exercise caution.",
                    severity="warning" if growth_rate >= 0.25 else "info",
                    region=state,
                    channels=["in_app"],
                    is_active=True,
                    is_automated=True,
                    created_at=now
                )
                db.add(broadcast)

                created_alerts.append({
                    "state": state,
                    "type": "RAPID_GROWTH",
                    "growth_rate": f"{growth_rate*100:.1f}%"
                })
    
    await db.commit()
    return created_alerts


async def run_auto_alert_generation(db: AsyncSession) -> Dict:
    """Main function to run all alert generation checks"""
    print(">>> Running auto-alert generation...")
    
    outbreak_alerts = await analyze_and_generate_alerts(db)
    growth_alerts = await check_growth_rate_alerts(db)
    
    total = len(outbreak_alerts) + len(growth_alerts)
    print(f"[OK] Generated {total} new alerts")
    
    return {
        "outbreak_alerts": outbreak_alerts,
        "growth_alerts": growth_alerts,
        "total_generated": total
    }
