@echo off
REM ################################
REM SymptoMap Doctor Station
REM Quick Start Script (Windows)
REM ################################

title SymptoMap Doctor Station

echo ========================================
echo   SymptoMap Doctor Station Startup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or higher
    echo Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 16 or higher
    echo Download from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [INFO] System Check:
python --version
node --version
call npm --version
echo.

REM Create necessary directories
if not exist "backups" mkdir backups
if not exist "export" mkdir export
if not exist "logs" mkdir logs

REM Backend Setup
echo ========================================
echo   Starting Backend (FastAPI)
echo ========================================
echo.

cd backend-python

REM Create virtual environment if doesn't exist
if not exist "venv" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo [INFO] Installing Python dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

REM Start backend
echo [INFO] Starting FastAPI server on port 8000...
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

cd ..

REM Wait for backend
echo [INFO] Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Frontend Setup
echo.
echo ========================================
echo   Starting Frontend (React + Vite)
echo ========================================
echo.

cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo [INFO] Installing Node.js dependencies...
    call npm install --silent
)

REM Start frontend
echo [INFO] Starting React development server on port 3000...
start /B npm run dev

cd ..

REM Wait for frontend
echo [INFO] Waiting for frontend to initialize...
timeout /t 5 /nobreak >nul

REM Success message
echo.
echo ========================================
echo   SUCCESS! Doctor Station is Running
echo ========================================
echo.
echo   Access URLs:
echo   ============
echo   Doctor Portal:  http://localhost:3000/doctor
echo   Dashboard:      http://localhost:3000/dashboard
echo   API Docs:       http://localhost:8000/api/docs
echo.
echo   Credentials:
echo   ============
echo   Password: Doctor@SymptoMap2025
echo.
echo ========================================
echo.
echo [TIP] Keep this window open while using the application
echo [TIP] Press any key to stop all services and exit
echo.

pause >nul

REM Cleanup
echo.
echo [INFO] Stopping all services...

REM Kill all Python and Node processes (be careful!)
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo [INFO] All services stopped
echo.
echo Thank you for using SymptoMap!
echo.
pause
