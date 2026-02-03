"""Inspect database schema"""
import sqlite3

conn = sqlite3.connect('symptomap.db')
cursor = conn.cursor()

print("=" * 60)
print("DATABASE SCHEMA INSPECTION")
print("=" * 60)

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cursor.fetchall()]
print(f"\nTables: {tables}")

# Get schema for each relevant table
for table in ['outbreaks', 'alerts', 'hospitals', 'users', 'doctor_outbreaks']:
    if table in tables:
        print(f"\n{table.upper()} SCHEMA:")
        print("-" * 40)
        cursor.execute(f"PRAGMA table_info({table})")
        for col in cursor.fetchall():
            print(f"  {col[1]:25} {col[2]:15} {'NOT NULL' if col[3] else ''}")
        
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  Total rows: {count}")
    else:
        print(f"\n{table.upper()}: Table does not exist")

conn.close()
