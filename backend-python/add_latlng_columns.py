"""
Add latitude and longitude columns to existing tables
"""
import sqlite3

DB_PATH = "symptomap.db"

print("\n🔧 ADDING LAT/LNG COLUMNS TO DATABASE\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    # Add latitude and longitude to hospitals table
    print("Adding latitude column to hospitals...")
    cursor.execute("ALTER TABLE hospitals ADD COLUMN latitude REAL")
    print("✅ Added latitude to hospitals")
    
    print("Adding longitude column to hospitals...")
    cursor.execute("ALTER TABLE hospitals ADD COLUMN longitude REAL")
    print("✅ Added longitude to hospitals")
    
    # Add latitude and longitude to outbreaks table
    print("Adding latitude column to outbreaks...")
    cursor.execute("ALTER TABLE outbreaks ADD COLUMN latitude REAL")
    print("✅ Added latitude to outbreaks")
    
    print("Adding longitude column to outbreaks...")
    cursor.execute("ALTER TABLE outbreaks ADD COLUMN longitude REAL")
    print("✅ Added longitude to outbreaks")
    
    conn.commit()
    print("\n✅ Successfully added all columns!")
    print("\n" + "="*80)
    print("🎉 DATABASE SCHEMA UPDATED!")
    print("="*80)
    print("\nColumns added:")
    print("  - hospitals.latitude")
    print("  - hospitals.longitude")
    print("  - outbreaks.latitude")
    print("  - outbreaks.longitude")
    print("\n")
    
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print(f"\n✅ Columns already exist: {e}")
    else:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

finally:
    conn.close()

print("Ready to populate data with lat/lng values!\n")
