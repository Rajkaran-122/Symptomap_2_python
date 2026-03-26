"""
Public API endpoints for the User Dashboard.
Provides read-only, aggregated data from the live database.
"""

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, distinct, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_response
from app.core.database import get_db
from app.models.broadcast import Broadcast
from app.models.doctor import DoctorOutbreak
from app.models.outbreak import Outbreak, Hospital

router = APIRouter(prefix="/public", tags=["Public Data"])

SEVERITY_RANK = {
    "critical": 4,
    "severe": 3,
    "moderate": 2,
    "mild": 1,
}

RISK_ORDER = {
    "Critical": 4,
    "High": 3,
    "Moderate": 2,
    "Low": 1,
}


def _is_sqlite_session(db: AsyncSession) -> bool:
    try:
        bind = db.get_bind()
        return bind is not None and "sqlite" in str(bind.url)
    except Exception:
        return False


def _db_datetime(db: AsyncSession, value: datetime) -> datetime:
    """Normalize datetime for SQLite (naive) vs Postgres (aware)."""
    if _is_sqlite_session(db) and value.tzinfo is not None:
        return value.replace(tzinfo=None)
    return value


def _normalize_key(value: str) -> str:
    return value.strip().lower()


def _classify_hotspot(outbreak_count: int, case_count: int, max_rank: int) -> Tuple[str, str]:
    if max_rank >= 4 or case_count >= 600 or outbreak_count >= 80:
        return "Critical", "red"
    if max_rank >= 3 or case_count >= 300 or outbreak_count >= 40:
        return "High", "orange"
    if max_rank >= 2 or case_count >= 120 or outbreak_count >= 15:
        return "Moderate", "yellow"
    return "Low", "green"


@router.get("/stats")
@cache_response(ttl_seconds=60)
async def get_public_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get high-level public statistics from outbreaks + approved doctor submissions.
    """
    now = datetime.now(timezone.utc)
    this_week_start = _db_datetime(db, now - timedelta(days=7))
    last_week_start = _db_datetime(db, now - timedelta(days=14))

    orm_count_result = await db.execute(select(func.count(Outbreak.id)))
    orm_outbreak_count = int(orm_count_result.scalar() or 0)

    doc_count_result = await db.execute(
        select(func.count(DoctorOutbreak.id)).where(DoctorOutbreak.status == "approved")
    )
    doc_outbreak_count = int(doc_count_result.scalar() or 0)

    try:
        broadcast_count_result = await db.execute(
            select(func.count(Broadcast.id)).where(Broadcast.is_active == True)
        )
        active_broadcasts = int(broadcast_count_result.scalar() or 0)
    except Exception:
        broadcast_count_result = await db.execute(select(func.count(Broadcast.id)))
        active_broadcasts = int(broadcast_count_result.scalar() or 0)

    orm_cases_this_week_result = await db.execute(
        select(func.sum(Outbreak.patient_count)).where(Outbreak.date_reported >= this_week_start)
    )
    orm_cases_this_week = int(orm_cases_this_week_result.scalar() or 0)

    doc_cases_this_week_result = await db.execute(
        select(func.sum(DoctorOutbreak.patient_count)).where(
            DoctorOutbreak.status == "approved",
            DoctorOutbreak.date_reported >= this_week_start,
        )
    )
    doc_cases_this_week = int(doc_cases_this_week_result.scalar() or 0)
    cases_this_week = orm_cases_this_week + doc_cases_this_week

    orm_cases_last_week_result = await db.execute(
        select(func.sum(Outbreak.patient_count)).where(
            Outbreak.date_reported >= last_week_start,
            Outbreak.date_reported < this_week_start,
        )
    )
    orm_cases_last_week = int(orm_cases_last_week_result.scalar() or 0)

    doc_cases_last_week_result = await db.execute(
        select(func.sum(DoctorOutbreak.patient_count)).where(
            DoctorOutbreak.status == "approved",
            DoctorOutbreak.date_reported >= last_week_start,
            DoctorOutbreak.date_reported < this_week_start,
        )
    )
    doc_cases_last_week = int(doc_cases_last_week_result.scalar() or 0)
    cases_last_week = orm_cases_last_week + doc_cases_last_week

    if cases_last_week > 0:
        trend_percentage = round(((cases_this_week - cases_last_week) / cases_last_week) * 100, 1)
    elif cases_this_week > 0:
        trend_percentage = 100.0
    else:
        trend_percentage = 0.0

    orm_states_result = await db.execute(
        select(distinct(Hospital.state))
        .join(Outbreak, Hospital.id == Outbreak.hospital_id)
        .where(Hospital.state.is_not(None), Hospital.state != "")
    )
    doc_states_result = await db.execute(
        select(distinct(DoctorOutbreak.state)).where(
            DoctorOutbreak.status == "approved",
            DoctorOutbreak.state.is_not(None),
            DoctorOutbreak.state != "",
        )
    )

    regions = set()
    for row in orm_states_result.all():
        if row[0]:
            regions.add(_normalize_key(row[0]))
    for row in doc_states_result.all():
        if row[0]:
            regions.add(_normalize_key(row[0]))

    orm_sources_result = await db.execute(
        select(distinct(Hospital.name))
        .join(Outbreak, Hospital.id == Outbreak.hospital_id)
        .where(Hospital.name.is_not(None), Hospital.name != "")
    )
    doc_sources_result = await db.execute(
        select(distinct(DoctorOutbreak.location_name)).where(
            DoctorOutbreak.status == "approved",
            DoctorOutbreak.location_name.is_not(None),
            DoctorOutbreak.location_name != "",
        )
    )

    trusted_sources = set()
    for row in orm_sources_result.all():
        if row[0]:
            trusted_sources.add(_normalize_key(row[0]))
    for row in doc_sources_result.all():
        if row[0]:
            trusted_sources.add(_normalize_key(row[0]))

    return {
        "activeOutbreaks": orm_outbreak_count + doc_outbreak_count,
        "activeBroadcasts": active_broadcasts,
        "casesThisWeek": cases_this_week,
        "trendPercentage": trend_percentage,
        "regionsAffected": len(regions),
        "verifiedSources": len(trusted_sources),
    }


@router.get("/hotspots")
@cache_response(ttl_seconds=60)
async def get_public_hotspots(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get top hotspot cities using outbreaks + approved doctor submissions.
    """
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

    orm_result = await db.execute(
        select(
            Hospital.city.label("city"),
            func.count(Outbreak.id).label("outbreak_count"),
            func.sum(Outbreak.patient_count).label("case_count"),
            func.max(severity_rank_orm).label("max_severity_rank"),
        )
        .join(Outbreak, Hospital.id == Outbreak.hospital_id)
        .where(Hospital.city.is_not(None), Hospital.city != "")
        .group_by(Hospital.city)
    )

    doc_result = await db.execute(
        select(
            DoctorOutbreak.city.label("city"),
            func.count(DoctorOutbreak.id).label("outbreak_count"),
            func.sum(DoctorOutbreak.patient_count).label("case_count"),
            func.max(severity_rank_doc).label("max_severity_rank"),
        )
        .where(
            DoctorOutbreak.status == "approved",
            DoctorOutbreak.city.is_not(None),
            DoctorOutbreak.city != "",
        )
        .group_by(DoctorOutbreak.city)
    )

    city_stats: Dict[str, Dict[str, Any]] = {}

    for row in orm_result.all():
        city_name = str(row.city).strip()
        key = _normalize_key(city_name)
        city_stats[key] = {
            "city": city_name,
            "count": int(row.outbreak_count or 0),
            "cases": int(row.case_count or 0),
            "max_rank": int(row.max_severity_rank or 0),
        }

    for row in doc_result.all():
        city_name = str(row.city).strip()
        key = _normalize_key(city_name)
        if key not in city_stats:
            city_stats[key] = {"city": city_name, "count": 0, "cases": 0, "max_rank": 0}
        city_stats[key]["count"] += int(row.outbreak_count or 0)
        city_stats[key]["cases"] += int(row.case_count or 0)
        city_stats[key]["max_rank"] = max(city_stats[key]["max_rank"], int(row.max_severity_rank or 0))

    hotspots: List[Dict[str, Any]] = []
    for item in city_stats.values():
        risk, color = _classify_hotspot(item["count"], item["cases"], item["max_rank"])
        hotspots.append(
            {
                "city": item["city"],
                "risk": risk,
                "color": color,
                "count": item["count"],
                "cases": item["cases"],
            }
        )

    hotspots.sort(key=lambda h: (RISK_ORDER.get(h["risk"], 0), h["count"], h["cases"]), reverse=True)
    return hotspots[:5]


@router.get("/broadcasts")
@cache_response(ttl_seconds=120)
async def get_public_broadcasts(
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get active public broadcasts.
    """
    try:
        query = (
            select(Broadcast)
            .where(Broadcast.is_active == True)
            .order_by(Broadcast.created_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        broadcasts = result.scalars().all()

        return [
            {
                "id": str(b.id),
                "title": b.title,
                "message": b.message if hasattr(b, "message") else b.content,
                "severity": b.severity,
                "category": (
                    b.category
                    if hasattr(b, "category") and b.category
                    else b.severity.capitalize() if b.severity else "General"
                ),
                "created_at": b.created_at.isoformat() if b.created_at else None,
                "source": b.source if hasattr(b, "source") else "System",
            }
            for b in broadcasts
        ]
    except Exception as e:
        import traceback

        print(f"Error fetching broadcasts: {e}")
        print(traceback.format_exc())
        return []


@router.get("/grid-stats")
@cache_response(ttl_seconds=60)
async def get_grid_stats(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Get aggregated stats for the Live Surveillance Grid.
    Clusters are derived from hospitals + approved doctor submission locations.
    """
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

    orm_clusters_result = await db.execute(
        select(
            Hospital.name.label("cluster_name"),
            func.count(Outbreak.id).label("outbreak_count"),
            func.max(severity_rank_orm).label("max_severity_rank"),
        )
        .join(Outbreak, Hospital.id == Outbreak.hospital_id)
        .where(Hospital.name.is_not(None), Hospital.name != "")
        .group_by(Hospital.name)
    )

    doc_cluster_name = func.coalesce(
        DoctorOutbreak.location_name,
        DoctorOutbreak.city,
        DoctorOutbreak.state,
        "Unknown Location",
    )
    doc_clusters_result = await db.execute(
        select(
            doc_cluster_name.label("cluster_name"),
            func.count(DoctorOutbreak.id).label("outbreak_count"),
            func.max(severity_rank_doc).label("max_severity_rank"),
        )
        .where(DoctorOutbreak.status == "approved")
        .group_by(doc_cluster_name)
    )

    clusters: Dict[str, Dict[str, int]] = {}

    for row in orm_clusters_result.all():
        name = str(row.cluster_name).strip()
        key = _normalize_key(name)
        clusters[key] = {
            "count": int(row.outbreak_count or 0),
            "max_rank": int(row.max_severity_rank or 0),
        }

    for row in doc_clusters_result.all():
        name = str(row.cluster_name).strip()
        key = _normalize_key(name)
        if key not in clusters:
            clusters[key] = {"count": 0, "max_rank": 0}
        clusters[key]["count"] += int(row.outbreak_count or 0)
        clusters[key]["max_rank"] = max(clusters[key]["max_rank"], int(row.max_severity_rank or 0))

    severe_clusters = 0
    moderate_clusters = 0

    for cluster in clusters.values():
        count = cluster["count"]
        max_rank = cluster["max_rank"]
        if max_rank >= SEVERITY_RANK["severe"] or count >= 20:
            severe_clusters += 1
        elif max_rank >= SEVERITY_RANK["moderate"] or count >= 8:
            moderate_clusters += 1

    total_clusters = len(clusters)

    return {
        "visual_clusters": total_clusters,
        "active_zones": total_clusters,
        "risk_severe": severe_clusters,
        "risk_moderate": moderate_clusters,
        "classification": "patient density vectors",
    }

