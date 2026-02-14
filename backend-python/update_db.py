
import sqlite3
import os

db_path = "symptomap.db"

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    # Try looking in parent/current directory logic if needed, but assuming cwd is correct
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Checking if 'language' column exists...")
    cursor.execute("PRAGMA table_info(chatbot_conversations)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if "language" in columns:
        print("'language' column already exists.")
    else:
        print("Adding 'language' column...")
        cursor.execute("ALTER TABLE chatbot_conversations ADD COLUMN language VARCHAR(10) DEFAULT 'en'")
        conn.commit()
        print("Column added successfully.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
