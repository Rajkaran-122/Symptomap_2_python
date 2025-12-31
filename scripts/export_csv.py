#!/usr/bin/env python3
"""
SymptoMap CSV Export Utility
Export all outbreak data from database to CSV file

Usage:
    python scripts/export_csv.py [output_file]
    python scripts/export_csv.py export/outbreaks_2025.csv

If no output file specified, creates timestamped file in export/ directory
"""

import csv
import sqlite3
import sys
import os
from datetime import datetime
from pathlib import Path

DATABASE_FILE = "symptomap.db"

def export_to_csv(output_file=None):
    """Export all outbreaks to CSV file"""
    
    # Check if database exists
    if not Path(DATABASE_FILE).exists():
        print(f"❌ ERROR: Database not found: {DATABASE_FILE}")
        return False
    
    # Generate default filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"export/outbreaks_{timestamp}.csv"
    
    # Create export directory if needed
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"📤 Exporting outbreaks to: {output_file}")
    print("")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        # Get all outbreaks
        cursor.execute("""
            SELECT 
                disease_type,
                patient_count,
                severity,
                latitude,
                longitude,
                location_name,
                city,
                state,
                country,
                description,
                date_reported,
                submitted_at,
                submitted_by,
                status
            FROM doctor_outbreaks
            ORDER BY submitted_at DESC
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("⚠️  No outbreaks found in database")
            conn.close()
            return False
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'disease_type', 'patient_count', 'severity',
                'latitude', 'longitude', 'location_name',
                'city', 'state', 'country', 'description',
                'date_reported', 'submitted_at', 'submitted_by', 'status'
            ])
            
            # Write data rows
            for row in rows:
                writer.writerow(row)
        
        conn.close()
        
        # Get file size
        file_size = output_path.stat().st_size
        file_size_kb = file_size / 1024
        
        # Summary
        print(f"✅ Export completed successfully!")
        print(f"   Records exported: {len(rows)}")
        print(f"   Output file: {output_file}")
        print(f"   File size: {file_size_kb:.2f} KB")
        print("")
        
        # Show statistics
        print("📊 Export Statistics:")
        
        # Count by disease type
        cursor = conn.cursor()
        cursor.execute("""
            SELECT disease_type, COUNT(*) as count
            FROM doctor_outbreaks
            GROUP BY disease_type
            ORDER BY count DESC
        """)
        
        disease_stats = cursor.fetchall()
        print("   By disease type:")
        for disease, count in disease_stats:
            print(f"     - {disease}: {count}")
        
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def print_usage():
    """Print usage instructions"""
    print("")
    print("Usage:")
    print("  python scripts/export_csv.py [output_file]")
    print("")
    print("Examples:")
    print("  python scripts/export_csv.py")
    print("  python scripts/export_csv.py export/my_export.csv")
    print("  python scripts/export_csv.py backups/outbreaks_$(date +%Y%m%d).csv")
    print("")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    success = export_to_csv(output_file)
    
    sys.exit(0 if success else 1)
