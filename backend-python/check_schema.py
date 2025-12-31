"""
Check SQLite database schema
"""
import sqlite3

DB_PATH = "symptomap.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("\n📊 DATABASE SCHEMA CHECK\n")

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}\n")

# Check users table schema
print("USERS TABLE COLUMNS:")
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")

# Check outbreaks count
cursor.execute("SELECT COUNT(*) FROM outbreaks")
count = cursor.fetchone()[0]
print(f"\nCurrent outbreaks count: {count}")

# Check hospitals count  
cursor.execute("SELECT COUNT(*) FROM hospitals")
h_count = cursor.fetchone()[0]
print(f"Current hospitals count: {h_count}")

conn.close()
