"""
Add 10 Jaipur hospitals with outbreak and alert data
"""
import sqlite3
from datetime import datetime, timezone, timedelta

# Connect to database
conn = sqlite3.connect('symptomap.db')
cursor = conn.cursor()

# Create alerts table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctor_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_type TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        affected_area TEXT,
        expiry_date TEXT,
        submitted_by TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'active'
    )
''')

print("✅ Ensured doctor_alerts table exists\n")

# Jaipur hospitals with coordinates
jaipur_hospitals = [
    {"name": "SMS Hospital", "lat": 26.9124, "lon": 75.7873},
    {"name": "Sawai Man Singh Medical College", "lat": 26.9157, "lon": 75.7854},
    {"name": "Fortis Escorts Hospital", "lat": 26.8854, "lon": 75.8017},
    {"name": "Eternal Heart Care Centre", "lat": 26.9260, "lon": 75.8235},
    {"name": "Narayana Multispeciality Hospital", "lat": 26.8467, "lon": 75.8056},
    {"name": "Manipal Hospital Jaipur", "lat": 26.9124, "lon": 75.7543},
    {"name": "Max Super Speciality Hospital", "lat": 26.8206, "lon": 75.8047},
    {"name": "Apex Hospital", "lat": 26.9226, "lon": 75.7820},
    {"name": "Ruban Memorial Hospital", "lat": 26.8969, "lon": 75.8069},
    {"name": "CK Birla Hospital", "lat": 26.9505, "lon": 75.7852}
]

# Disease data for outbreaks
diseases = [
    {"type": "Dengue", "count": 45, "severity": "moderate", "desc": "Seasonal dengue outbreak in monsoon"},
    {"type": "Malaria", "count": 23, "severity": "moderate", "desc": "Vector-borne disease cases increasing"},
    {"type": "Typhoid", "count": 18, "severity": "mild", "desc": "Water contamination reported"},
    {"type": "Influenza", "count": 56, "severity": "mild", "desc": "Seasonal flu affecting respiratory patients"},
    {"type": "COVID-19", "count": 12, "severity": "moderate", "desc": "New variant cases detected"},
    {"type": "Dengue", "count": 32, "severity": "severe", "desc": "Critical dengue cases reported"},
    {"type": "Chikungunya", "count": 28, "severity": "moderate", "desc": "Mosquito-borne illness outbreak"},
    {"type": "Gastroenteritis", "count": 41, "severity": "mild", "desc": "Food poisoning cases"},
    {"type": "Hepatitis A", "count": 15, "severity": "moderate", "desc": "Waterborne hepatitis outbreak"},
    {"type": "Tuberculosis", "count": 9, "severity": "severe", "desc": "Active TB cases under treatment"}
]

# Alert data
alerts = [
    {"type": "warning", "title": "Dengue Alert - Jaipur Region", "msg": "Increase in dengue cases. Take mosquito prevention measures."},
    {"type": "critical", "title": "Water Contamination Alert", "msg": "Boil water before drinking. Typhoid cases reported."},
    {"type": "info", "title": "Seasonal Flu Advisory", "msg": "Flu season active. Get vaccinated if eligible."},
    {"type": "warning", "title": "COVID-19 Variant Detected", "msg": "New variant cases found. Follow safety protocols."},
    {"type": "critical", "title": "High Dengue Risk Zones", "msg": "Multiple hospitals reporting dengue cases. Use mosquito repellent."},
    {"type": "info", "title": "Health Check-up Camp", "msg": "Free health screening available at government hospitals."},
    {"type": "warning", "title": "Monsoon Disease Alert", "msg": "Waterborne diseases expected. Maintain hygiene."},
    {"type": "critical", "title": "Immediate Action Required", "msg": "Chikungunya outbreak spreading. Seek medical attention for fever."},
    {"type": "info", "title": "Vaccination Drive", "msg": "Free vaccinations available for children and elderly."},
    {"type": "warning", "title": "Air Quality Alert", "msg": "Poor air quality affecting respiratory patients."}
]

print("🏥 Adding 10 Jaipur Hospitals with Outbreaks and Alerts...\n")

# Add outbreaks
for i, hospital in enumerate(jaipur_hospitals):
    disease = diseases[i]
    
    cursor.execute('''
        INSERT INTO doctor_outbreaks 
        (disease_type, patient_count, severity, latitude, longitude,
         location_name, city, state, description, date_reported, submitted_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        disease['type'],
        disease['count'],
        disease['severity'],
        hospital['lat'],
        hospital['lon'],
        hospital['name'],
        'Jaipur',
        'Rajasthan',
        disease['desc'],
        datetime.now(timezone.utc).isoformat(),
        'doctor',
        datetime.now(timezone.utc).isoformat()
    ))
    
    print(f"✓ Added {disease['type']} outbreak at {hospital['name']}")
    print(f"  Cases: {disease['count']} | Severity: {disease['severity']}")
    print()

# Add alerts
for i, hospital in enumerate(jaipur_hospitals):
    alert = alerts[i]
    expiry = datetime.now(timezone.utc) + timedelta(days=7)
    
    cursor.execute('''
        INSERT INTO doctor_alerts
        (alert_type, title, message, latitude, longitude, affected_area,
         expiry_date, submitted_by, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        alert['type'],
        alert['title'],
        alert['msg'],
        hospital['lat'],
        hospital['lon'],
        f"{hospital['name']}, Jaipur",
        expiry.isoformat(),
        'doctor',
        datetime.now(timezone.utc).isoformat(),
        'active'
    ))
    
    print(f"🚨 Added {alert['type'].upper()} alert for {hospital['name']}")
    print(f"  Title: {alert['title']}")
    print()

conn.commit()

# Verify data
cursor.execute('SELECT COUNT(*) FROM doctor_outbreaks WHERE city = "Jaipur"')
outbreak_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM doctor_alerts WHERE affected_area LIKE "%Jaipur%"')
alert_count = cursor.fetchone()[0]

print("=" * 60)
print(f"✅ Successfully added Jaipur hospital data!")
print(f"   Total Outbreaks in Jaipur: {outbreak_count}")
print(f"   Total Alerts in Jaipur: {alert_count}")
print("=" * 60)

# Show summary
print("\n📊 Jaipur Outbreak Summary:")
cursor.execute('''
    SELECT disease_type, COUNT(*) as count, SUM(patient_count) as total_cases
    FROM doctor_outbreaks 
    WHERE city = "Jaipur"
    GROUP BY disease_type
    ORDER BY total_cases DESC
''')

for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]} hospital(s), {row[2]} total cases")

print("\n🚨 Active Alerts:")
cursor.execute('''
    SELECT alert_type, title
    FROM doctor_alerts 
    WHERE affected_area LIKE "%Jaipur%" AND status = "active"
    ORDER BY alert_type
''')

for row in cursor.fetchall():
    print(f"   [{row[0].upper()}] {row[1]}")

conn.close()
print("\n✅ Database updated successfully!")
print("🌐 Refresh the dashboard to see all Jaipur hospital data!")
