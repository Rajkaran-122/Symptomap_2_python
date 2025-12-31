"""
Check alerts table schema  
"""
import sqlite3

conn = sqlite3.connect("symptomap.db")
cursor = conn.cursor()

print("\n📋 ALERTS TABLE SCHEMA:\n")
cursor.execute("PRAGMA table_info(alerts)")
for row in cursor.fetchall():
    print(f"  {row[1]:25} | {row[2]:15} | NOT NULL: {row[3]}")
    
print("\n📊 Current alerts count:")
cursor.execute("SELECT COUNT(*) FROM alerts")
print(f"  {cursor.fetchone()[0]} alerts\n")

conn.close()
