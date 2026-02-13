import os

log_file = "uvicorn_logs.txt"
if not os.path.exists(log_file):
    print(f"Log file not found: {log_file}")
    exit(1)

# Try different encodings
encodings = ['utf-16', 'utf-8', 'cp1252']
for enc in encodings:
    try:
        with open(log_file, 'r', encoding=enc) as f:
            lines = f.readlines()
            print(f"Successfully read with {enc}")
            for line in lines:
                if "DEBUG" in line:
                    print(line.strip())
                if "Database has" in line:
                    print(line.strip())
            break
    except Exception as e:
        print(f"Failed with {enc}: {e}")
