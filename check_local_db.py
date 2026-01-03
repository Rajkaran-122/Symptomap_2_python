import sqlite3
import os

# Check the local database
db_path = 'backend-python/symptomap.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check doctor_outbreaks (approved)
c.execute("SELECT COUNT(*) FROM doctor_outbreaks WHERE status='approved'")
approved = c.fetchone()[0]
print(f"doctor_outbreaks (approved): {approved}")

# Check doctor_outbreaks (all)
c.execute("SELECT COUNT(*) FROM doctor_outbreaks")
all_doctor = c.fetchone()[0]
print(f"doctor_outbreaks (all): {all_doctor}")

# Check outbreaks table
try:
    c.execute("SELECT COUNT(*) FROM outbreaks")
    outbreaks = c.fetchone()[0]
    print(f"outbreaks (ORM): {outbreaks}")
except Exception as e:
    print(f"outbreaks table error: {e}")

# Check severity distribution
c.execute("""
    SELECT severity, COUNT(*) 
    FROM doctor_outbreaks 
    WHERE status='approved' 
    GROUP BY severity
""")
print("\nSeverity distribution:")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Check total patients
c.execute("SELECT SUM(patient_count) FROM doctor_outbreaks WHERE status='approved'")
patients = c.fetchone()[0] or 0
print(f"\nTotal patients: {patients}")

conn.close()
