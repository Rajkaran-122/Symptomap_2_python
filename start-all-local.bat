@echo off
echo ===================================================
echo   SymptoMap Local Startup Script (No Docker)
echo ===================================================

echo.
echo [1/3] Starting ML Service...
start "SymptoMap ML Service" cmd /k "call run_ml_service.bat"

echo.
echo [2/3] Starting Backend (Mock DB Mode)...
cd backend
start "SymptoMap Backend" cmd /k "npm run dev"
cd ..

echo.
echo [3/3] Starting Frontend...
cd frontend
start "SymptoMap Frontend" cmd /k "npm run dev"
cd ..

echo.
echo ===================================================
echo   Services are starting in separate windows.
echo   Frontend: http://localhost:3000
echo   Backend:  http://localhost:8787
echo   ML API:   http://localhost:8000
echo ===================================================
echo.
echo NOTE: Since Docker is not running, the backend is using
echo       a MOCK DATABASE. Data will not be saved.
echo.
pause
