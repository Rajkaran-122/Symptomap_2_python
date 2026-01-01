import sqlite3
conn = sqlite3.connect('backend-python/symptomap.db')
c = conn.cursor()
c.execute("PRAGMA table_info(doctor_outbreaks)")
for row in c.fetchall():
    print(row)
conn.close()
