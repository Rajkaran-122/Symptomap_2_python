@echo off
echo [INFO] Setting up Flask OTP Auth System...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Create Virtual Environment
if not exist "venv_auth" (
    echo [INFO] Creating virtual environment 'venv_auth'...
    python -m venv venv_auth
)

:: Activate and Install
echo [INFO] Activating virtual environment...
call venv_auth\Scripts\activate

echo [INFO] Installing dependencies...
pip install -r requirements.txt

:: Initialize Database
if not exist "migrations" (
    echo [INFO] Initializing migrations...
    flask db init
)

echo [INFO] Generating and applying migrations...
flask db migrate -m "Initial Schema"
flask db upgrade

echo [INFO] Setup complete! You can now run 'run.bat' to start the server.
pause
