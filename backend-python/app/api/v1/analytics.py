"""
Analytics API - Enhanced data endpoints for charts and trends
"""

from fastapi import APIRouter
from datetime import datetime, timezone, timedelta
import sqlite3
import os
from collections import defaultdict

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db_connection():
    """Get SQLite database connection"""
    from app.core.config import get_sqlite_db_path
    conn = sqlite3.connect(get_sqlite_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/activity-feed")
async def get_activity_feed():
    """
    Get recent activity for dashboard feed
    Shows latest outbreaks, approvals, and alerts
    """
    activities = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get recent outbreaks (last 10)
        cursor.execute('''
            SELECT id, disease_type, location_name, city, state, severity, status, created_at
            FROM doctor_outbreaks
            ORDER BY created_at DESC
            LIMIT 10
        ''')
        
        for row in cursor.fetchall():
            status = row['status'] or 'pending'
            if status == 'approved':
                action = "Outbreak approved"
                icon = "check"
                color = "green"
            elif status == 'rejected':
                action = "Outbreak rejected"
                icon = "x"
                color = "red"
            else:
                action = "New outbreak reported"
                icon = "alert"
                color = "yellow"
            
            activities.append({
                "id": f"outbreak_{row['id']}",
                "type": "outbreak",
                "action": action,
                "disease": row['disease_type'],
                "location": f"{row['location_name']}, {row['city']}" if row['city'] else row['location_name'],
                "severity": row['severity'],
                "status": status,
                "icon": icon,
                "color": color,
                "time": row['created_at']
            })
        
        # Get recent alerts
        cursor.execute('''
            SELECT id, alert_type, title, affected_area, status, created_at
            FROM doctor_alerts
            ORDER BY created_at DESC
            LIMIT 5
        ''')
        
        for row in cursor.fetchall():
            activities.append({
                "id": f"alert_{row['id']}",
                "type": "alert",
                "action": f"Alert: {row['title']}",
                "alert_type": row['alert_type'],
                "location": row['affected_area'],
                "status": row['status'],
                "icon": "bell",
                "color": "blue",
                "time": row['created_at']
            })
        
        conn.close()
        
        # Sort by time and limit
        activities.sort(key=lambda x: x['time'] or '', reverse=True)
        
    except Exception as e:
        print(f"Error fetching activity feed: {e}")
    
    return {
        "activities": activities[:15],
        "total": len(activities)
    }


@router.get("/trend-data")
async def get_trend_data():
    """
    Get outbreak trend data for line chart
    Groups by day for the last 30 days
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all outbreaks with dates
        cursor.execute('''
            SELECT date(date_reported) as date, COUNT(*) as count, SUM(patient_count) as cases
            FROM outbreaks
            WHERE date_reported IS NOT NULL
            GROUP BY date(date_reported)
            ORDER BY date DESC
            LIMIT 30
        ''')
        
        trends = []
        for row in cursor.fetchall():
            if row['date']:
                trends.append({
                    "date": row['date'],
                    "outbreaks": row['count'],
                    "cases": row['cases'] or 0
                })
        
        conn.close()
        
        # Reverse to show oldest first
        trends.reverse()
        
        return {
            "trend_data": trends,
            "period": "Last 30 days"
        }
    except Exception as e:
        return {"trend_data": [], "error": str(e)}


@router.get("/disease-distribution")
async def get_disease_distribution():
    """
    Get disease distribution for pie chart
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT disease_type, COUNT(*) as count, SUM(patient_count) as cases
            FROM outbreaks
            GROUP BY disease_type
            ORDER BY count DESC
        ''')
        
        distribution = []
        colors = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899']
        
        for i, row in enumerate(cursor.fetchall()):
            distribution.append({
                "name": row['disease_type'],
                "value": row['count'],
                "cases": row['cases'] or 0,
                "color": colors[i % len(colors)]
            })
        
        conn.close()
        
        return {"distribution": distribution}
    except Exception as e:
        return {"distribution": [], "error": str(e)}


@router.get("/severity-breakdown")
async def get_severity_breakdown():
    """
    Get severity breakdown for bar chart
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT severity, COUNT(*) as count, SUM(patient_count) as cases
            FROM outbreaks
            GROUP BY severity
        ''')
        
        severity_colors = {
            'severe': '#ef4444',
            'critical': '#dc2626',
            'moderate': '#f97316',
            'mild': '#22c55e'
        }
        
        breakdown = []
        for row in cursor.fetchall():
            breakdown.append({
                "severity": row['severity'],
                "outbreaks": row['count'],
                "cases": row['cases'] or 0,
                "color": severity_colors.get(row['severity'], '#6b7280')
            })
        
        conn.close()
        
        return {"breakdown": breakdown}
    except Exception as e:
        return {"breakdown": [], "error": str(e)}


@router.get("/regional-stats")
async def get_regional_stats():
    """
    Get regional statistics for map legend and comparison
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT state, COUNT(*) as outbreaks, SUM(patient_count) as cases,
                   COUNT(CASE WHEN severity = 'severe' THEN 1 END) as severe_count
            FROM outbreaks
            JOIN hospitals ON outbreaks.hospital_id = hospitals.id
            WHERE state IS NOT NULL
            GROUP BY state
            ORDER BY outbreaks DESC
        ''')
        
        regions = []
        for row in cursor.fetchall():
            # Calculate risk level
            severe_ratio = (row['severe_count'] or 0) / max(row['outbreaks'], 1)
            risk_level = 'high' if severe_ratio > 0.3 else 'medium' if severe_ratio > 0.1 else 'low'
            
            regions.append({
                "state": row['state'],
                "outbreaks": row['outbreaks'],
                "cases": row['cases'] or 0,
                "severe": row['severe_count'] or 0,
                "risk_level": risk_level
            })
        
        conn.close()
        
        return {"regions": regions}
    except Exception as e:
        return {"regions": [], "error": str(e)}


@router.get("/week-comparison")
async def get_week_comparison():
    """
    Compare this week vs last week stats
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        now = datetime.now(timezone.utc)
        this_week_start = (now - timedelta(days=7)).isoformat()
        last_week_start = (now - timedelta(days=14)).isoformat()
        last_week_end = (now - timedelta(days=7)).isoformat()
        
        # This week
        cursor.execute('''
            SELECT COUNT(*) as count, COALESCE(SUM(patient_count), 0) as cases
            FROM outbreaks
            WHERE date_reported >= ?
        ''', (this_week_start,))
        this_week = cursor.fetchone()
        
        # Last week
        cursor.execute('''
            SELECT COUNT(*) as count, COALESCE(SUM(patient_count), 0) as cases
            FROM outbreaks
            WHERE date_reported >= ? AND date_reported < ?
        ''', (last_week_start, last_week_end))
        last_week = cursor.fetchone()
        
        conn.close()
        
        # Calculate changes
        outbreak_change = this_week['count'] - last_week['count']
        case_change = this_week['cases'] - last_week['cases']
        
        return {
            "this_week": {
                "outbreaks": this_week['count'],
                "cases": this_week['cases']
            },
            "last_week": {
                "outbreaks": last_week['count'],
                "cases": last_week['cases']
            },
            "change": {
                "outbreaks": outbreak_change,
                "cases": case_change,
                "outbreak_percent": round(outbreak_change / max(last_week['count'], 1) * 100, 1),
                "case_percent": round(case_change / max(last_week['cases'], 1) * 100, 1)
            }
        }
    except Exception as e:
        return {"error": str(e)}
