"""
Export API - CSV export for outbreak data
"""

from fastapi import APIRouter
from fastapi.responses import Response
from datetime import datetime, timezone
import sqlite3
import os
import csv
from io import StringIO

router = APIRouter(prefix="/export", tags=["Export"])


def get_db_connection():
    """Get SQLite database connection"""
    from app.core.config import get_sqlite_db_path
    conn = sqlite3.connect(get_sqlite_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/csv/outbreaks")
async def export_outbreaks_csv():
    """
    Export approved outbreaks as CSV file
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id,
                disease_type,
                patient_count,
                severity,
                location_name,
                city,
                state,
                latitude,
                longitude,
                description,
                date_reported,
                status,
                created_at
            FROM doctor_outbreaks
            WHERE status = 'approved'
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Disease Type', 'Patient Count', 'Severity',
            'Location', 'City', 'State', 'Latitude', 'Longitude',
            'Description', 'Date Reported', 'Status', 'Created At'
        ])
        
        # Data
        for row in rows:
            writer.writerow([
                row['id'],
                row['disease_type'],
                row['patient_count'],
                row['severity'],
                row['location_name'],
                row['city'],
                row['state'],
                row['latitude'],
                row['longitude'],
                row['description'],
                row['date_reported'],
                row['status'],
                row['created_at']
            ])
        
        csv_content = output.getvalue()
        filename = f"symptomap_outbreaks_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        return Response(content=f"Error: {str(e)}", status_code=500)


@router.get("/csv/all")
async def export_all_csv():
    """
    Export all outbreaks (including pending) as CSV file
    Admin/authenticated use
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id,
                disease_type,
                patient_count,
                severity,
                location_name,
                city,
                state,
                latitude,
                longitude,
                description,
                date_reported,
                COALESCE(status, 'pending') as status,
                created_at
            FROM doctor_outbreaks
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'Disease Type', 'Patient Count', 'Severity',
            'Location', 'City', 'State', 'Latitude', 'Longitude',
            'Description', 'Date Reported', 'Status', 'Created At'
        ])
        
        # Data
        for row in rows:
            writer.writerow([
                row['id'],
                row['disease_type'],
                row['patient_count'],
                row['severity'],
                row['location_name'],
                row['city'],
                row['state'],
                row['latitude'],
                row['longitude'],
                row['description'],
                row['date_reported'],
                row['status'],
                row['created_at']
            ])
        
        csv_content = output.getvalue()
        filename = f"symptomap_all_outbreaks_{datetime.now().strftime('%Y%m%d')}.csv"
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        return Response(content=f"Error: {str(e)}", status_code=500)
