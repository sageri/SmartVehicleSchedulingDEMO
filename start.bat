@echo off
REM Demo startup script for AI Vehicle Routing System

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo Demo Startup Script
echo ========================================
echo.

REM ========================================
REM 1. Setup and start backend
REM ========================================
echo [1/4] Activating backend virtual environment...
if not exist "backend\venv" (
    echo Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

call backend\venv\Scripts\activate.bat
echo OK: Backend virtual environment activated

echo.
echo [2/4] Starting backend server on port 8000...
start "Backend Server" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo OK: Backend server started

REM ========================================
REM 2. Setup and start frontend
REM ========================================
echo.
echo [3/4] Starting frontend server on port 5173...
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"
echo OK: Frontend server started

REM ========================================
REM 3. Open demo page in browser
REM ========================================
echo.
echo [4/4] Opening demo page in browser...

REM Wait 3 seconds for servers to start
timeout /t 3 /nobreak

REM Open browser
start "" "http://localhost:5173"
echo OK: Demo page opened

echo.
echo ========================================
echo All services started successfully!
echo ========================================
echo.
echo Access points:
echo   Frontend: http://localhost:5173
echo   Backend API: http://localhost:8000/api/v1
echo   API Docs: http://localhost:8000/docs
echo.
echo To stop:
echo   Backend window: Ctrl+C
echo   Frontend window: Ctrl+C
echo.

pause
