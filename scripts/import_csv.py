#!/usr/bin/env python3
"""
SymptoMap CSV Import Utility
Import outbreak data from CSV file into database

Usage:
    python scripts/import_csv.py <csv_file>
    python scripts/import_csv.py data/sample_outbreaks.csv

CSV Format:
    disease_type,patient_count,severity,latitude,longitude,location_name,city,state,description,date_reported
    Dengue,45,moderate,26.9124,75.7873,SMS Hospital,Jaipur,Rajasthan,Seasonal outbreak,2025-01-15
"""

import csv
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DATABASE_FILE = "symptomap.db"

def validate_csv_headers(headers):
    """Validate CSV has required columns"""
    required = {
        'disease_type', 'patient_count', 'severity',
        'latitude', 'longitude', 'location_name',
        'city', 'state', 'date_reported'
    }
    
    missing = required - set(headers)
    
    if missing:
        print(f"❌ ERROR: Missing required columns: {', '.join(missing)}")
        return False
    
    return True

def validate_row(row, line_num):
    """Validate individual row data"""
    errors = []
    
    # Check required fields
    if not row.get('disease_type'):
        errors.append("disease_type is empty")
    
    # Validate patient_count
    try:
        count = int(row['patient_count'])
        if count <= 0:
            errors.append("patient_count must be positive")
    except ValueError:
        errors.append("patient_count must be a number")
    
    # Validate severity
    if row.get('severity') not in ['mild', 'moderate', 'severe']:
        errors.append("severity must be: mild, moderate, or severe")
    
    # Validate coordinates
    try:
        lat = float(row['latitude'])
        if not (-90 <= lat <= 90):
            errors.append("latitude must be between -90 and 90")
    except ValueError:
        errors.append("latitude must be a number")
    
    try:
        lon = float(row['longitude'])
        if not (-180 <= lon <= 180):
            errors.append("longitude must be between -180 and 180")
    except ValueError:
        errors.append("longitude must be a number")
    
    if errors:
        print(f"⚠️  Line {line_num}: {', '.join(errors)}")
        return False
    
    return True

def import_csv(csv_file, skip_invalid=True):
    """Import outbreaks from CSV file"""
    
    # Check if file exists
    if not Path(csv_file).exists():
        print(f"❌ ERROR: File not found: {csv_file}")
        return False
    
    # Check if database exists
    if not Path(DATABASE_FILE).exists():
        print(f"❌ ERROR: Database not found: {DATABASE_FILE}")
        print("Please start the application first to create the database.")
        return False
    
    print(f"📊 Importing from: {csv_file}")
    print("")
    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        
        imported_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate headers
            if not validate_csv_headers(reader.fieldnames):
                return False
            
            print(f"✅ CSV headers validated")
            print("")
            
            for line_num, row in enumerate(reader, start=2):  # Start at 2 (header is line 1)
                # Validate row
                if not validate_row(row, line_num):
                    skipped_count += 1
                    if not skip_invalid:
                        print("❌ Import aborted due to validation error")
                        conn.close()
                        return False
                    continue
                
                # Insert into database
                try:
                    cursor.execute("""
                        INSERT INTO doctor_outbreaks 
                        (disease_type, patient_count, severity, latitude, longitude,
                         location_name, city, state, description, date_reported,
                         submitted_by, submitted_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        row['disease_type'],
                        int(row['patient_count']),
                        row['severity'],
                        float(row['latitude']),
                        float(row['longitude']),
                        row['location_name'],
                        row['city'],
                        row['state'],
                        row.get('description', ''),
                        row['date_reported'],
                        'csv_import',
                        datetime.now().isoformat()
                    ))
                    
                    imported_count += 1
                    print(f"✓ Imported: {row['disease_type']} in {row['city']} ({row['patient_count']} cases)")
                    
                except sqlite3.Error as e:
                    print(f"❌ Database error on line {line_num}: {e}")
                    skipped_count += 1
                    if not skip_invalid:
                        conn.rollback()
                        conn.close()
                        return False
        
        # Commit all changes
        conn.commit()
        conn.close()
        
        # Summary
        print("")
        print("=" * 60)
        print(f"✅ Import completed successfully!")
        print(f"   Imported: {imported_count} outbreaks")
        if skipped_count > 0:
            print(f"   Skipped:  {skipped_count} rows (validation errors)")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def print_usage():
    """Print usage instructions"""
    print("")
    print("Usage:")
    print("  python scripts/import_csv.py <csv_file>")
    print("")
    print("Example:")
    print("  python scripts/import_csv.py data/sample_outbreaks.csv")
    print("")
    print("CSV Format:")
    print("  disease_type,patient_count,severity,latitude,longitude,")
    print("  location_name,city,state,description,date_reported")
    print("")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ ERROR: No CSV file specified")
        print_usage()
        sys.exit(1)
    
    csv_file = sys.argv[1]
    success = import_csv(csv_file)
    
    sys.exit(0 if success else 1)
