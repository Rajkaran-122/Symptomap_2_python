"""Check actual alert data structure in database"""
import sqlite3

conn = sqlite3.connect("symptomap.db")
cursor = conn.cursor()

print("\n📋 ALERT TABLE STRUCTURE:\n")
cursor.execute("PRAGMA table_info(alerts)")
columns = cursor.fetchall()
for col in columns:
    print(f"  {col[1]:25} | {col[2]:15} | NOT NULL: {col[3]}")

print("\n📊 SAMPLE ALERT DATA:\n")
cursor.execute("SELECT * FROM alerts LIMIT 1")
row = cursor.fetchone()

if row:
    print("Columns and values:")
    for i, col in enumerate(columns):
        value = row[i]
        if isinstance(value, str) and len(value) > 100:
            value = value[:100] + "..."
        print(f"  {col[1]:25} = {value}")
else:
    print("  No alerts found in database")

cursor.execute("SELECT COUNT(*) FROM alerts")
count = cursor.fetchone()[0]
print(f"\n✅ Total alerts in database: {count}\n")

conn.close()
