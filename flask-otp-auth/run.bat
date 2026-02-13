@echo off
echo [INFO] Starting Flask OTP Auth Server...

if not exist "venv_auth" (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call venv_auth\Scripts\activate
flask run --port 5000 --reload
