
import sqlite3
import os

# Connect to DB
db_path = os.path.join(os.path.dirname(__file__), 'backend-python', 'symptomap.db')
print(f"Connecting to: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check existing
    cursor.execute("SELECT count(*), status FROM doctor_outbreaks GROUP BY status")
    rows = cursor.fetchall()
    print("Current counts:", rows)

    # Approve all pending
    cursor.execute("UPDATE doctor_outbreaks SET status = 'approved' WHERE status = 'pending' OR status IS NULL")
    print(f"Updated pending to approved. Rows affected: {cursor.rowcount}")

    # If count is low, insert some dummy approved outbreaks
    cursor.execute("SELECT count(*) FROM doctor_outbreaks WHERE status = 'approved'")
    count = cursor.fetchone()[0]
    
    if count < 5:
        print("Inserting dummy approved outbreaks...")
        dummy_data = [
            ('Dengue', 15, 'moderate', 28.6139, 77.2090, 'Connaught Place', 'New Delhi', 'Delhi', 'High fever cases', '2024-01-15', 'approved'),
            ('COVID-19', 45, 'severe', 19.0760, 72.8777, 'General Hospital', 'Mumbai', 'Maharashtra', 'Cluster detected', '2024-01-16', 'approved'),
            ('Malaria', 8, 'mild', 13.0827, 80.2707, 'City Clinic', 'Chennai', 'Tamil Nadu', 'Seasonal spike', '2024-01-14', 'approved'),
            ('Typhoid', 12, 'moderate', 22.5726, 88.3639, 'Community Health Center', 'Kolkata', 'West Bengal', 'Water contamination', '2024-01-12', 'approved'),
            ('Flu', 25, 'mild', 12.9716, 77.5946, 'Tech Park Clinic', 'Bangalore', 'Karnataka', 'Seasonal flu', '2024-01-16', 'approved')
        ]
        
        cursor.executemany('''
            INSERT INTO doctor_outbreaks 
            (disease_type, patient_count, severity, latitude, longitude, location_name, city, state, description, date_reported, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', dummy_data)
        print(f"Inserted {len(dummy_data)} approved outbreaks.")
    
    conn.commit()
    conn.close()
    print("Done.")

except Exception as e:
    print(f"Error: {e}")
